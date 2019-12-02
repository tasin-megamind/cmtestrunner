import csv
import json
import re
import random
import string
import yaml
from django.conf import settings
from django.core import mail
import os
from django.db import connection
from io import StringIO
from django.core.management import call_command
from django.apps import apps
from rest_framework.test import APIClient
from types import SimpleNamespace as Namespace

reset_seq_query = ''
all_models = []

def get_random_string(size):
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    return ''.join(random.choice(chars) for _ in range(size))

def add_str_to_each_list_element(str, list_, where='before'):
    if where != 'before':
        new_list = [x + str for x in list_]
    else:
        new_list = [str + x for x in list_]

    return new_list


def get_int_value_if_available(value):
    try:
        match = re.match(r'int\(([0-9]+)\)', str(value))
    except Exception as e:
        return 'lib error: ' + str(e)
    if match is not None:
        return int(match[1])
    else:
        return value

def set_reset_seq_query():
    global reset_seq_query
    commands = StringIO()

    for app in apps.get_app_configs():
        label = app.label
        call_command('sqlsequencereset', '--no-color', label, stdout=commands)

    reset_seq_query = commands.getvalue()

def set_all_models():
    global all_models
    for app in settings.TEST_APPS:
        for model in apps.get_app_config(app).get_models():
            all_models.append(model)



def parse_list_string(list_string):
    list_string_ = list_string.strip()
    try:
        int(list_string_)
        return list_string_
    except Exception as e:
        special_str = '&!$%'
        try:
            list_string_ = list_string_.replace("\\'", special_str)
            list_string_ = list_string_.replace("'", '"')
            list_string_ = list_string_.replace(special_str, "'")
            return json.loads(list_string_)
        except Exception as e:
            return list_string


def request_response_formatter(file):
    with open(settings.TEST_DATA_PATH + file, 'r') as test_file:
        test_data = csv.reader(test_file, delimiter=',', quotechar='"')
        header = next(test_data)
        all_req_resp = []

        for row in test_data:
            req = {}
            resp = {}
            for index, each_header in enumerate(header):
                if row[index] != 'N/A':
                    if each_header[:5] == 'resp_':
                        jsonFile = re.match(r'snapshot\((.*\.json)\)',
                                            row[index])
                        if jsonFile:
                            filename = jsonFile[1]
                            with open(settings.TEST_DATA_PATH + 'snapshots/' +
                                      filename) as f:
                                snapshot_data = json.load(f)
                                resp[each_header[5:]] = snapshot_data
                        else:
                            if re.match(r'string\((.*)\)', row[index]):
                                resp[each_header[5:]] = re.match(
                                    r'string\((.*)\)', row[index])[1]
                            else:
                                resp[each_header[5:]] = parse_list_string(
                                    row[index])
                    else:
                        if re.match(r'string\((.*)\)', row[index]):
                            req[each_header] = re.match(
                                r'string\((.*)\)', row[index])[1]
                        else:
                            req[each_header] = parse_list_string(row[index])

            result = {'req': req, 'resp': resp}
            all_req_resp.append(result)

    return all_req_resp

def get_all_locales():
    locales_dir = settings.LOCALE_PATHS[0]
    all_locales = os.listdir(locales_dir)
    return all_locales

def reset_db():
    for model in all_models:
        model.objects.all().delete()
    cursor = connection.cursor()
    cursor.execute(reset_seq_query)

def get_translations(file):
    with open(
            settings.TEST_PAYLOAD_PATH + 'translation/' + file + '.yml',
            'r',
            encoding='utf8') as fp:
        translations = yaml.load(fp)
    return translations

BOOL = {
    'true': True,
    'True': True,
    'false': False,
    'False': False,
    'None': False,
    'none': False
}

def set_auth_header(client, auth_token):
    existing_headers = client._credentials
    existing_headers['HTTP_AUTHORIZATION'] = 'token ' + auth_token
    client.credentials(**existing_headers)

def reset_auth_header(client):
    existing_headers = client._credentials
    if existing_headers.get('HTTP_AUTHORIZATION'):
        existing_headers.pop('HTTP_AUTHORIZATION')
    client.credentials(**existing_headers)

def set_lang_header(client, lang):
    existing_headers = client._credentials
    existing_headers['HTTP_ACCEPT_LANGUAGE'] = lang
    client.credentials(**existing_headers)

def format_response(response_obj):
    try:
        response = json.loads(response_obj.content)
    except Exception as e:
        response = {}
    if type(response) is list:
        response = {'content': response}

    response['status_code'] = response_obj.status_code
    return response

def process_request_response(**kwargs):
    processor = getattr(kwargs['client'], kwargs['method'])
    response = processor(
        kwargs['url'],
        kwargs.get('data', None),
        format=kwargs.get('format', 'json'))
    return format_response(response)

def unit_test_formatter(file_name):
    with open(settings.TEST_DATA_PATH + 'unittest/' + file_name, 'r')\
            as test_file:
        test_data = csv.reader(test_file, delimiter=',', quotechar='"')
        header = next(test_data)

        all_test_data = []
        args_idx = []
        kwargs_idx = []
        inits_idx = []
        returns_idx = None

        for index, each_header in enumerate(header):
            if each_header[:7] == 'kwargs_':
                kwargs_idx.append(index)
            elif each_header[:5] == 'init_':
                inits_idx.append(index)
            elif each_header == 'returns':
                returns_idx = index
            else:
                args_idx.append(index)

        for each_row in test_data:
            inits = []
            args = []
            kwargs = {}
            returns = ''

            for init_idx in inits_idx:
                inits.append(get_int_value_if_available(each_row[init_idx]))

            for arg_idx in args_idx:
                args.append(get_int_value_if_available(each_row[arg_idx]))

            for kwarg_idx in kwargs_idx:
                kwargs[header[kwarg_idx][7:]] = get_int_value_if_available(
                    each_row[kwarg_idx])

            returns = get_int_value_if_available(each_row[returns_idx])

            all_test_data.append({
                'inits': inits,
                'args': args,
                'kwargs': kwargs,
                'returns': returns
            })

        return all_test_data

def dict_to_obj(resp):
    try:
        if type(resp) is dict:
            resp = json.dumps(resp)
        else:
            resp = str(resp, 'UTF-8')
        return json.loads(resp, object_hook=lambda d: Namespace(**d))
    except Exception as e:
        return json.loads(
            json.dumps({
                'error': resp
            }), object_hook=lambda d: Namespace(**d))

def get_test_endpoints(file):
    with open(settings.TEST_PAYLOAD_PATH + file, 'r') as fp:
        endpoints = yaml.load(fp)
    endpoints = dict_to_obj(endpoints)
    return endpoints
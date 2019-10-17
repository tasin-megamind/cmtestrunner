import csv
import json
import re
import random
import string
from yaml import Loader, load
from django.conf import settings
from django.core import mail
import os
from django.db import connection
from io import StringIO
from django.core.management import call_command
from django.apps import apps
from types import SimpleNamespace as Namespace
import random
import numpy as np

reset_seq_query = ''
all_models = []


class CustomDict(dict):

    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value



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
    except Exception:
        special_str = '&!$%^*&@~`'
        try:
            list_string_ = list_string_.replace("\\'", special_str)
            list_string_ = list_string_.replace("'", '"')
            list_string_ = list_string_.replace(special_str, "'")
            return json.loads(list_string_)
        except Exception as e:
            return list_string


def simplify_data(data):
    if data == 'N/A':
        return False
    if re.match(r'string\((.*)\)', data):
        return re.match(r'string\((.*)\)', data)[1]
    elif re.match(r'random\((.*, [0-9]+)\)', data):
        matched = re.match(r'random\((.*), ([0-9]+)\)', data)
        random_str = random.choice(matched[1]) * int(matched[2])
        return random_str
    elif re.match(r'integer\(([0-9]+)\)', data):
        return int(re.match(r'integer\(([0-9]+)\)', data)[1])
    elif re.match(r'bool\((.*)\)', data):
        return BOOL.get(re.match(r'bool\((.*)\)', data)[1])
    else:
        return parse_list_string(data)


def request_response_formatter(file):
    with open(settings.TEST_DATA_PATH + file, 'r') as test_file:
        test_data = csv.reader(test_file, delimiter=',', quotechar='"')
        header = next(test_data)
        all_req_resp = []

        for row in test_data:
            req = {}
            resp = {}
            headers = {}

            for index, each_header in enumerate(header):
                simplified_data = simplify_data(row[index])
                if simplified_data:
                    if each_header[:5] == 'resp_':
                        resp[each_header[5:]] = simplified_data
                    elif each_header[:7] == 'header_':
                        headers[each_header[7:]] = simplified_data
                    else:
                        parsed_obj = parse_snapshot(simplified_data)
                        if type(parsed_obj) is dict:
                            req.update(parsed_obj)
                        else:
                            req[each_header] = simplified_data

            result = {'req': req, 'resp': resp, 'headers': headers}
            all_req_resp.append(result)

    return all_req_resp

def get_all_locales():
    all_locales = []
    locales_dir = settings.LOCALE_DIR
    if os.path.isdir(locales_dir):
        all_locales += os.listdir(locales_dir)
    return all_locales

def reset_db(*arg):
    for model in all_models:
        model.objects.all().delete()
    cursor = connection.cursor()
    cursor.execute(reset_seq_query)

def get_translations(file):
    with open(
            settings.TEST_PAYLOAD_PATH + 'translation/' + file + '.yml',
            'r',
            encoding='utf8') as fp:
        translations = load(fp, Loader)
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
    existing_headers = client.headers
    existing_headers['Authorization'] = 'token ' + auth_token
    client.headers.update(existing_headers)

def reset_auth_header(client):
    existing_headers = client.headers
    if existing_headers.get('Authorization'):
        existing_headers.pop('Authorization')
    client.headers.update(existing_headers)

def set_lang_header(client, lang):
    existing_headers = client.headers
    existing_headers['Accept-Language'] = lang
    client.headers.update(existing_headers)

def set_custom_headers(client, headers):
    existing_headers = client.headers
    existing_headers = {**existing_headers, **headers}
    client.headers.update(existing_headers)


def format_response(response_obj):
    try:
        response = json.loads(response_obj.content)
    except Exception:
        response = {}
    if type(response) is list:
        response = {'content': response}

    response['status_code'] = response_obj.status_code
    return response

def process_request_response(**kwargs):
    content_type = kwargs.get('format', 'application/json')
    client = kwargs.get('client')
    client.headers.update({'Content-Type': content_type})
    if settings.TEST_SERVER == 'testserver':
        data = kwargs.get('data', None)
    else:
        data = json.dumps(kwargs.get('data', None))
    processor = getattr(client, kwargs['method'])
    response = processor(
        kwargs['url'],
        data=data,
        )
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
        return json.loads(resp, object_hook=lambda d: CustomDict(d))
    except Exception as e:
        return json.loads(
            json.dumps({
                'error': resp
            }), object_hook=lambda d: CustomDict(d))

def get_test_endpoints(file):
    with open(settings.TEST_PAYLOAD_PATH + file, 'r') as fp:
        endpoints = load(fp, Loader)

    for k, v in endpoints.items():
        endpoints[k] = settings.TEST_SERVER + v
    endpoints = dict_to_obj(endpoints)
    return endpoints

fail_log = []
reproduce_object = []
exceptions = []


def generate_failed_test_report(**kwargs):
    # kwargs = dict_to_obj(kwargs)
    report_ = [
                kwargs.get('test_name'), kwargs.get('test_id'), 
                kwargs.get('priority'), kwargs.get('purpose'), 
                kwargs.get('reproduce_steps')
            ]
    report = {
        'test_id': kwargs.get('test_id'),
        'test': kwargs.get('purpose'),
        'reproduce_steps': kwargs.get('reproduce_steps'),
        'request_body': json.dumps(kwargs.get('request_body'), indent=4, sort_keys=False, ensure_ascii=False),
        'request_header': json.dumps(kwargs.get('request_header'), indent=4, sort_keys=False, ensure_ascii=False),
        'response': json.dumps(kwargs.get('response'), indent=4, sort_keys=False, ensure_ascii=False),
        'expected_response': json.dumps(kwargs.get('expected_response'), indent=4, sort_keys=False, ensure_ascii=False),
        'error_info': kwargs.get('error_info'),
    }
    fail_log.append(report_)
    reproduce_object.append(report)

def generate_analytics(fail_log):
    if not fail_log:
        return []
    fail_log = np.array(fail_log)
    priorities, counts = np.unique(fail_log[:, 2], return_counts=True)
    # priorities = [str(x) for x in priorities]
    prior_count = list(zip(counts, priorities))
    # return [' '.join(x) for x in prior_count]
    return prior_count



def parse_snapshot(snapshot, actual=None):
    matched = re.match(r'snapshot\((.*\.json)\)((\.)(.*))?', str(snapshot))
    if matched:
        snapshot_file = matched[1]
        
        if os.path.isfile(
            settings.TEST_DATA_PATH + 'snapshots/' + snapshot_file):
            f = open(settings.TEST_DATA_PATH + 'snapshots/' +
                                snapshot_file, 'r')

            if matched[4]:
                keys = matched[4].split('=')[0].split('.')
                value = simplify_data(matched[4].split('=')[1])
                temp = [json.load(f)]
                for index, key in enumerate(keys):
                    temp.append(temp[index].get(key))
                temp[-1] = parse_list_string(value)
                count = len(temp) - 1
                while(count):
                    temp[count-1][next(iter(temp[count-1]))] = temp[count]
                    count-=1
                return temp[0]
            else:
                try:
                    return json.load(f)
                except Exception:
                    return False
        else:
            f = open(settings.TEST_DATA_PATH + 'snapshots/' +
                                snapshot_file, 'w', encoding='utf-8')
            if actual:
                json.dump(actual, f, ensure_ascii=False, indent=4)
                return actual


        

    return snapshot



# def process_snapshot(expected, actual):

#     parsed_object = parse_snapshot(expected)
#     if not matched_obj:
#         f = open(settings.TEST_DATA_PATH + 'snapshots/' +
#                                 matched_obj[1], 'w')
#         json.dump(actual, f, indent=4)

#         return actual
    
#     return parsed_object

    # if re.match(r'snapshot\((.*\.json)\)', expected):
    #     snapshot_file = re.match(r'snapshot\((.*\.json)\)', expected)[1]
    #     if not os.path.isfile(
    #         settings.TEST_DATA_PATH + 'snapshots/' + snapshot_file):
    #         f = open(settings.TEST_DATA_PATH + 'snapshots/' +
    #                             snapshot_file, 'w')
    #         json.dump(actual, f, indent=4)
    #         return actual
            
    #     else:
    #         with open(settings.TEST_DATA_PATH + 'snapshots/' +
    #                     snapshot_file, 'r') as f:
    #             return json.load(f)
    
    # return expected
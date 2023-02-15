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
import requests
import copy
import time
import io
from .json_traverser import JsonTraverser

class Constants():
    RESET_SEQ_QUERY = ''
    MODELS = []
    FAIL_LOG = []
    FAILED_TESTS = {}
    EXCEPTIONS = []
    PASSED_TESTS = {}
    PASSED_LOG = []


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
    # global reset_seq_query
    commands = StringIO()

    for app in apps.get_app_configs():
        label = app.label
        call_command('sqlsequencereset', '--no-color', label, stdout=commands)

    Constants.RESET_SEQ_QUERY = commands.getvalue()

def set_all_models():
    # global all_models
    for app in settings.TEST_APPS:
        for model in apps.get_app_config(app).get_models():
            Constants.MODELS.append(model)



def parse_list_string(list_string):
    list_string_ = list_string.strip()
    try:
        float(list_string_)
        return list_string_
    except Exception:
        special_str = '&!$%^*&@~`'
        try:
            list_string_ = list_string_.replace("\\'", special_str)
            list_string_ = list_string_.replace("'", '"')
            list_string_ = list_string_.replace(special_str, "'")
            return json.loads(list_string_)
        except Exception:
            return list_string






def simplify_data(data):
    if data == 'N/A':
        return None

    if re.match(r'random\((.*, [0-9]+)\)', data):
        matched = re.match(r'random\((.*), ([0-9]+)\)', data)
        random_str = ''.join(random.choice(matched[1]) for _ in range(int(matched[2])))
        return random_str
    elif re.match(r'integer\(([0-9]+)\)', data):
        return int(re.match(r'integer\(([0-9]+)\)', data)[1])
    elif re.match(r'float\(([0-9]+\.)\)', data):
        return float(re.match(r'float\(([0-9]+\.)\)', data)[1])
    elif re.match(r'bool\((.*)\)', data):
        return BOOL.get(re.match(r'bool\((.*)\)', data)[1])
    elif re.match(r'attachment\((.*)\)', data):
        attachment_file = re.match('attachment\((.*)\)', data)[1]
        return open(settings.TEST_DATA_PATH + '/upload/' + attachment_file, 'rb')

    else:
        return parse_list_string(data)



def request_response_formatter(file):
    with open(settings.TEST_DATA_PATH + '/' + file, 'r') as test_file:
        test_data = csv.reader(test_file, delimiter=',', quotechar='"')
        header = next(test_data)
        all_req_resp = []

        for row in test_data:
            req = {'files': {}}
            resp = {}
            headers = {}

            for index, each_header in enumerate(header):
                simplified_data = simplify_data(row[index])
                parsed_obj = parse_snapshot(simplified_data)
                if simplified_data is not None:
                    if each_header[:5] == 'resp_':
                        resp[each_header[5:]] = simplified_data
                    elif each_header[:7] == 'header_':
                        if each_header[7:] == 'headers' and type(parsed_obj) is dict:
                            headers.update(parsed_obj)
                        else:
                            headers[each_header[7:]] = parsed_obj
                    elif isinstance(parsed_obj, io.IOBase):
                        files = req.get('files')
                        files.update({
                            each_header: parsed_obj
                        })
                        req['files'] = files
                    else:
                        if type(parsed_obj) is dict and each_header == 'request_body':
                            req.update(parsed_obj)
                        else:
                            req[each_header] = parsed_obj
            

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
    for model in Constants.MODELS:
        model.objects.all().delete()
    cursor = connection.cursor()
    cursor.execute(Constants.RESET_SEQ_QUERY)

def get_translations(file):
    with open(
            settings.TEST_PAYLOAD_PATH + '/translation/' + file + '.yml',
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

def get_data_from_yml(file):
    with open(settings.TEST_DATA_PATH + '/yml/' + file, encoding='utf8') as fp:
        data = load(fp,Loader)
    return data


def set_auth_header(client, auth_token):
    existing_headers = client.headers
    existing_headers['Authorization'] = auth_token
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
        response = response_obj.content
    if type(response) is not dict:
        response = {'content': response}

    response['status_code'] = str(response_obj.status_code)
    response['headers'] = dict(response_obj.headers)
    return response

def process_request_response(**kwargs):
    files = None
    client = kwargs.get('client')
    
    if kwargs.get('data'):
        files = kwargs.get('data').pop('files')

    data = kwargs.get('data', {})

    processor = getattr(client, kwargs['method'])
    if files:
        response = processor(
            kwargs['url'],
            data=data,
            files=files
            )
    else:
        response = processor(
            kwargs['url'],
            json=data,
            verify=False
            )
    
    for k,v in files.items():
        data[k] = str(v)
    response_time = response.elapsed.total_seconds() * 1000
    response = format_response(response)
    response['response_time'] = float("%0.2f"%(response_time))
    return response

def unit_test_formatter(file_name):
    with open(settings.TEST_DATA_PATH + '/unittest/' + file_name, 'r')\
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
    with open(settings.TEST_PAYLOAD_PATH + '/' + file, 'r') as fp:
        endpoints = load(fp, Loader)

    for k, v in endpoints.items():
        endpoints[k] = settings.TEST_SERVER + v
    endpoints = dict_to_obj(endpoints)
    return endpoints


def get_test_name(test_data_set):
    test_name = test_data_set[:-4]
    test_name = test_name.replace('_', ' ')
    return test_name

def generate_test_report(**kwargs):
    # kwargs = dict_to_obj(kwargs)
    test_name = get_test_name(kwargs.get('test_name'))
    report_ = [
                test_name, kwargs.get('test_id'), 
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
        'response_time': kwargs.get('response_time'),
        'status_code': kwargs.get('status_code'),
        'endpoint': kwargs.get('endpoint'),
        'passed': True
    }
    Constants.PASSED_LOG.append(report_)
    if not Constants.PASSED_TESTS.get(test_name):
        Constants.PASSED_TESTS[test_name] = [report]
    else:
        Constants.PASSED_TESTS[test_name].append(report)

def mark_test_as_failed(test_data_set):
    test_name = get_test_name(test_data_set)

    print(test_data_set)
    print('Constants.FAIL_LOG:>>>>>>>>>>', Constants.FAIL_LOG)
    Constants.FAIL_LOG.append(Constants.PASSED_LOG[-1])
    Constants.PASSED_TESTS[test_name][-1]['passed'] = False
    del Constants.PASSED_LOG[-1]
    # Constants.FAILED_TESTS[-1]['failed'] = True


def generate_analytics(fail_log):
    if not fail_log:
        return []

    res = {}
    prior_count = []
    for test_data in fail_log:
        if not res.get(test_data[2]):
            res = {
               test_data[2]: 1
            }
        else:
            res[test_data[2]] += 1

    for key, val in res.items():
        prior_count.append([val, key])

    # Constants.FAIL_LOG = np.array(fail_log)
    # priorities, counts = np.unique(Constants.FAIL_LOG[:, 2], return_counts=True)
    # # priorities = [str(x) for x in priorities]
    # prior_count = list(zip(counts, priorities))
    # return [' '.join(x) for x in prior_count]
    return prior_count


def object_modifier(obj, keys, value):
    temp = [obj]
    set_value = True
    for index, key in enumerate(keys):
        if re.match(r'^.*\[[0-9]+\]$', key):
            list_index = int(re.match(r'^(.*)\[([0-9]+)\]$', key)[2])
            attr = re.match(r'^(.*)(\[([0-9]+)\])$', key)[1]
            
            if len(temp[index].get(attr)) <= list_index:
                raise Exception('value is not replaceble in given object')

            if type(temp[index].get(attr)) is list and len(temp[index].get(attr)) > int(list_index):
                temp[index][attr][list_index] = object_modifier(temp[index].get(attr)[list_index], keys[index+1:], value)
                set_value = False
                break
        else:
            temp.append(temp[index].get(key))


    if set_value:
        temp[-1] = value

    count = len(temp) - 1
    while(count):
        temp[count-1][keys[count-1]] = temp[count]
        count-=1
    return temp[0]


def replace_attribute_value(obj, attributes):
    key_val = attributes.split('=')
    keys = key_val[0].split('.')
    value = simplify_data(key_val[1])
    return object_modifier(obj, keys, value)



def parse_snapshot(snapshot, actual=None):
    matched = re.match(r'snapshot\((.*\.json)\)((\.)\((.*)\))?', str(snapshot))
    if matched:
        snapshot_file = matched[1]
        if os.path.isfile(
            settings.TEST_DATA_PATH + '/snapshots/' + snapshot_file):

            f = open(settings.TEST_DATA_PATH + '/snapshots/' +
                                snapshot_file, 'r')

            try:
                obj = json.load(f)
            except Exception:
                return f.read()

            if matched[4]:              
                x = matched[4].split(',')
                for _ in x:
                    obj = replace_attribute_value(obj, _)
                return obj
            else:
                return obj
        else:
            if actual:
                f = open(settings.TEST_DATA_PATH + '/snapshots/' +
                                snapshot_file, 'w', encoding='utf-8')
            
                json.dump(actual, f, ensure_ascii=False, indent=4)
                return actual     

    return snapshot


def get_attribute_value_from_json(json_obj, attribute_path):
    if attribute_path and type(json_obj) is dict:
        attribute_value = copy.deepcopy(json_obj)
        attribute_path = attribute_path.split('.')
        for attribute in attribute_path:
            list_available = re.match(r'^(.*)\[([0-9]+)\]$', attribute)
            index = None
            if list_available:
                attribute = list_available[1]
                index = int(list_available[2])

            if type(attribute_value) is dict:
                attribute_value = attribute_value.get(attribute)
                if index is not None:
                    attribute_value = attribute_value[index]
            else:
                return attribute_path
                # raise Exception('attribute not found in dictionary object')
        
        return attribute_value

    raise Exception('get_attribute_value_from_json: argument error')

def set_context_vars(context_vars, response):

    if context_vars == '*':
        for var_name, value in response:
            setattr(Context, var_name, value)

    else:
        for var_name, element in context_vars.items():
            if re.match(r'^(.*)\[\]$', var_name):
                var_name = re.match(r'^(.*)\[\]$', var_name)[1]
                if Context.get(var_name):
                    Context.get(var_name).append(get_attribute_value_from_json(response, element))
                else:
                    empty_list = []
                    empty_list.append(get_attribute_value_from_json(response, element))
                    setattr(Context, var_name, empty_list)
            else:
                setattr(Context, var_name, get_attribute_value_from_json(response, element))


# expects csv file with base_url alias, endpoint, headers & req body
def create_default_data_by_api(file):
    data = request_response_formatter('default/' + file)
    
    for _ in data:
        url = getattr(settings, _.get('req').pop('base_url').upper() + '_BASE_URL') + \
            _.get('req').pop('endpoint')
        request_method = _.get('req').get('method', 'post')
        request_body = _.get('req')
        client = requests.Session()
        headers = _.get('headers')
        
        
        request_body = replace_context_var(request_body)
        client.headers.update(replace_context_var(headers))

        response = process_request_response(
            client=client,
            url=form_endpoint(url, request_body),
            data=request_body,
            method=request_method
        )

        if int(response.get('status_code')) in range(200, 205):
            print('Default Data Created with ' + url)
            if _.get('req').get('set_cookies'):
                Context.cookies = get_cookie_string_from(client.cookies)
            set_context_vars(_.get('req').get('context', {}), response)
        else:
            raise Exception('default data generation failed: ' + url + '\n\n' + str(_.get('req')) + '\n\n' + str(response))

        if _.get('req').get('wait'):
            time.sleep(int(_.get('req').get('wait')))
        

    return response


def form_endpoint(endpoint, request_body):
    if re.match(r'(.*/)?(<.*>)(/.*)?', endpoint):
        for k, v in request_body.items():
            endpoint = endpoint.replace('<' + k + '>', str(v))

    return endpoint


def get_cookie_string_from(cookie_jar):
    cookie_dict = cookie_jar.get_dict()
    cookie_string = ''
    for k,v in cookie_dict.items():
        cookie_string = cookie_string + k + '=' + v + '; '
    
    return cookie_string[:-2]


def replace_context_var(obj):
    
    traverser = JsonTraverser(
        object=obj, 
        find_with_regex='Context\.(.*)', 
        replace_with=Context
        )
    traverser.play()
    return traverser.get_analyzed()


def set_default_data_to_context():
    yml_files = os.listdir(settings.TEST_DATA_PATH + '/yml/')
    for f in yml_files:
        data = get_data_from_yml(f)
        if data:
            Context.update(data)
    return Context



Context = CustomDict()
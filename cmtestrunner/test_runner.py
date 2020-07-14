from unittest import TestCase
from rest_framework.test import APIClient
from django.utils.translation import ugettext as _
from django.utils import translation
from .middleware import (
                            request_response_formatter, get_all_locales,
                            get_translations, reset_db, BOOL,
                            set_auth_header, reset_auth_header, set_custom_headers,
                            set_lang_header, set_reset_seq_query, set_all_models,
                            unit_test_formatter, generate_test_report,
                            parse_snapshot, generate_analytics, get_test_endpoints,
                            Constants, mark_test_as_failed, form_endpoint, replace_context_var,
                            set_default_data_to_context
                        )
from unittest import TextTestRunner, TextTestResult
from django.test.runner import DiscoverRunner
import inspect
import traceback
from rest_framework.test import RequestsClient
from django.conf import settings
import requests
import re
import json
import os
import csv
from django.template.loader import render_to_string
from .object_manager import ObjectManager
import time
import copy


class CustomTextTestResult(TextTestResult):
    def startTestRun(self):
        set_reset_seq_query()
        set_all_models()
        set_default_data_to_context()

    def stopTestRun(self):
        self.testsRun = TestRunner.total_test_cases
        analytics = generate_analytics(Constants.FAIL_LOG)
        if TestRunner.query_executor:
            TestRunner.query_executor.quit()

        rendered = render_to_string('report.html', {
            'priority_fail_count': analytics,
            'passed_tests': Constants.PASSED_TESTS,
            'failed_tests': Constants.FAILED_TESTS,
            'success_count': self.testsRun - len(Constants.FAIL_LOG),
            'success_percentage': float("%0.2f"%((self.testsRun - len(Constants.FAIL_LOG))/(self.testsRun + len(Constants.EXCEPTIONS)) * 100)),
            'fail_count': len(Constants.FAIL_LOG),
            'fail_percentage': float("%0.2f"%(len(Constants.FAIL_LOG)/(self.testsRun + len(Constants.EXCEPTIONS)) * 100)),
            'exception_count': len(Constants.EXCEPTIONS),
            'exception_percentage': float("%0.2f"%(len(Constants.EXCEPTIONS)/(self.testsRun + len(Constants.EXCEPTIONS)) * 100)),
            'exception_details': Constants.EXCEPTIONS
        })

        
        if not os.path.exists(settings.TEST_PAYLOAD_PATH + '/reports'):
            os.makedirs(settings.TEST_PAYLOAD_PATH + '/reports')

        f = open(settings.TEST_PAYLOAD_PATH + '/reports/report.html', 'w')
        f.write(rendered)


    def startTest(self, test):
        "Called when the given test is about to be run"
        self._mirrorOutput = False
        self._setupStdout()


class CustomTextTestRunner(TextTestRunner):
    resultclass = CustomTextTestResult


class CMTestRunner(DiscoverRunner):
    test_runner = CustomTextTestRunner


class TestRunner(TestCase):
    client = False
    total_test_cases = 0
    create_default_user = lambda:None
    create_default_superuser = lambda:None
    create_default_superuser_token = lambda:None
    create_default_user_token = lambda:None
    reset_db = lambda:None
    total_exceptions = 0
    package = None
    ENDPOINTS = None
    query_executor = None



    def set_test_vars(self, test_data):
        # TestRunner.total_test_cases += 1
        self.response = None
        reset_auth_header(TestRunner.client)
        self.request_body = test_data.get('req')
        if self.request_body.get('user_type'):
            user_type = self.request_body.pop('user_type')
            if user_type == 'user':
                self.set_user_auth()
            elif user_type == 'admin':
                self.set_superuser_auth()
            elif user_type == 'invalid':
                set_auth_header(TestRunner.client, 'XXXinvalid_tokenXXX')
     
        self.reset_env = self.request_body.get('reset_env')
        

        self.wait = self.request_body.get('wait', 0)
        self.exp_response = test_data.get('resp')
        self.priority = self.request_body.pop('priority')
        self.test_id = self.request_body.pop('test_id')
        self.test_purpose = self.request_body.pop('comment')
        self.error_info = '\nTest ID: ' + str(
            self.test_id) + ' =====>>>>> ' + self.test_data_set + \
            ' failed for language: %s.\n' % self.accept_lang
        self.custom_headers = test_data.get('headers')
        # set_custom_headers(TestRunner.client, self.custom_headers)

        # if re.match(r'(.*/)?(<.*>)(/.*)?', self.endpoint):
        #     for k, v in self.request_body.items():
        #         self.endpoint = self.endpoint.replace('<' + k + '>', str(v))
        #         setattr(TestRunner.ENDPOINTS, self.endpoint_alias, self.endpoint)
        self.endpoint = form_endpoint(self.endpoint, self.request_body)
        setattr(TestRunner.ENDPOINTS, self.endpoint_alias, self.endpoint)


    def get_error(self, error_info, exp_response):
        errors = 'Validation failed for: ' + error_info + '\n\n'
        errors += 'Test Purpose: ' + self.test_purpose + '\n\n'
        errors += 'Requset Header: ' + str(
            TestRunner.client.headers) + '\n\n'
        errors += 'Request Body: \n\t' + str(self.request_body)[:100] + (
            ['', '....}'][len(str(self.request_body)) > 100]) + '\n\n'
        return errors

    def format_expected_response(self, exp_resp, accept_lang):
        translations = self.load_translations(accept_lang)
        if type(exp_resp) is list:
            for idx, x in enumerate(exp_resp):
                if type(x) is not dict:
                    if translations.get(x):
                        exp_resp[idx] = translations.get(x)
                    elif type(x) is not int:
                        exp_resp[idx] = _(x)
        elif type(exp_resp) is not dict:
            if translations.get(exp_resp):
                exp_resp = translations.get(exp_resp)
            elif type(exp_resp) is not int and type(exp_resp) is not float:
                exp_resp = _(exp_resp)
        return exp_resp

    def load_translations(self, accept_lang):
        return get_translations(accept_lang)


    def set_endpoints(self):
        TestRunner.ENDPOINTS = get_test_endpoints('endpoints.yml')

    def set_environment(self, envs):
        settings.TEST_SERVER = getattr(settings, self.package.upper() + '_BASE_URL')
        self.set_endpoints()
        TestRunner.client = self.get_client()   # need to find out why this is here again
        if settings.TEST_SERVER == 'http://testserver':
            TestRunner.reset_db = reset_db
        if TestRunner.query_executor:
            TestRunner.reset_db(TestRunner.query_executor)
        translation.activate('en')
        self.reproduce_steps = []
        try:
            for env in envs:
                self.reproduce_steps.append(env.__doc__)
                args = inspect.getargspec(env).args
                if args and args[0] == 'client':
                    env(TestRunner.client)
                else:
                    env()
        except Exception as e:
            Constants.EXCEPTIONS.append({
                'test_method': self.test_method.__name__,
                'details': e
            })
            raise
            # raise Exception(env.__doc__ + ':: ' + str(e))


    def set_headers(self, **kwargs):
        accept_lang = kwargs.get('accept_lang')
        set_lang_header(TestRunner.client, accept_lang)
        return True

    def set_user_auth(self):
        TestRunner.create_default_user()
        token = TestRunner.create_default_user_token()
        set_auth_header(TestRunner.client, token)

    def set_superuser_auth(self):
        TestRunner.create_default_superuser()
        token = TestRunner.create_default_superuser_token()
        set_auth_header(TestRunner.client, token)

    def get_response(self):
        return self.response

    def get_client(self):
        if settings.TEST_SERVER == 'http://testserver':
            return RequestsClient()
        else:
            return requests.Session()

    # see CONTRIBUTING.md for test data formats.
    def verify_test_result(self, exp_response, test_id, accept_lang):

        response_ = {}
        response_time = self.response.pop('response_time')

        

        exp_response_ = copy.deepcopy(exp_response)

        for key, value in exp_response_.items():
            if accept_lang != 'en':
                exp_response[key] = self.format_expected_response(
                    exp_response[key], accept_lang)
            if key == 'response':
                exp_response.pop('response')
                exp_response.update(parse_snapshot(value, self.response))   # there is a bug in this line, response may not be a dictionary always
                response_.update(self.response)
                continue
            exp_response[key] = value = parse_snapshot(value, self.response.get(key))
            response_[key] = self.response.get(key)
            exp_response = replace_context_var(exp_response)
        
        self.response = response_

        
        object_manager = ObjectManager(self.response, exp_response)
        object_manager.match_obj()
        self.response, exp_response = object_manager.get_converted()
        self.is_matched = object_manager.is_matched()
        error_info = ', '.join(object_manager.mismatched_keys())
        errors = self.get_error(error_info, exp_response)
        
        generate_test_report(
                test_name=self.test_data_set, priority=self.priority, test_id=self.test_id, 
                purpose=self.test_purpose, reproduce_steps=self.reproduce_steps,
                request_body=self.request_body, response=self.response, 
                request_header=dict(TestRunner.client.headers),
                expected_response=exp_response,
                error_info=error_info,
                response_time=response_time
                )
        
        try:
            self.assertEqual(self.is_matched, True, msg=errors)
        except AssertionError:
            mark_test_as_failed()
            raise


    def set_test_attributes(self, **kwargs):
        # TestRunner.client = self.get_client()
        self.test_method = kwargs.get('test_method')
        self.environment = kwargs.get('env', [])
        self.set_environment(self.environment)
        self.sub_test = kwargs.get('sub_test')
        self.accept_lang = kwargs.get('accept_lang')
        self.set_headers(accept_lang=self.accept_lang)
        self.test_data_set = kwargs.get('test_data_set')
        self.test_data = request_response_formatter('tests/' + self.test_data_set)
        self.endpoint_alias = kwargs.get('test_method').__name__.upper() + '_URL'
        self.endpoint = getattr(
            TestRunner.ENDPOINTS, 
            self.endpoint_alias
            )
        



    def process_tests(self, **kwargs):
        
        self.set_test_attributes(**kwargs)
            
        for each_test_data in self.test_data:
            self.set_test_vars(each_test_data)

            if self.request_body.get(
                    'accept_lang'
            ) and self.request_body.get('accept_lang') != self.accept_lang:
                TestRunner.total_test_cases -= 1
                continue
            time.sleep(float(self.wait)/1000)
            if self.reset_env:
                self.set_environment(self.environment)
            
        
            files = self.request_body.pop('files')
            self.request_body = replace_context_var(self.request_body)
            self.request_body['files'] = files
            set_custom_headers(TestRunner.client, replace_context_var(self.custom_headers))
            
            try:
                self.response = kwargs.get('test_method')(
                    client=TestRunner.client,
                    request_body=self.request_body,
                    accept_lang=self.accept_lang,
                    )
                
            except Exception as e:
                print(traceback.format_exc())
                errors = self.get_error(self.error_info, self.exp_response)
                with self.subTest():
                    self.assertEqual(None, e, msg=errors)
            with self.subTest():
                TestRunner.total_test_cases += 1
                self.verify_test_result(self.exp_response, self.test_id,
                                        self.accept_lang)

    def execute_tests(self, **kwargs):
        locales = get_all_locales()
        locales.append('en')
        for each_lang in locales:
            kwargs['accept_lang'] = each_lang
            self.process_tests(**kwargs)

    def execute_unit_tests(self, **kwargs):

        test_data_set = kwargs.get('test_data_set')
        test_data = unit_test_formatter(test_data_set)
        self.set_environment(kwargs.get('env'))

        for each_test_data in test_data:
            args = each_test_data.get('args')
            inits = each_test_data.get('inits')
            kwargs_ = each_test_data.get('kwargs')
            returns = each_test_data.get('returns')
            test_obj = kwargs.get('test_object')
            if kwargs.get('test_class'):
                test_class = getattr(test_obj, kwargs.get('test_class'))
                test_method = kwargs.get('test_method')
                if kwargs.get('static'):
                    test_obj = getattr(test_class, test_method)
                else:
                    test_obj = test_class(*inits)
                    test_obj = getattr(test_obj, test_method)
            else:
                test_obj = getattr(test_obj, kwargs.get('test_method'))
            response = test_obj(*args, **kwargs_)
            TestRunner.total_test_cases += 1

            self.assertEqual(str(response), str(returns))

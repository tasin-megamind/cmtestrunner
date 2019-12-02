from unittest import TestCase
from rest_framework.test import APIClient
from django.utils.translation import ugettext as _
from django.utils import translation
from .middleware import (request_response_formatter, get_all_locales,
                                   get_translations, reset_db, BOOL,
                                   set_auth_header, reset_auth_header, 
                                   set_lang_header, set_reset_seq_query, set_all_models)
from unittest import TextTestRunner, TextTestResult
from django.test.runner import DiscoverRunner
import inspect
import traceback


class CustomTextTestResult(TextTestResult):
    def startTestRun(self):
        set_reset_seq_query()
        set_all_models()

    def stopTestRun(self):
        self.testsRun = TestRunner.total_test_cases

    def startTest(self, test):
        "Called when the given test is about to be run"
        self._mirrorOutput = False
        self._setupStdout()


class CustomTextTestRunner(TextTestRunner):
    resultclass = CustomTextTestResult


class CMTestRunner(DiscoverRunner):
    test_runner = CustomTextTestRunner


class TestRunner(TestCase):
    client = APIClient()
    total_test_cases = 0
    create_default_user = lambda:None
    create_default_superuser = lambda:None
    create_default_superuser_token = lambda:None
    create_default_user_token = lambda:None

    def set_test_vars(self, test_data):
        TestRunner.total_test_cases += 1
        self.response = None
        self.request_body = test_data.get('req')
        if self.request_body.get('user_type'):
            user_type = self.request_body.pop('user_type')
            if user_type == 'user':
                self.set_user_auth()
            elif user_type == 'admin':
                self.set_superuser_auth()
            elif user_type == 'invalid':
                set_auth_header(TestRunner.client, 'XXXinvalid_tokenXXX')
            elif user_type == 'none':
                reset_auth_header(TestRunner.client)

        self.exp_response = test_data.get('resp')
        self.test_id = self.request_body.pop('test_id')
        self.test_purpose = self.request_body.pop('comment')
        self.error_info = '\nTest ID: ' + str(
            self.test_id) + ' =====>>>>> ' + self.test_data_set + \
            ' failed for language: %s.\n' % self.accept_lang

    def get_error(self, error_info, exp_response):
        errors = error_info
        errors += 'Test Purpose: ' + self.test_purpose + '\n\n'
        errors += 'Requset Header: ' + str(
            TestRunner.client._credentials) + '\n\n'
        errors += 'Request Body: ' + str(self.request_body) + '\n\n'
        errors += 'Actual Response: \n\t' + str(self.response)[:200] + (
            ['', '....}'][len(str(self.response)) > 200]) + '\n\n'
        errors += 'Expected Response: \n\t' + str(exp_response)[:200] + (
            ['', '....}'][len(str(exp_response)) > 200]) + '\n\n'
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

    def set_environment(self, envs):
        TestRunner.client = APIClient()
        reset_db()
        translation.activate('en')
        for env in envs:
            args = inspect.getargspec(env).args
            if args and args[0] == 'client':
                env(TestRunner.client)
            else:
                env()

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

    # see CONTRIBUTING.md for test data formats.
    def verify_test_result(self, exp_response, test_id, accept_lang):

        for key, value in exp_response.items():
            if accept_lang != 'en':
                exp_response[key] = self.format_expected_response(
                    exp_response[key], accept_lang)

            error_info = '\nTest ID: ' + str(
                test_id
            ) + ' =====>>>>> ' + self.test_data_set + ' >> ' + key + (
                ' validation failed for language: %s.\n' % accept_lang)

            errors = self.get_error(error_info, exp_response)

            if type(value) is list:
                self.assertEqual(
                    self.response.get(key, None), value, msg=errors)
            elif value == 'bool(true)':
                self.assertTrue(self.response.get(key, None), msg=errors)
            elif value == 'bool(false)':
                self.assertFalse(
                    BOOL.get(str(self.response.get(key, True)), True),
                    msg=errors)
            else:
                self.assertEqual(
                    str(self.response.get(key, None)),
                    str(exp_response[key]),
                    msg=errors)

    def set_test_attributes(self, **kwargs):
        self.set_environment(kwargs.get('env', []))
        self.sub_test = kwargs.get('sub_test')
        self.accept_lang = kwargs.get('accept_lang')
        self.set_headers(accept_lang=self.accept_lang)
        self.test_data_set = kwargs.get('test_data_set')
        self.test_data = request_response_formatter(self.test_data_set)

    def process_tests(self, **kwargs):
        self.set_test_attributes(**kwargs)
        for each_test_data in self.test_data:
            self.set_test_vars(each_test_data)
            try:
                if self.request_body.get(
                        'accept_lang'
                ) and self.request_body.get('accept_lang') != self.accept_lang:
                    TestRunner.total_test_cases -= 1
                    continue
                self.response = kwargs.get('test_method')(
                    client=TestRunner.client,
                    request_body=self.request_body,
                    accept_lang=self.accept_lang)

                with self.sub_test():
                    self.verify_test_result(self.exp_response, self.test_id,
                                            self.accept_lang)
            except Exception as e:
                print(traceback.format_exc())
                errors = self.get_error(self.error_info, self.exp_response)
                with self.sub_test():
                    self.assertEqual(None, e, msg=errors)

    def execute_tests(self, **kwargs):
        locales = get_all_locales()
        locales.append('en')
        for each_lang in locales:
            kwargs['accept_lang'] = each_lang
            self.process_tests(**kwargs)

    def execute_unit_tests(self, **kwargs):
        args = kwargs.get('test_data').get('args')
        kwargs_ = kwargs.get('test_data').get('kwargs')
        returns = kwargs.get('test_data').get('returns')
        response = kwargs.get('test_method')(*args, **kwargs_)

        self.assertEqual(str(response), str(returns))

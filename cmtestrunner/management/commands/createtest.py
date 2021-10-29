from django.core.management.base import BaseCommand
import re
import os
from django.conf import settings
import pkg_resources

class Command(BaseCommand):
    help = 'creates test'

    def create_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def create_file(self, file):
        open(file, 'a+')

    def update_file(self, file, content):
        f = open(file, 'a')
        f.write(content)

    def get_template(self, file):
        f = open(self.templates_dir + file, 'r')
        return f.read()

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            default=None,
            type=str,
            help='Specify test name',
            required=True)
        parser.add_argument(
            '-X',
            default=None,
            type=str,
            help='Specify request method',
            required=True)
        parser.add_argument(
            '-u', 
            default=None, 
            type=str, 
            help='Specify test endpoint withot host & port')
        parser.add_argument(
            '-a',
            default=None,
            type=str,
            help='Specify app name',
            required=True)

    def generate_tests(self):
        tests_template = self.get_template('tests_template.txt')
        current_tests = open(self.base_dir + '/' + self.app_name + '/test_api.py', 'r').read()

        tests_template = tests_template.replace('<test_name>', self.test_name)
        if re.sub(r'#.*', '', current_tests).strip():
            tests_template = tests_template.split('<><><><><><><><><><>')[1]    
        else:
            tests_template = tests_template.replace('<><><><><><><><><><>', '')
            tests_template = tests_template.replace('<app>', self.app_name)
            tests_template = tests_template.replace('<App>', self.app_name.capitalize())

        self.update_file(self.base_dir + '/' + self.app_name + '/test_api.py', tests_template)
    
    def generate_test_methods(self):
        test_methods_template = self.get_template('test_methods_template.txt')
        current_test_methods = open(self.base_dir + '/' + self.app_name + '/test_methods.py', 'r').read()

        test_methods_template = test_methods_template.replace('<test_name>', self.test_name)
        test_methods_template = test_methods_template.replace('<request_method>', self.request_method)
        test_methods_template = test_methods_template.replace('<test_url_alias>', self.test_url_alias)
        if re.sub(r'#.*', '', current_test_methods).strip():
            test_methods_template = test_methods_template.split('<><><><><><><><><><>')[1]
        else:
            test_methods_template = test_methods_template.replace('<><><><><><><><><><>', '')
        
        self.update_file(self.base_dir + '/' + self.app_name + '/test_methods.py', test_methods_template)

    def generate_endpoints(self):
        endpoints_template = self.get_template('endpoints_template.txt')
        endpoints_template = endpoints_template.replace('<test_url_alias>', self.test_url_alias)
        endpoints_template = endpoints_template.replace('<test_url>', self.test_url)
        self.update_file(self.base_dir + '/utils/test/endpoints.yml', endpoints_template)

    def handle(self, *args, **kwargs):
        self.templates_dir = pkg_resources.resource_filename('cmtestrunner', 'management/templates/')
        self.app_name = kwargs.get('a')
        self.test_url = kwargs.get('u')
        self.request_method = kwargs.get('X')
        self.test_name = kwargs.get('t')
        self.base_dir = settings.BASE_DIR

        self.test_url_alias = self.test_name.upper() + '_URL'
        # self.create_dir(self.base_dir + '/' + self.app_name + '/tests')
        self.create_file(self.base_dir + '/' + self.app_name + '/test_api.py')
        self.create_file(self.base_dir + '/' + self.app_name + '/test_methods.py')

        self.generate_endpoints()
        self.generate_test_methods()
        self.generate_tests()
        
        if not os.path.exists(self.base_dir + '/utils/test/data/tests/' + self.test_name + '.csv'):
            file_content = 'test_id,request_body,resp_response,priority,comment'
            self.update_file(self.base_dir + '/utils/test/data/tests/' + self.test_name + '.csv', file_content)

        self.stdout.write(
                self.style.SUCCESS('Successfully created test'))
        












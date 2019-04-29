from django.core.management.base import BaseCommand
import re
import os
from django.conf import settings
import pkg_resources


class Command(BaseCommand):
    help = 'Creates test automatically.'

    def create_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def create_file(self, file):
        open(file, 'a+')

    def update_file(self, file, content):
        f = open(file, 'a')
        f.write(content)

    def create_skeleton(self):
        # self.create_dir(settings.BASE_DIR + '/' + self.app_name + '/tests')
        self.create_file(settings.BASE_DIR + '/' + self.app_name + '/test_unit.py')

    def write_to_unit_tests(self, content):
        with open(settings.BASE_DIR + '/' + self.app_name + '/test_unit.py', 'a') as f:
            f.write(content)

    def write_to_unit_test_imports(self, content):
        with open(settings.BASE_DIR + '/utils/test/' + 'unittest.py',
                  'a') as f:
            f.write(content)

    def create_test_data_file(self, test_method):
        if not os.path.exists(settings.BASE_DIR + '/utils/test/data/unittest/' + test_method + '.csv'):
            os.mknod(settings.BASE_DIR + '/utils/test/data/unittest/' + test_method + '.csv')

    def get_template(self, file_name):
        template = open(self.templates_dir + file_name, 'r')
        return template.read()

    def create_unit_test(self,
                         test_name,
                         import_path,
                         test_class=None,
                         static_method=False):

        try:
            current_tests = open(settings.BASE_DIR + '/' + self.app_name + '/test_unit.py', 'r').read()
            test_method_template = self.get_template(
                'unit_test_method_template.txt')
            test_import_template = self.get_template(
                'unit_test_import_template.txt')
            self.create_test_data_file(test_name)

            if current_tests:
                test_method_template = test_method_template.split('<><><><><><><><><>')[1]
            else:
                test_method_template = test_method_template.replace('<><><><><><><><><>', '')

            test_method_template = test_method_template.replace(
                '<test_name>', test_name)

            if test_class:
                test_import_template = test_import_template.replace(
                    '<test_object>', test_class)
                test_method_template = test_method_template.replace(
                    '<test_class_name>', test_class)
            else:
                test_method_template = test_method_template.replace(
                    '\'<test_class_name>\'', 'False')
                test_import_template = test_import_template.replace(
                    '<test_object>', test_name)
            
            if not static_method:
                test_method_template = test_method_template.replace(
                '<static>', 'False')
            else:
                test_method_template = test_method_template.replace(
                '<static>', 'True')
            

            test_method_template = test_method_template.replace(
                '<test_method_name>', test_name)
            test_import_template = test_import_template.replace(
                'import_path', import_path)

            self.write_to_unit_tests(test_method_template)
            self.write_to_unit_test_imports(test_import_template)

            return True

        except Exception as e:
            print(e)
            return False

    def add_arguments(self, parser):
        parser.add_argument(
            '-t',
            default=None,
            type=str,
            help='Specify test name',
            required=True)
        parser.add_argument(
            '-a',
            default=None,
            type=str,
            help='Specify app name',
            required=True)
        parser.add_argument(
            '-p',
            default=None,
            type=str,
            help='Specify test method location',
            required=True)
        parser.add_argument(
            '-c', default=None, type=str, help='Specify test class')
        parser.add_argument(
            '--static',
            action='store_true',
            dest='static_method',
            help='Specifies your method as static',
        )

    def handle(self, *args, **options):
        self.templates_dir = pkg_resources.resource_filename('cmtestrunner', 'management/templates/')
        test_name = options.get('t')
        self.app_name = options.get('a')
        import_path = options.get('p')
        test_class = options.get('c', None)
        static_method = options.get('static_method', False)
        self.create_skeleton()

        if self.create_unit_test(test_name, import_path, test_class,
                                 static_method):
            self.stdout.write(
                self.style.SUCCESS('Successfully added test "%s"' % test_name))
        else:
            self.stdout.write(
                self.style.ERROR('Error while adding test: "%s"' % test_name))

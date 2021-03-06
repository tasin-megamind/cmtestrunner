from django.core.management.base import BaseCommand
import re
import os
import config.settings as settings


class Command(BaseCommand):
    help = 'Creates test automatically.'

    def write_to_unit_tests(self, content):
        with open(settings.TEST_PAYLOAD_PATH + 'unit_tests.py', 'a') as f:
            f.write(content)

    def write_to_unit_test_imports(self, content):
        with open(settings.TEST_PAYLOAD_PATH + 'unit_test_imports.py',
                  'a') as f:
            f.write(content)

    def create_test_data_file(self, test_method):
        if not os.path.exists(settings.TEST_DATA_PATH + test_method + '.csv'):
            os.mknod(settings.TEST_DATA_PATH + test_method + '.csv')

    def get_template(self, file_name):
        template = open(settings.TEST_PAYLOAD_PATH + file_name, 'r')
        return template.read()

    def create_unit_test(self,
                         test_name,
                         import_path,
                         test_class=None,
                         static_method=False):

        try:
            test_method_template = self.get_template(
                'unit_test_method_template.txt')
            test_import_template = self.get_template(
                'unit_test_import_template.txt')
            test_method = re.sub('test_[A-Za-z]+_', '', test_name)
            self.create_test_data_file(test_method)

            test_method_template = test_method_template.replace(
                'test_name', test_name)
            test_method_template = test_method_template.replace(
                'test_data_file_name', test_method)

            if test_class:
                test_import_template = test_import_template.replace(
                    'test_object', test_class)
                if not static_method:
                    test_class += '()'
                test_method_template = test_method_template.replace(
                    'test_class_name', test_class)
            else:
                test_import_template = test_import_template.replace(
                    'test_object', test_method)
                test_method_template = test_method_template.replace(
                    'test_class_name.', '')

            test_method_template = test_method_template.replace(
                'test_method_name', test_method)
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
        test_name = options.get('t')
        import_path = options.get('p')
        test_class = options.get('c', None)
        static_method = options.get('static_method', False)

        if self.create_unit_test(test_name, import_path, test_class,
                                 static_method):
            self.stdout.write(
                self.style.SUCCESS('Successfully added test "%s"' % test_name))
        else:
            self.stdout.write(
                self.style.ERROR('Error while adding test: "%s"' % test_name))

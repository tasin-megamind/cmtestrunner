from django.core.management.base import BaseCommand
import re
import os
from django.conf import settings
import pkg_resources

class Command(BaseCommand):
    help = 'creates test skeleton for API testing'

    def create_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('created ' + directory)

    def create_file(self, file):
        open(file, 'a+')
        print('created ' + file)

    def handle(self, *args, **kwargs):
        base_dir = str(settings.BASE_DIR)
        self.create_dir(base_dir + '/utils/test')
        self.create_dir(base_dir + '/utils')
        self.create_dir(base_dir + '/utils/test/reports')
        self.create_dir(base_dir + '/utils/test/data')
        self.create_dir(base_dir + '/utils/test/data/unittest')
        self.create_dir(base_dir + '/utils/test/data/snapshots')
        self.create_dir(base_dir + '/utils/test/data/upload')
        self.create_dir(base_dir + '/utils/test/data/tests')
        self.create_dir(base_dir + '/utils/test/data/default')
        self.create_dir(base_dir + '/utils/test/data/yml')
        self.create_dir(base_dir + '/utils/test/translation')
        self.create_dir(base_dir + '/utils/fixtures')

        self.create_file(base_dir + '/utils/__init__.py')
        self.create_file(base_dir + '/utils/test/endpoints.yml')
        self.create_file(base_dir + '/utils/test/unittest.py')
        self.create_file(base_dir + '/utils/test/test_runner.py')
        self.create_file(base_dir + '/utils/test/middleware.py')

        templates_dir = pkg_resources.resource_filename('cmtestrunner', 'management/templates/')
        test_runner_content = None
        with open(templates_dir + 'test_runner_template.txt', 'r') as f:
            test_runner_content = f.read()

        with open(base_dir + '/utils/test/test_runner.py' , 'w') as f:
            f.write(test_runner_content)


        self.stdout.write(
                self.style.SUCCESS('Successfully created test skeleton'))

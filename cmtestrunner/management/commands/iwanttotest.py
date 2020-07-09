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
        self.create_dir(settings.BASE_DIR + '/utils')
        self.create_dir(settings.BASE_DIR + '/utils/test')
        self.create_dir(settings.BASE_DIR + '/utils/test/reports')
        self.create_dir(settings.BASE_DIR + '/utils/test/data')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/unittest')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/snapshots')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/upload')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/tests')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/default')
        self.create_dir(settings.BASE_DIR + '/utils/test/data/yml')
        self.create_dir(settings.BASE_DIR + '/utils/test/translation')
        self.create_dir(settings.BASE_DIR + '/utils/fixtures')

        self.create_file(settings.BASE_DIR + '/utils/__init__.py')
        self.create_file(settings.BASE_DIR + '/utils/test/endpoints.yml')
        self.create_file(settings.BASE_DIR + '/utils/test/unittest.py')
        self.create_file(settings.BASE_DIR + '/utils/test/test_runner.py')
        self.create_file(settings.BASE_DIR + '/utils/test/middleware.py')

        templates_dir = pkg_resources.resource_filename('cmtestrunner', 'management/templates/')
        test_runner_content = None
        with open(templates_dir + 'test_runner_template.txt', 'r') as f:
            test_runner_content = f.read()

        with open(settings.BASE_DIR + '/utils/test/test_runner.py' , 'w') as f:
            f.write(test_runner_content)


        self.stdout.write(
                self.style.SUCCESS('Successfully created test skeleton'))

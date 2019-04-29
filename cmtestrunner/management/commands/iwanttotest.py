from django.core.management.base import BaseCommand
import re
import os
from django.conf import settings

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
        self.create_dir(settings.BASE_DIR + '/utils/test/translation')
        self.create_dir(settings.BASE_DIR + '/utils/fixtures')

        self.create_file(settings.BASE_DIR + '/utils/__init__.py')
        self.create_file(settings.BASE_DIR + '/utils/test/endpoints.yml')
        self.create_file(settings.BASE_DIR + '/utils/test/unittest.py')

        self.stdout.write(
                self.style.SUCCESS('Successfully created test skeleton'))

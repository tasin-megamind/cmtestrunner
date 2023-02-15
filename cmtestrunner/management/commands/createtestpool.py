from genericpath import isdir
from django.core.management.base import BaseCommand
import re
import os
from django.conf import settings
import pkg_resources
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'generates test pool from test directory'

    def create_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('created ' + directory)

    def create_file(self, file):
        open(file, 'a+')
        print('created ' + file)

    def handle(self, *args, **kwargs):
        base_dir = str(settings.BASE_DIR)
        test_dir = base_dir + '/utils/test/data/tests'

        templates_dir = pkg_resources.resource_filename('cmtestrunner', 'templates/')

        test_pool = render_to_string('test_pool.html', {
            'test_data_dir': test_dir 
        })

        f = open(settings.TEST_PAYLOAD_PATH + '/reports/test_pool.html', 'w')
        f.write(test_pool)

        self.stdout.write(
                self.style.SUCCESS('launched test pool'))

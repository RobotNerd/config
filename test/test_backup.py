#!/usr/bin/python3
import os
import unittest

from test import data
from lib import backup
from lib.logger import Logger


FILENAME='test_backup_file.txt'
PATH=f'{data.BASE_PATH}/{FILENAME}'
logger = Logger()


class TestBackup(unittest.TestCase):

    def test_backup_file(self):
        data.reset()
        backup.to_file(logger, PATH)
        contents = os.listdir(data.BASE_PATH)
        self.assertEqual(len(contents), 0)

        with open(PATH, 'w') as file:
            file.write('test')
        contents = os.listdir(data.BASE_PATH)
        self.assertEqual(len(contents), 1)

        backup.to_file(logger, PATH)
        contents = os.listdir(data.BASE_PATH)
        self.assertEqual(len(contents), 1)
        self.assertIn(f'{FILENAME}.bkp.', contents[0])

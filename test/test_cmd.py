#!/usr/bin/python3
import unittest

from lib import cmd


class TestCommand(unittest.TestCase):

    def test_run_command(self):
        cmd.run('ls -l'.split(' '))
        self.assertTrue(True)

    def test_run_bad_command(self):
        with self.assertRaises(cmd.CommandRunnerError):
            cmd.run('ls -l ./this-is-not-a-valid-path/'.split(' '))

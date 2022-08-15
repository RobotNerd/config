#!/usr/bin/python3
import unittest

from lib.command import Cmd, CommandRunnerError


class TestCommand(unittest.TestCase):

    def test_run_command(self):
        Cmd.run('ls -l'.split(' '))
        self.assertTrue(True)

    def test_run_bad_command(self):
        with self.assertRaises(CommandRunnerError):
            Cmd.run('ls -l ./this-is-not-a-valid-path/'.split(' '))

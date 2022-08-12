#!/usr/bin/python3

import subprocess


class CommandRunnerError(Exception):
    pass


class Cmd:

    @staticmethod
    def run(cmd):
        output = subprocess.run(cmd, capture_output=True)
        if output.returncode != 0:
            raise CommandRunnerError(output.stderr.decode('utf-8'))

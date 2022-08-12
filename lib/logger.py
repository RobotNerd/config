#!/usr/bin/python3
from colorama import Fore
from colorama import Style


class Logger():

    levels = {
        'info': 0,
        'warn': 1,
        'error': 2
    }

    def __init__(self, level):
        key = level.lower().strip()
        self._level = self.levels.get(key)
        if self._level is None:
            raise ValueError(f'Invalid log level: f{level}')

    def info(self, msg):
        if self._level <= self.levels['info']:
            print(f'INFO:  {msg}')

    def warn(self, msg):
        if self._level <= self.levels['warn']:
            print(f'{Fore.YELLOW}WARN:  {msg}{Style.RESET_ALL}')

    def error(self, msg):
        if self._level <= self.levels['error']:
            print(f'{Fore.RED}ERROR: {msg}{Style.RESET_ALL}')

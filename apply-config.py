#!/usr/bin/python3

import argparse

from lib.config import Config
from lib.config_files import ConfigFiles
from lib.git import Git
from lib.logger import Logger
from lib.ssh import SSH
from lib.vim import Vim

CONFIG_PATH = './config.yml'


class PlatformConfigMissing(Exception):
    pass


def apply_changes(logger, args, cfg):
    ConfigFiles.copy(logger, args, cfg)
    Git.configure(logger, cfg)
    Vim.vundle(logger, cfg)
    SSH.generate_key(logger, cfg)
    SSH.enable_sshd(logger, cfg)


def parse_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'platform',
        type=str,
        help=f'target platform (as specified in {CONFIG_PATH})')
    parser.add_argument(
        '--work',
        action='store_true',
        help='apply config specific to work machine')
    parser.add_argument(
        '--personal',
        action='store_true',
        help='apply config specific to personal machine')
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['info', 'warn', 'error'],
        help='log level for messaging')

    return parser.parse_args()


def show_manual_steps():
    print('''
Manual setup checklist:
- Browser extensions
  - Lastpass
  - uBlock
  - Foxy Gestures (Firefox)
- Setup security keys
  - github
- VS Code extensions
  - vscode-viml-syntax
  - sort lines
- Login to services
  - Dropbox
  - GitHub
  - StackOverflow
''')


def verify_platform_exists(logger, platform, cfg):
    if cfg.get(platform) is None:
        msg = f'platform "{platform}" does not exist in {CONFIG_PATH}'
        logger.error(msg)
        raise PlatformConfigMissing(msg)


def run():
    args = parse_cli_args()
    logger = Logger(args.log_level)
    cfg_loader = Config(logger)
    cfg = cfg_loader.load(CONFIG_PATH)
    verify_platform_exists(logger, args.platform, cfg)
    # apply_changes(logger, args, cfg)  # TODO temporarily disabled to prevent applying it to my system
    show_manual_steps()


if __name__ == "__main__":
    run()

#!/usr/bin/python3

import argparse

from lib.config import Config
from lib import config_files
from lib import git
from lib.logger import Logger
from lib import shell
from lib.ssh import SSH
from lib.vim import Vim

from platforms.alpine import Alpine
from platforms.macos import MacOS
from platforms.manjaro import Manjaro

import lib.manual_config as manual_config

CONFIG_PATH = './config.yml'


class PlatformConfigMissing(Exception):
    pass


class UnrecognizedPlatform(Exception):
    pass


def apply_changes(logger, args, cfg):
    platform = get_platform(logger, args, cfg)
    platform.install_applications()
    config_files.copy(logger, args, cfg)
    shell.add_custom_shell_config(logger, cfg)
    git.configure(logger, cfg)
    Vim.vundle(logger, cfg)
    SSH.generate_key(logger, cfg)
    platform.enable_sshd()


def get_platform(logger, args, cfg):
    platform = None
    if args.platform == 'macos':
        platform = MacOS(logger, args, cfg)
    elif args.platform == 'manjaro_linux':
        platform = Manjaro(logger, args, cfg)
    elif args.platform == 'alpine_linux':
        platform = Alpine(logger, args, cfg)
    else:
        raise UnrecognizedPlatform(args.platform)
    return platform


def parse_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'platform',
        type=str,
        help=f'target platform (as specified in {CONFIG_PATH})')
    parser.add_argument(
        '--config-path',
        type=str,
        default=CONFIG_PATH,
        help='path to config file'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='info',
        choices=['info', 'warn', 'error'],
        help='log level for messaging')
    parser.add_argument(
        '--personal',
        action='store_true',
        help='apply config specific to personal machine')
    parser.add_argument(
        '--work',
        action='store_true',
        help='apply config specific to work machine')

    return parser.parse_args()


def show_manual_steps():
    print(manual_config.to_string())


def verify_platform_exists(logger, platform, cfg):
    if cfg.get(platform) is None:
        msg = f'platform "{platform}" does not exist in {CONFIG_PATH}'
        logger.error(msg)
        raise PlatformConfigMissing(msg)


def run():
    args = parse_cli_args()
    logger = Logger(args.log_level)
    cfg_loader = Config(logger)
    cfg = cfg_loader.load(args.config_path)
    verify_platform_exists(logger, args.platform, cfg)
    apply_changes(logger, args, cfg)
    show_manual_steps()


if __name__ == "__main__":
    run()

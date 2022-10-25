#!/usr/bin/python3
import os

from lib import manual_config


class UnsupportedShell(Exception):
    pass


def add_custom_shell_config(logger, cfg):
    rc_file = _get_or_create_rc_file(logger)
    rc_custom = _get_rc_custom_path(cfg)
    if _contains_rc_custom_cmd(rc_file, rc_custom):
        logger.info(f'.rc_custom already referenced in {rc_file}; no changes made')
        return
    _append_rc_custom_cmd(rc_file, rc_custom)
    manual_config.add_step('Shell scripts', f'run command: source {rc_file}')


def add_cmd_to_rc_custom(cfg, cmd):
    rc_custom = _get_rc_custom_path(cfg)
    with open(os.path.expandvars(rc_custom), 'a') as file:
        file.write(f'\n\n{cmd}\n')


def _get_or_create_rc_file(logger):
    shell = get_shell_name()
    if shell == '/bin/bash':
        rc_file = os.path.expandvars('$HOME/.bashrc')
    elif shell == '/bin/zsh':
        rc_file = os.path.expandvars('$HOME/.zshrc')
    elif shell == '/bin/ash':
        rc_file = os.path.expandvars('$HOME/.profile')
    else:
        raise UnsupportedShell(shell)
    
    if not os.path.exists(rc_file):
        logger.warn(f'rc file {rc_file} does not exist; creating file')
        open(rc_file, 'a').close()

    return rc_file


def get_shell_name():
    shell = os.environ.get('SHELL')
    if shell is None:
        if os.path.exists('/bin/ash'):
            shell = '/bin/ash'
        elif os.path.exists('/bin/bash'):
            shell = '/bin/bash'
        elif os.path.exists('/bin/zsh'):
            shell = '/bin/zsh'
    return shell


def _append_rc_custom_cmd(rc_file, rc_custom):
    with open(rc_file, 'a') as file:
        file.write(f'\nsource {rc_custom}\n')


def _contains_rc_custom_cmd(rc_file, rc_custom):
    custom = rc_custom.split('/')[-1]
    with open(rc_file, 'r') as file:
        text = file.read()
        if custom in text:
            return True
    return False


def _get_rc_custom_path(cfg):
    path = None
    for item in cfg['config_files']['all']:
        if item['name'] == 'rc-custom':
            path = item['dst']
            break
    return path

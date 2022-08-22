#!/usr/bin/python3
from lib import cmd


def configure(logger, cfg):
    if not cfg['configure_git_global_settings']:
        return

    logger.info('configuring git')
    base_cmd = 'git config --global'.split(' ')

    email = cfg['user_info']['email']
    name = cfg['user_info']['name']

    cmd.run(base_cmd + f'user.email {email}'.split(' '))
    cmd.run(base_cmd + f'user.name {name}'.split(' '))
    cmd.run(base_cmd + 'pager.branch false'.split(' '))
    cmd.run(base_cmd + 'pager.diff false'.split(' '))

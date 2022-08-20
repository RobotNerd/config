#!/usr/bin/python3
from lib.command import Cmd


class Git:

    @staticmethod
    def configure(logger, cfg):
        if not cfg['configure_git_global_settings']:
            return

        logger.info('configuring git')
        base_cmd = 'git config --global'.split(' ')

        email = cfg['user_info']['email']
        name = cfg['user_info']['name']

        Cmd.run(base_cmd + f'user.email {email}'.split(' '))
        Cmd.run(base_cmd + f'user.name {name}'.split(' '))
        Cmd.run(base_cmd + 'pager.branch false'.split(' '))
        Cmd.run(base_cmd + 'pager.diff false'.split(' '))

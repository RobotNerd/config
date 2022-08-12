#!/usr/bin/python3
from lib.command import Cmd


class Git:

    @staticmethod
    def configure(logger, cfg):
        logger.info('configuring git')
        base_cmd = 'git config --global'.split(' ')

        email = cfg['user_info']['email'].split(' ')
        name = cfg['user_info']['name'].split(' ')

        Cmd.run(base_cmd + f'user.email {email}')
        Cmd.run(base_cmd + f'user.name {name}')
        Cmd.run(base_cmd + 'pager.branch false'.split(' '))
        Cmd.run(base_cmd + 'pager.diff false'.split(' '))

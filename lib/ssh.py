#!/usr/bin/python3
import os

from lib.backup import Backup
from lib.command import Cmd


class SSH:

    @staticmethod
    def generate_key(logger, cfg):
        if not cfg['ssh']['generate_ssh_key']:
            return

        logger.info('generating ssh key')
        keyfile_path = os.path.expandvars(cfg['ssh']['ssh_keyfile_path'])
        Backup.file(logger, keyfile_path)
        # See stackoverflow for command details: https://stackoverflow.com/a/43235320/241025
        cmd = [
            'ssh-keygen', '-q',
            '-N', '""',  # Do not use a passphrase.
            '-t', cfg['ssh']['ssh_algorithm'],
            '-f', keyfile_path,
            '-C', cfg['user_info']['email'],
        ]
        Cmd.run(cmd)

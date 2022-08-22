#!/usr/bin/python3
import os

from lib import backup
from lib import cmd


def generate_key(logger, cfg):
    if not cfg['ssh']['generate_ssh_key']:
        return

    logger.info('generating ssh key')
    keyfile_path = os.path.expandvars(cfg['ssh']['ssh_keyfile_path'])
    backup.to_file(logger, keyfile_path)
    # See stackoverflow for command details: https://stackoverflow.com/a/43235320/241025
    command = [
        'ssh-keygen', '-q',
        '-N', '""',  # Do not use a passphrase.
        '-t', cfg['ssh']['ssh_algorithm'],
        '-f', keyfile_path,
        '-C', cfg['user_info']['email'],
    ]
    cmd.run(command)

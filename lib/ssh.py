#!/usr/bin/python3

from lib.command import Cmd
import os
import time


class SSH:

    @staticmethod
    def generate_key(logger, cfg):
        if not cfg['ssh']['generate_ssh_key']:
            return

        logger.info('generating ssh key')
        SSH.backup_existing_file(logger, cfg)
        cmd = f"ssh-keygen -t {cfg['ssh']['ssh_keyfile']} -C {cfg['user_info']['email']}".split()
        Cmd.run(cmd)
    
    @staticmethod
    def backup_existing_file(logger, cfg):
        path = f"{os.environ['HOME']}/.ssh/id_{cfg['ssh']['ssh_keyfile']}"
        if os.path.exists(path):
            backup_path = path + f'.bkp.{round(time.time())}'
            logger.warn(f'file {path} exists\nmaking backup {backup_path}')
            os.rename(path, backup_path)

    @staticmethod
    def enable_sshd(logger, cfg):
        if not cfg['ssh']['sshd_enabled']:
            return
        
        logger.info('enabling sshd')
        Cmd.run('sudo systemctl enable sshd'.split())
        Cmd.run('sudo systemctl start sshd'.split())
        raise NotImplementedError()

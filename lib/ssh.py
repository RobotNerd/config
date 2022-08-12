#!/usr/bin/python3
from lib.backup import Backup
from lib.command import Cmd
import os


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
        path = os.path.expandvars(f"$HOME/.ssh/id_{cfg['ssh']['ssh_keyfile']}")
        Backup.file(logger, path)

    @staticmethod
    def enable_sshd(logger, cfg):
        if not cfg['ssh']['sshd_enabled']:
            return
        
        logger.info('enabling sshd')
        Cmd.run('sudo systemctl enable sshd'.split())
        Cmd.run('sudo systemctl start sshd'.split())
        raise NotImplementedError()

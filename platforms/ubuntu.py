#!/usr/bin/python3
from lib import cmd
import lib.manual_config as manual_config


class Ubuntu:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        logger.info('Enter sudo password when prompted')
        cmd.run(['sudo', 'ls'])
    
    def install_applications(self):
        platform = self.cfg['ubuntu']

        self.logger.info('install packages')
        apt = platform['apt']
        packages = []
        if apt['all']:
            packages = apt['all']
        if self.args.personal and apt['personal']:
            packages += apt['personal']
        if self.args.work and apt['work']:
            packages += apt['work']
        if packages:
            cmd.run(['sudo', 'apt-get', 'install', '-y'] + packages)
        
        manual_config.add_step('ubuntu', f'Install vscode {platform['vscode']['src']}')
    
    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return
        self.logger.info('enabling sshd')
        cmd.run('systemctl enable ssh'.split())
        cmd.run('systemctl start ssh'.split())

#!/usr/bin/python3
from lib import cmd


class Ubuntu:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        logger.info('Enter sudo password when prompted')
    
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
            cmd.run(['sudo', 'apt', 'install', '-y'] + packages)
        
        self._install_vscode()

    def _install_vscode(self):
        if not self.cfg['ubuntu']['vscode']['install']:
            return
        src = self.cfg['ubuntu']['vscode']['src']
        dst = self.cfg['ubuntu']['vscode']['dst']
        cmd.run(f'wget {src} -O {dst}'.split(' '))
        cmd.run(f'sudo apt install {dst}'.split(' '))
    
    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return
        self.logger.info('enabling sshd')
        cmd.run('systemctl enable ssh'.split())
        cmd.run('systemctl start ssh'.split())

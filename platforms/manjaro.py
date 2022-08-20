#!/usr/bin/python3
from lib.command import Cmd


class Manjaro:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        # TODO prompt for sudo pwd
    
    def install_applications(self):
        platform = self.cfg['manjaro_linux']

        self.logger.info('install packages')
        pacman = platform['pacman']
        packages = pacman['all']
        if self.args.personal:
            packages += pacman['personal']
        if self.args.work:
            packages += pacman['work']
        Cmd.run(['sudo', 'pacman', '-Syu', '--noconfirm'] + packages)
    
        self.logger.info('installing packages with snap')
        snap = platform['snap_applications']
        snap_packages = snap['all']
        if self.args.personal:
            snap_packages += snap['personal']
        if self.args.work:
            snap_packages += snap['work']
        Cmd.run(['sudo', 'snap', 'install'] + snap_packages)

        self._install_zoom()
    
    def _install_zoom(self):
        if not self.cfg['manjaro_linux']['zoom']['install']:
            return
        
        src = self.cfg['manjaro_linux']['zoom']['src']
        dst = self.cfg['manjaro_linux']['zoom']['dst']

        Cmd.run(f'wget {src} -O {dst}'.split(' '))
        Cmd.run(f'sudo pacman -U --noconfirm {dst}'.split(' '))
    
    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return

        self.logger.info('enabling sshd')
        Cmd.run('systemctl enable sshd'.split())
        Cmd.run('systemctl start sshd'.split())

#!/usr/bin/python3
from lib import cmd
from lib import shell


class MacOS:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        self._install_homebrew()
        logger.info('Enter sudo password when prompted')

    def _install_homebrew(self):
        self.logger.info('installing homebrew')
        tmp_path = '/tmp/install_brew.sh'
        cmd.run([
            'curl',
            '-fsSL',
            'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh',
            '>',
            tmp_path
        ])
        cmd.run(['/bin/bash', tmp_path])
        cmd.run(['rm', tmp_path])
    
    def install_applications(self):
        platform = self.cfg['macos']
        brew = platform['brew']

        self.logger.info('installing brew applications')
        packages = []
        if brew['all']:
            packages = brew['all']
        if self.args.personal and brew['personal']:
            packages += brew['personal']
        if self.args.work and brew['work']:
            packages += brew['work']
        if packages:
            cmd.run(['brew', 'install'] + packages)

        self.logger.info('installing brew cask applications')
        brew = platform['brew_casks']
        packages = []
        if brew['all']:
            packages = brew['all']
        if self.args.personal and brew['personal']:
            casks += brew['personal']
        if self.args.work and brew['work']:
            casks += brew['work']
        if casks:
            cmd.run(['brew', 'install', '--cask'] + casks)

    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return

        self.logger.info('enabling sshd')
        cmd.run('sudo systemsetup -setremotelogin on'.split(' '))

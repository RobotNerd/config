#!/usr/bin/python3
from inspect import ArgSpec
from lib.command import Cmd


class MacOS:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        self._install_homebrew()
        # TODO prompt for sudo pwd

    def _install_homebrew(self):
        self.logger.info('installing homebrew')
        Cmd.run([
            '/bin/bash',
            '-c',
            '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        ])
    
    def install_applications(self):
        self.logger.info('installing brew applications')
        packages = self.cfg['macos']['brew']['all']
        if self.args.personal:
            packages += self.cfg['macos']['brew']['personal']
        if self.args.work:
            packages += self.cfg['macos']['brew']['work']
        Cmd.run(['brew', 'install'] + packages)

        self.logger.info('installing brew cask applications')
        casks = self.cfg['macos']['brew_casks']['all']
        if self.args.personal:
            casks += self.cfg['macos']['brew_casks']['personal']
        if self.args.work:
            casks += self.cfg['macos']['brew_casks']['work']
        Cmd.run(['brew', 'install', '--cask'] + casks)

    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return

        self.logger.info('enabling sshd')
        Cmd.run('sudo systemsetup -setremotelogin on'.split(' '))

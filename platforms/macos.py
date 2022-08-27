#!/usr/bin/python3
import os

from lib import cmd


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
            '-o',
            tmp_path
        ])
        # To run brew without prompting the user, the env var NONINTERACTIVE needs to
        # be set to 1. The env var is temporarily added to run the command.
        # See https://stackoverflow.com/a/34333710/241025
        old_environ = dict(os.environ)
        new_environ = dict(os.environ)
        try:
            new_environ['NONINTERACTIVE'] = 1
            os.environ.update(new_environ)
            cmd.run(['/bin/bash', tmp_path])
        finally:
            os.environ.clear()
            os.environ.update(old_environ)
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

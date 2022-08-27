#!/usr/bin/python3
import os

from lib import cmd
from lib import manual_config


class MacOS:

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
        logger.info('Enter sudo password when prompted')
        cmd.run(['sudo', 'ls']) # command to invoke su prompt
        self._install_homebrew()

    def _install_homebrew(self):
        if self._is_brew_installed():
            self.logger.info('brew already installed')
            return

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
            new_environ['NONINTERACTIVE'] = '1'
            os.environ.update(new_environ)
            cmd.run(['/bin/bash', tmp_path])
        finally:
            os.environ.clear()
            os.environ.update(old_environ)
        cmd.run(['rm', tmp_path])
    
    def _is_brew_installed(self):
        installed = False
        try:
            cmd.run(['brew', '-v'])
            installed = True
        except cmd.CommandRunnerError:
            pass
        return installed
    
    def install_applications(self):
        platform = self.cfg['macos']

        self.logger.info('installing brew applications')
        brew = platform['brew']
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
        casks = platform['brew_casks']
        packages = []
        if casks['all']:
            packages = casks['all']
        if self.args.personal and casks['personal']:
            packages += casks['personal']
        if self.args.work and casks['work']:
            packages += casks['work']
        if packages:
            cmd.run(['brew', 'install', '--cask'] + packages)

        if 'iterm2' in packages:
            self._add_iterm2_manual_step()

    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return

        self.logger.info('enabling sshd')
        cmd.run('sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist'.split(' '))
    
    def _add_iterm2_manual_step(self):
        manual_config.add_step('Configure iterm2 option key', 'Profile > Default > Keys > General')
        manual_config.add_step('Configure iterm2 option key', 'Left Option Key = Esc+')
        manual_config.add_step('Configure iterm2 option key', 'Profile > Default > Keys > Key Mappings')
        manual_config.add_step(
            'Configure iterm2 option key',
            'create/change option + left arrow shortcut to send escape sequence "b"')
        manual_config.add_step(
            'Configure iterm2 option key',
            'create/change option + right arrow shortcut to send escape sequence "f"')

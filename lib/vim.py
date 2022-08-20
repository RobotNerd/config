#!/usr/bin/python3
from lib.command import Cmd, CommandRunnerError
import os


class Vim:

    @staticmethod
    def vundle(logger, cfg):
        if not cfg['vundle']:
            return

        if not Vim._is_installed():
            return

        logger.info('installing vundle')

        remove_bundle_dir = 'rm -fr $HOME/.vim/bundle'
        install_vundle = 'git clone https://github.com/VundleVim/Vundle.vim.git $HOME/.vim/bundle/Vundle.vim'
        install_plugins = 'vim +PluginInstall +qall'

        Cmd.run(os.path.expandvars(remove_bundle_dir).split(' '))
        Cmd.run(os.path.expandvars(install_vundle).split(' '))
        Cmd.run(install_plugins.split(' '))

    @staticmethod
    def _is_installed():
        installed = False
        try:
            Cmd.run(f'which vim'.split(' '))
            installed = True
        except CommandRunnerError:
            pass
        return installed

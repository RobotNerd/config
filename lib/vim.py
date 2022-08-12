#!/usr/bin/python3
from lib.command import Cmd


class Vim:

    @staticmethod
    def vundle(logger, cfg):
        if not cfg['vundle']:
            return
        
        logger.info('installing vundle')
        Cmd.run('rm -fr ~/.vim/bundle'.split(' '))
        Cmd.run('git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim'.split(' '))
        Cmd.run('vim +PluginInstall +qall'.split(' '))
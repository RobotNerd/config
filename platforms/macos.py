#!/usr/bin/python3
from lib.command import Cmd


class MacOS:

    @staticmethod
    def setup(logger):
        logger.info('installing homebrew')
        Cmd.run([
            '/bin/bash',
            '-c',
            '"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        ])
    
    @staticmethod
    def install_applications(logger, args, cfg):
        logger.info('installing brew applications')
        packages = cfg['macos']['brew']['all']
        if args.personal:
            packages += cfg['macos']['brew']['personal']
        if args.work:
            packages += cfg['macos']['brew']['work']
        Cmd.run(['brew', 'install'] + packages)

        logger.info('installing brew cask applications')
        casks = cfg['macos']['brew_casks']['all']
        if args.personal:
            casks += cfg['macos']['brew_casks']['personal']
        if args.work:
            casks += cfg['macos']['brew_casks']['work']
        Cmd.run(['brew', 'install', '--cask'] + casks)

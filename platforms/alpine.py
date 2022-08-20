#!/usr/bin/python3
from lib.command import Cmd


class Alpine:

    '''Strictly for testing config changes to docker containers.'''
    
    @staticmethod
    def install_applications(logger, args, cfg):
        platform = cfg['alpine_linux']

        logger.info('install packages')
        apk = platform['apk']
        packages = apk['all']
        if args.personal:
            packages += apk['personal']
        if args.work:
            packages += apk['work']
        Cmd.run(['apk', 'add', '--no-cache'] + packages)

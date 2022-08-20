#!/usr/bin/python3
from lib.command import Cmd


class Alpine:

    '''Strictly for testing config changes to docker containers.'''

    def __init__(self, logger, args, cfg):
        self.args = args
        self.cfg = cfg
        self.logger = logger
    
    def install_applications(self):
        platform = self.cfg['alpine_linux']

        self.logger.info('install packages')
        apk = platform['apk']
        packages = []
        if apk['all']:
            packages = apk['all']
        if self.args.personal and apk['personal']:
            packages += apk['personal']
        if self.args.work and apk['work']:
            packages += apk['work']
        if packages:
            Cmd.run(['apk', 'add', '--no-cache'] + packages)
    
    def enable_sshd(self):
        if not self.cfg['ssh']['sshd_enabled']:
            return

        self.logger.info('skipping sshd enable for alpine docker container')

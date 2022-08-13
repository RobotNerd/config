#!/usr/bin/python3
from lib.command import Cmd


class Manjaro:
    
    @staticmethod
    def install_applications(logger, args, cfg):
        platform = cfg['manjaro_linux']

        logger.info('install packages')
        pacman = platform['pacman']
        packages = pacman['all']
        if args.personal:
            packages += pacman['personal']
        if args.work:
            packages += pacman['work']
        Cmd.run(['sudo', 'pacman', '-Syu', '--noconfirm'] + packages)
    
        logger.info('installing packages with snap')
        snap = platform['snap_applications']
        snap_packages = snap['all']
        if args.personal:
            snap_packages += snap['personal']
        if args.work:
            snap_packages += snap['work']
        Cmd.run(['sudo', 'snap', 'install'] + snap_packages)

        Manjaro._install_zoom(logger, cfg)
    
    @staticmethod
    def _install_zoom(logger, cfg):
        if not cfg['manjaro_linux']['zoom']['install']:
            return
        
        src = cfg['manjaro_linux']['zoom']['src']
        dst = cfg['manjaro_linux']['zoom']['dst']

        Cmd.run(f'wget {src} -O {dst}'.split(' '))
        Cmd.run(f'sudo pacman -U --noconfirm {dst}'.split(' '))

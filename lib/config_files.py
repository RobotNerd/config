#!/usr/bin/python3
from lib.backup import Backup
import os
import shutil


class ConfigFiles:

    @staticmethod
    def copy(logger, args, cfg):
        paths = cfg['config_files']['all']
        if args.personal:
            paths += cfg['config_files']['personal']
        if args.work:
            paths += cfg['config_files']['work']

        for path in paths:
            logger.info(f"copying {path['name']}")
            src = os.path.expandvars(path['src'])
            dst = os.path.expandvars(path['dst'])
            Backup.file(logger, src)
            shutil.copy(src, dst)

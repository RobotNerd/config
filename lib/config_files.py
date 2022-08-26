#!/usr/bin/python3
import os
import shutil

from lib import backup


def copy(logger, args, cfg):
    paths = cfg['config_files']['all']
    if args.personal and cfg['config_files']['personal']:
        paths += cfg['config_files']['personal']
    if args.work and cfg['config_files']['work']:
        paths += cfg['config_files']['work']

    for path in paths:
        logger.info(f"copying {path['name']}")
        src = os.path.expandvars(path['src'])
        dst = os.path.expandvars(path['dst'])
        if backup.is_needed(src, dst):
            backup.to_file(logger, dst)
        shutil.copy(src, dst)

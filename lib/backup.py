#!/usr/bin/python3
import filecmp
import os
import time


def to_file(logger, path):
    if os.path.exists(path):
        backup_path = path + f'.bkp.{round(time.time())}'
        logger.warn(f'file {path} exists.\n      Making backup: {backup_path}')
        os.rename(path, backup_path)


def is_needed(file1, file2):
    if not os.path.exists(file1):
        return False
    if not os.path.exists(file2):
        return False
    if filecmp.cmp(file1, file2):
        return False
    return True

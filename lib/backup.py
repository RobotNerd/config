#!/usr/bin/python3

import os
import time


class Backup:
    
    @staticmethod
    def file(logger, path):
        if os.path.exists(path):
            backup_path = path + f'.bkp.{round(time.time())}'
            logger.warn(f'file {path} exists.\n      Making backup: {backup_path}')
            os.rename(path, backup_path)

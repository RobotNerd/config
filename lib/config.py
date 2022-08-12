#!/usr/bin/python3

import yaml


class ConfigFileError(Exception):
    pass


class Config:

    def __init__(self, logger):
        self.logger = logger
    
    def load(self, path):
        self.logger.info('loading yaml config')
        with open(path, 'r') as file:
            cfg = yaml.safe_load(file)
        return cfg
    
    def validate_user_info(self, cfg):
        user_info = cfg.get('user_info')
        if user_info is None:
            msg = '"user_info" field is missing from config'
            self.logger.warn(msg)
            cfg['user_info']['email'] = ''
            cfg['user_info']['name'] = ''
        if not user_info['email']:
            user_info['email'] = input('enter your email address: ')
        if not user_info['name']:
            user_info['email'] = input('enter your name: ')

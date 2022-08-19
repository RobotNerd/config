#!/usr/bin/python3
from lib.command import Cmd
import os


class UnsupportedShell(Exception):
    pass


class Shell:

    @staticmethod
    def add_custom_shell_config(logger, cfg):
        rc_file = Shell._get_or_create_rc_file(logger)
        rc_custom = Shell._get_rc_custom_path(cfg)
        if Shell._contains_rc_custom_cmd(rc_file, rc_custom):
            logger.info(f'.rc_custom already referenced in {rc_file}; no changes made')
            return
        Shell._append_rc_custom_cmd(rc_file, rc_custom)
        # Cmd.run(f'source {rc_file}'.split(' '))  # TODO add step to manual output to run this `source` command

    @staticmethod
    def _get_or_create_rc_file(logger):
        shell = Shell._get_shell_name()
        if shell.endswith('bash'):
            rc_file = os.path.expandvars('$HOME/.bashrc')
        elif shell.endswith('zsh'):
            rc_file = os.path.expandvars('$HOME/.zshrc')
        elif shell.endswith('ash'):
            rc_file = os.path.expandvars('$HOME/.profile')
        else:
            raise UnsupportedShell(shell)
        
        if not os.path.exists(rc_file):
            logger.warn(f'rc file {rc_file} does not exist; creating file')
            open(rc_file, 'a').close()

        return rc_file
    
    @staticmethod
    def _get_shell_name():
        shell = os.environ.get('SHELL')
        if shell is None:
            if os.path.exists('/bin/ash'):
                shell = 'ash'
            elif os.path.exists('/bin/bash'):
                shell = 'bash'
            elif os.path.exists('/bin/zash'):
                shell = 'zsh'
        return shell
    
    @staticmethod
    def _append_rc_custom_cmd(rc_file, rc_custom):
        with open(rc_file, 'a') as file:
            file.write(f'\nsource {rc_custom}\n')
    
    @staticmethod
    def _contains_rc_custom_cmd(rc_file, rc_custom):
        custom = rc_custom.split('/')[-1]
        with open(rc_file, 'r') as file:
            text = file.read()
            if custom in text:
                return True
        return False
    
    @staticmethod
    def _get_rc_custom_path(cfg):
        path = None
        for item in cfg['config_files']['all']:
            if item['name'] == 'rc-custom':
                path = item['dst']
                break
        return path

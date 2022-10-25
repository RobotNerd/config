#!/usr/bin/python3
from lib import cmd
from lib import shell

import os


def configure(logger, cfg):
    if not cfg['configure_git_global_settings']:
        return

    logger.info('configuring git')
    base_cmd = 'git config --global'.split(' ')

    email = cfg['user_info']['email']
    name = cfg['user_info']['name']

    cmd.run(base_cmd + f'user.email {email}'.split(' '))
    cmd.run(base_cmd + ['user.name', name])
    cmd.run(base_cmd + 'pager.branch false'.split(' '))
    cmd.run(base_cmd + 'pager.diff false'.split(' '))

    _enable_tab_autocomplete(logger, cfg)

def _enable_tab_autocomplete(logger, cfg):
    shell_name = shell.get_shell_name()
    if shell_name == '/bin/ash':
        logger.warn('git auto-completion config for ash shell is test-only')
        shell.add_cmd_to_rc_custom(cfg, '# git tab autocompletion\n# not implemented for ash\n')
    elif shell_name == '/bin/bash':
        logger.warn('git auto-completion not yet implemented for bash shell')
    elif shell_name == '/bin/zsh':
        shell.add_cmd_to_rc_custom(cfg, '# git tab autocompletion\nautoload -Uz compinit && compinit\n')
    else:
        raise shell.UnsupportedShell(shell_name)

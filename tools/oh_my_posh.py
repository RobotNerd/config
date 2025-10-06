#!/usr/bin/python3
from lib import cmd
from lib import shell
import lib.manual_config as manual_config


def _update_rc_custom(cfg, theme_path):
    shell_name = shell.get_shell_name()
    oh_my_posh_rc = f'''# ohmyposh
if [ "$TERM_PROGRAM" != "Apple_Terminal" ]; then
  eval "$(oh-my-posh init {shell_name} --config {theme_path})"
fi'''
    shell.add_cmd_to_rc_custom(cfg, oh_my_posh_rc)


def install(logger, cfg):
    logger.info('Installing oh-my-posh')
    if not cfg['ohmyposh']['install']:
        return
    src = cfg['ohmyposh']['src']
    shell_name = shell.get_shell_name()
    tmp_path = '/tmp/install_oh_my_posh.sh'
    cmd.run(['curl', '-fsSL', src, '-o', tmp_path])
    cmd.run([shell_name, tmp_path])
    cmd.run(['rm', tmp_path])

    font = src = cfg['ohmyposh']['font']
    cmd.run(f'oh-my-posh font install {font}'.split(' '))
    manual_config.add_step('oh-my-posh', f'Configure terminal to use {font}')

    src = cfg['ohmyposh']['theme']['src']
    dst = cfg['ohmyposh']['theme']['dst']
    cmd.run(f'wget {src} -O {dst}'.split(' '))

    _update_rc_custom(cfg, dst)

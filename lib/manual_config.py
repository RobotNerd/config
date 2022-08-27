#!/usr/bin/python3

'''Singleton to manage list of steps that have to be done manually.'''


_steps = {}

def set_defaults(args, cfg):
    firefox = 'Add firefox browser extensions'
    add_step(firefox, 'FoxyGestures')
    add_step(firefox, 'uBlock')
    if args.personal:
        add_step(firefox, 'LastPass')

    if cfg['configure_git_global_settings']:
        git = 'Setup security keys'
        add_step(git, 'github')
    
    vscode = 'Add VS Code extensions'
    add_step(vscode, 'sort lines')
    if args.personal:
        add_step(vscode, 'vscode-viml-syntax')

    services = 'Login to services'
    add_step(services, 'GitHub')
    if args.personal:
        add_step(services, 'Dropbox')
        add_step(services, 'StackOverflow')


def to_string():
    output = '\nManual steps needed to complete configuration:\n'
    for group, steps in _steps.items():
        output += f'- {group}\n'
        for step in steps:
            output += f'  - {step}\n'
    return output

def _add_group(group):
    if group not in _steps.keys():
        _steps[group] = []

def add_step(group, step):
    _add_group(group)
    _steps[group].append(step)

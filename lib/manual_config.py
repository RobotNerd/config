#!/usr/bin/python3

'''Singleton to manage list of steps that have to be done manually.'''


_steps = {
    'Add firefox browser extensions': [
        'Lastpass',
        'uBlock',
        'Foxy Gestures (Firefox)',
    ],
    'Setup security keys': [
        'github',
    ],
    'Add VS Code extensions': [
        'vscode-viml-syntax',
        'sort lines',
    ],
    'Login to services': [
        'Dropbox',
        'GitHub',
        'StackOverflow',
    ],
}

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

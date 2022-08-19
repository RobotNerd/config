#!/usr/bin/python3

'''Singleton to manage list of steps that have to be done manually.'''


_steps = {
    'Browser extensions': [
        'Lastpass',
        'uBlock',
        'Foxy Gestures (Firefox)',
    ],
    'Setup security keys': [
        'github',
    ],
    'VS Code extensions': [
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
    output = ''
    for group, steps in _steps.values():
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

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python script that automatically applies configuration to Unix-like systems (macOS, Ubuntu, Manjaro, Alpine Linux). The script installs packages, copies config files, configures git, sets up SSH, installs vim plugins, and provides post-installation manual steps.

## Commands

### Running the Script
```bash
# Basic usage - specify platform and machine type
python3 apply-config.py <platform> [--personal] [--work]

# Examples
python3 apply-config.py macos --work
python3 apply-config.py ubuntu --personal
python3 apply-config.py manjaro --personal --work
```

### Testing
```bash
# Run unit tests
python3 -m unittest

# Manual test with Docker (Alpine Linux)
docker build -t alpine-test:test -f Dockerfile-test .
docker run -it alpine-test:test /bin/ash
python3 apply-config.py alpine_linux --personal --work --config-path ./config.yml
```

### Dependencies
```bash
pip3 install -r requirements.txt
```

## Architecture

### Entry Point
- `apply-config.py`: Main script that orchestrates configuration application
  - Parses CLI args (platform, --personal, --work, --config-path, --log-level)
  - Loads config.yml
  - Delegates to platform-specific classes
  - Shows manual configuration steps after completion

### Execution Flow (apply-config.py:33-42)
1. Platform-specific application installation
2. Copy config files (dotfiles)
3. Add custom shell config
4. Configure git global settings
5. Run vundle for vim plugins
6. Generate SSH keys
7. Enable sshd service
8. Install oh-my-posh
9. Display manual configuration steps

### Platform Implementations (`platforms/`)
Each platform class follows the same interface:
- `__init__(logger, args, cfg)`: Initialize and handle platform setup (e.g., install homebrew on macOS)
- `install_applications()`: Install packages using platform's package manager
- `enable_sshd()`: Enable SSH daemon if configured

Platform-specific package managers:
- **MacOS**: `brew` and `brew cask`
- **Ubuntu**: `apt-get`
- **Manjaro**: `pacman` and `snap`, optional zoom installer
- **Alpine**: `apk`

### Library Modules (`lib/`)
- `config.py`: Loads and validates config.yml, prompts for missing user info
- `config_files.py`: Copies dotfiles from config-files/ to user's home directory
- `git.py`: Runs `git config --global` commands
- `ssh.py`: Generates SSH keys using ssh-keygen
- `vim.py`: Installs vim plugins via vundle
- `shell.py`: Adds custom shell configuration
- `cmd.py`: Command runner utility
- `backup.py`: Backs up existing files before overwriting
- `logger.py`: Logging utility with color-coded output
- `manual_config.py`: Singleton that tracks manual steps users must complete (browser extensions, service logins, etc.)

### Configuration (`config.yml`)
Structured with platform-specific sections and `all`/`personal`/`work` subdivisions:
- `user_info`: Name and email for git configuration
- `configure_git_global_settings`: Boolean to enable git config
- `ssh`: SSH key generation settings and sshd enablement
- `vundle`: Boolean to install vim plugins
- `ohmyposh`: Oh My Posh installation settings
- `config_files`: Lists dotfiles to copy (all/personal/work)
- Platform sections (e.g., `macos`, `ubuntu`): Package lists organized by all/personal/work

### Tools (`tools/`)
- `oh_my_posh.py`: Installs oh-my-posh shell prompt customization

### Config Files (`config-files/`)
Dotfiles that get copied to the system:
- `rc-custom`: Custom shell configuration
- `tmux.conf`: tmux configuration
- `vimrc`: vim configuration
- `nethackrc`: NetHack configuration (personal only)
- `ublock-origin-filters.txt`: uBlock Origin filters

## Development Notes

- The script requires sudo privileges for package installation
- Platform classes may add manual configuration steps via `manual_config.add_step()`
- The test config is at `test/config.yml` for unit testing
- When adding a new platform, create a class in `platforms/` implementing the standard interface
- Config validation happens at load time; missing user_info prompts for input

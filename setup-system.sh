#!/usr/bin/env bash

set -e

source ./scripts/global-apps.sh
source ./scripts/personal-apps.sh
source ./scripts/messaging.sh

skip_custom_actions=''
skip_package_manager=''
skip_sshd=''
skip_user_details=''
skip_vundle=''
target=''
work_only=''

CFG_PATH='./config-files'

print_usage() {
  echo "Command usage:"
  echo "  setup-system.sh -t TARGET"
  echo
  echo "  -t TARGET : name of the local *.sh file for the target platform"
  echo "  -a        : skip platform-specific actions"
  echo "  -p        : skip package manager application install"
  echo "  -s        : skip starting sshd"
  echo "  -u        : skip entry of user details"
  echo "  -v        : skip vundle install"
  echo "  -w        : install on a work machine and skip personal applications"
  exit 0
}

while getopts 'apst:uvw' flag; do
  case "${flag}" in
    a) skip_custom_actions='true' ;;
    p) skip_package_manager='true' ;;
    s) skip_sshd='true' ;;
    t) target="${OPTARG}" ;;
    u) skip_user_details='true' ;;
    v) skip_vundle='true' ;;
    w) work_only='true' ;;
    *) print_usage
       exit 1 ;;
  esac
done

# Load the target specific configuration.
if [ "$target" == '' ]; then
  print_usage
  exit 1
fi
source ./$target

# Get user inputs needed by the script.
if [ "$skip_user_details" != 'true' ]; then
  echo -n "Enter your name: "
  read USERNAME
  echo -n "Enter your email: "
  read EMAIL
fi

# Execute any custom setup specific to the target platform.
if [ "$skip_custom_actions" != 'true' ]; then
  custom_setup
fi

# Concatenate app names into single string
all=""
if [ "$work_only" == 'true' ]; then
  APPS=("${GLOBAL_APPS[@]}" "${DISTRO_APPS[@]}")
else
  APPS=("${GLOBAL_APPS[@]}" "${PERSONAL_APPS[@]}" "${DISTRO_APPS[@]}")
fi
for i in "${APPS[@]}"
do
  all+=" $i"
done

if [ "$skip_package_manager" != 'true' ]; then
  info "Installing applications with pacman"
  eval "sudo $PKG_MGR $all"
fi

if [ ! -f "$HOME/.gitconfig" ]; then
  info "Configuring git"
  git config --global user.email $EMAIL
  git config --global user.name $USERNAME
  git config --global pager.branch false
  git config --global pager.diff false
fi

info "Copying config files from github"
cp $CFG_PATH/nethackrc $HOME/.nethackrc
cp $CFG_PATH/tmux.conf $HOME/.tmux.conf
cp $CFG_PATH/vimrc $HOME/.vimrc

source ./scripts/shell-config.sh

if [ "$skip_vundle" != 'true' ]; then
  # Vundle setup for vim
  # See: https://github.com/VundleVim/Vundle.vim
  rm -fr ~/.vim/bundle
  git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
  vim +PluginInstall +qall
fi

SSH_KEY="$HOME/.ssh/id_ed25519"
if [ ! -f "$SSH_KEY" ]; then
  info "Generate ssh key"
  ssh-keygen -t ed25519 -C $EMAIL
fi

# Enable ssh server
if [ "$skip_sshd" != 'true' ]; then
  sudo systemctl enable sshd
  sudo systemctl start sshd
fi

# Execute any custom actions specific to the target platform.
if [ "$skip_custom_actions" != 'true' ]; then
  custom_actions
  custom_teardown
fi

# Print out list of manual tasks
echo
info "Manual setup checklist"
echo "- Browser extensions"
echo "  - Lastpass"
echo "  - uBlock"
echo "  - Foxy Gestures (Firefox)"
echo "- Setup security keys"
echo "  - github"
echo "- VS Code extensions"
echo "  - vscode-viml-syntax"
echo "  - sort lines"
echo "- Login to services"
echo "  - Dropbox"
echo "  - GitHub"
echo "  - StackOverflow"

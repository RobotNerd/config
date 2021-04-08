#!/usr/bin/bash

set -e

source global-apps.sh
source messaging.sh

skip_custom_actions=''
skip_package_manager=''
skip_vundle=''
target=''

print_usage() {
  echo "Command usage:"
  echo "  setup-system.sh -t TARGET"
  echo
  echo "  -t TARGET : name of the local *.sh file for the target platform"
  echo "  -a        : skip platform-specific actions"
  echo "  -p        : skip package manager application install"
  echo "  -v        : skip vundle install"
  exit 0
}

while getopts 'apt:v' flag; do
  case "${flag}" in
    a) skip_custom_actions='true' ;;
    p) skip_package_manager='true' ;;
    t) target="${OPTARG}" ;;
    v) skip_vundle='true' ;;
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

# Execute any custom setup specific to the target platform.
if [ "$skip_custom_actions" != 'true' ]; then
  custom_setup
fi

# Concatenate app names into single string
all=""
APPS=("${GLOBAL_APPS[@]}" "${DISTRO_APPS[@]}")
for i in "${APPS[@]}"
do
  all+=" $i"
done

if [ "$skip_package_manager" != 'true' ]; then
  info "Installing applications with pacman"
  eval "sudo $PKG_MGR $all"
fi

info "Copying config files from github"
cp ./nethackrc $HOME/.nethackrc
cp ./tmux.conf $HOME/.tmux.conf
cp ./vimrc $HOME/.vimrc

BASHRC_CMD="source $HOME/.bashrc-custom"
if ! grep -qe "$BASHRC_CMD" "$HOME/.bashrc"; then
  info "Appending bashrc config from github to .bashrc"
  cp ./bashrc $HOME/.bashrc-custom
  cp $HOME/.bashrc $HOME/bkp.bashrc
  echo -e "\n$BASHRC_CMD" >> $HOME/.bashrc
  source $HOME/.bashrc
fi

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
  ssh-keygen -t ed25519 -C "marshall.bowles@gmail.com"
fi

# Enable ssh server
sudo systemctl enable sshd
sudo systemctl start sshd

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
echo "- Setup security keys"
echo "  - github"
echo "- VS Code extensions"
echo "  - vscode-viml-syntax"
echo "- Login to services"
echo "  - Dropbox"
echo "  - GitHub"
echo "  - StackOverflow"

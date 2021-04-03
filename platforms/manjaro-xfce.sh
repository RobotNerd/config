#!/usr/bin/bash

# Install apps
declare -a DISTRO_APPS=(
  redshift
  the_silver_searcher
)

declare -a SNAP_APPS=(
  "code --classic"
)

PKG_MGR="pacman -Syu --noconfirm"

custom_setup() {
  :
}

custom_actions() {
  # install applications with snap
  for i in "${SNAP_APPS[@]}"
  do
    sudo snap install $i
  done
}

custom_teardown() {
  # No action
  :
}

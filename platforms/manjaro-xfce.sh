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
  # install snap package manager for installing some applications
  # from: https://wiki.manjaro.org/index.php/Snap
  #eval "$PKG_MGR snapd"
  #systemctl enable --now snapd.socket
  #ln -s /var/lib/snapd/snap /snap
  :
}

custom_actions() {
  # install applications with snap
  for i in "${SNAP_APPS[@]}"
  do
    eval "snap install $i"
  done
}

custom_teardown() {
  # No action
  :
}

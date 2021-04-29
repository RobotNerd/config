#!/usr/bin/bash

OS="linux"

# Install apps
declare -a DISTRO_APPS=(
  gimp
  inkscape
  redshift
)

declare -a SNAP_APPS=(
  "code --classic"    # Visual Studio Code
  "slack --classic"
)

PKG_MGR="pacman -Syu --noconfirm"
REDSHIFT_PATH=$HOME/.config/redshift/redshift.conf
ZOOM_PKG=zoom_x86_64.pkg.tar.xz
ZOOM_LOCAL=$HOME/Downloads/$ZOOM_PKG
ZOOM_URI=https://zoom.us/client/latest/$ZOOM_PKG

custom_setup() {
  :
}

custom_actions() {
  # install applications with snap
  for i in "${SNAP_APPS[@]}"
  do
    sudo snap install $i
  done

  cp $CFG_PATH/redshift.conf $REDSHIFT_PATH

  # Download and install Zoom
  if [ ! -f "$ZOOM_LOCAL" ]; then
    wget $ZOOM_URI -O $ZOOM_LOCAL
    sudo pacman -U --noconfirm $ZOOM_LOCAL
  fi
}

custom_teardown() {
  # No action
  :
}

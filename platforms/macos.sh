#!/usr/bin/bash

OS="mac"

# Applications to install
declare -a DISTRO_APPS=()

# These must be installed with the --cast flag.
declare -a BREW_CASK_APPS=(
  google-chrome
  firefox
  gimp
  inkscape
  iterm2
  slack
  visual-studio-code
  zoom
)

PKG_MGR="brew install"
PKG_MGR_CASK="brew install --cask"

custom_setup() {
  # install homebrew
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
}

custom_actions() {
  if [ "$skip_package_manager" != 'true' ]; then
    info "Install brew casks"

    # Concatenate macos appliation names installed as brew casks.
    cask_app_names=""
    for i in "${BREW_CASK_APPS[@]}"
    do
      cask_app_names+=" $i"
    done

    eval "$PKG_MGR_CASK $cask_app_names"
  fi
}

custom_teardown() {
  :  # No action
}

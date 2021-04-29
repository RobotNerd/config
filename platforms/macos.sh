#!/usr/bin/bash

# Install apps
declare -a DISTRO_APPS=(
  the_silver_searcher
  "--cask google-chrome"
  "--cask firefox"
  "--cask gimp"
  "--cask inkscape"
  "--cask iterm2"
  "--cask slack"
  "--cask visual-studio-code"
  "--cask zoom"
)

PKG_MGR="brew install"

custom_setup() {
  # install homebrew
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
}

custom_actions() {
  :  # No action
}

custom_teardown() {
  :  # No action
}

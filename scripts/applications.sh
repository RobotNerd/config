# Applications installed on all systems.
declare -a GLOBAL_APPS=(
  docker
  git
  the_silver_searcher
  tmux
  vim
)

# Applications installed on personal devices.
declare -a PERSONAL_APPS=(
  nethack
  openssh
  veracrypt
)

function install_apps () {
  info "Installing applications with $PKG_MGR"

  # Concatenate application names into single string
  all_app_names=""
  if [ "$work_only" == "true" ]; then
    APPS=("${GLOBAL_APPS[@]}" "${DISTRO_APPS[@]}")
  else
    APPS=("${GLOBAL_APPS[@]}" "${PERSONAL_APPS[@]}" "${DISTRO_APPS[@]}")
  fi

  for i in "${APPS[@]}"
  do
    all_app_names+=" $i"
  done

  # Install applications
  case "$OS" in
    mac)
      eval "$PKG_MGR $all_app_names"
    ;;
    linux)
      eval "sudo $PKG_MGR $all_app_names"
    ;;
  esac
}
SHELL_CMD="source $HOME/.rc-custom"

case "$SHELL" in
  *bash*) SHELL_CFG="$HOME/.bashrc" ;;
  *zsh*) SHELL_CFG="$HOME/.zshrc" ;;
esac

if ! grep -qe "$SHELL_CMD" "$SHELL_CFG"; then
  info "Appending rc-custom config from github to $SHELL_CFG"
  cp $CFG_PATH/rc-custom $HOME/.rc-custom
  cp $SHELL_CFG $SHELL_CFG.bkp
  echo -e "\n$SHELL_CMD" >> $SHELL_CFG
  source $SHELL_CFG
fi
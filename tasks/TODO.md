# TODO

## mac

- Add command to allow applications from anywhere
  ```sh
  sudo spctl --master-disable
  ```

- Add iterm2 light/dark mode script.

## bugs

- Reconcile CLI platform names with `config.yml` section keys. `platforms/manjaro.py:14`
  reads `cfg['manjaro_linux']` and `platforms/alpine.py:15` reads `cfg['alpine_linux']`,
  but `config.yml` declares `manjaro` and has no alpine section. Only `macos` and `ubuntu`
  currently run: `manjaro` raises `KeyError: 'manjaro_linux'`, `alpine` raises
  `PlatformConfigMissing`, and `alpine_linux` raises `UnrecognizedPlatform` — which breaks
  the docker test flow, since `test/config.yml` uses the `alpine_linux` key.

- Fix snap install in `platforms/manjaro.py:29-30`. `snap = platform['snap_applications']`
  is immediately overwritten by `snap = []`, so `snap['all']` raises `TypeError`.
  `snap_packages` is also only bound inside the first `if`, so it can be unbound at line 37.

- Decide on the minimum python version. The f-string at `platforms/ubuntu.py:30` nests `'`
  inside a `'...'` literal (PEP 701), making 3.12+ a hard requirement and a `SyntaxError`
  on older interpreters. Either rewrite the string or document the floor.

- Add the missing `ohmyposh` key to `test/config.yml`. `tools/oh_my_posh.py:18`
  dereferences `cfg['ohmyposh']['install']` unconditionally, so the docker test dies with
  a `KeyError` at the last step of the pipeline.

- Expand `$HOME` in `tools/oh_my_posh.py`. `theme.dst` (`$HOME/.poshthemes/`) goes straight
  to `wget -P` with no shell to expand it, creating a literal `./$HOME/` directory.
  `_update_rc_custom` also passes that directory as oh-my-posh's `--config`, which expects
  the `.omp.json` file itself.

- Make `shell.add_cmd_to_rc_custom` (`lib/shell.py:21`) idempotent. It appends without a
  containment check, unlike `add_custom_shell_config`, so re-running the script duplicates
  the git-autocomplete and oh-my-posh blocks in `~/.rc-custom`.

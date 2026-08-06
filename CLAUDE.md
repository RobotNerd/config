# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status: v2 refactor planned

A ground-up refactor is specified in **`docs/DESIGN.md`**, with the rules to follow in
**`docs/CONVENTIONS.md`** and sequenced, ID'd work in **`tasks/TODO.md`**. Read those
first — the sections below describe the **current (v1)** code, which v2 replaces.

Headline v2 changes: zero runtime dependencies (`config.yml` → `config.toml` via stdlib
`tomllib`, no colorama), a plan/apply split that makes idempotence and dry-run structural,
first-class Windows 11 support, a stdlib ANSI TUI, and golden-file plan tests. manjaro and
alpine are deprecated.

## Project Overview

A Python script that applies personal machine configuration to Unix-like systems:
installs packages via the platform's package manager, copies dotfiles into `$HOME`,
configures git and SSH, and installs vim plugins and oh-my-posh. Steps that can't be
automated are collected during the run and printed as a manual checklist at the end.

## Commands

```bash
pip3 install -r requirements.txt          # colorama, pyyaml

python3 apply-config.py macos --work
python3 apply-config.py ubuntu --personal --work
```

`--personal` and `--work` are independent flags and may be combined; see the
all/personal/work convention below. Also `--config-path` (default `./config.yml`) and
`--log-level {info,warn,error}`.

Only `macos` and `ubuntu` run to completion today — see [Known breakage](#known-breakage).

### Tests

```bash
python3 -m unittest                                            # discovery, 3 tests
python3 -m unittest test.test_backup.TestBackup.test_backup_file   # single test
```

Run from the repo root: `test/data.py` hardcodes the relative path `./unittest_data`,
and `data.reset()` does `shutil.rmtree` on it.

### Manual test in Docker

`Dockerfile-test` copies the repo into an Alpine image and overwrites `config.yml` with
`test/config.yml`.

```bash
docker build -t alpine-test:test -f Dockerfile-test .
docker run -it alpine-test:test /bin/ash
python3 apply-config.py alpine_linux --personal --work --config-path ./config.yml
```

This flow is currently broken — see [Known breakage](#known-breakage) items 1 and 4.
Add `--platform linux/amd64` to `docker run` on Apple Silicon.

## Architecture

`apply_changes` (`apply-config.py:33-42`) is the whole program — a fixed, unconditional
nine-step pipeline. Each step decides for itself whether it's a no-op by checking its own
config flag and returning early (e.g. `lib/vim.py:8`, `lib/ssh.py:9`, `lib/git.py:9`).
There is no dependency graph and no resume; a raised exception aborts the run partway.

The step order carries real constraints:

1. `platform.install_applications()`
2. `config_files.copy` — writes `rc-custom` to its `dst`, which later steps append to.
3. `shell.add_custom_shell_config` — resolves that `dst` back out of the config
   (`lib/shell.py:71 _get_rc_custom_path`, matching on `name == 'rc-custom'`) and sources
   it from the user's real rc file.
4. `git.configure`, then 5. `vim.vundle`, 6. `ssh.generate_key`, 7. `platform.enable_sshd()`,
   8. `oh_my_posh.install` — steps 4 and 8 append shell snippets into `rc-custom`, so they
   must follow step 2.
9. `show_manual_steps()` prints the accumulated checklist.

So: anything that appends to `rc-custom` must be sequenced after `config_files.copy`, and
`rc-custom` must stay in the `config_files.all` list under exactly the name `rc-custom`.

### Platform classes (`platforms/`)

Duck-typed, no base class or ABC. `get_platform` (`apply-config.py:45-57`) maps the CLI
string to one of four classes; each implements:

- `__init__(logger, args, cfg)` — **does side-effectful setup**, not just assignment.
  macOS/Ubuntu/Manjaro run `cmd.run(['sudo', 'ls'])` here purely to trigger the sudo
  password prompt up front; macOS additionally downloads and runs the Homebrew installer
  with `NONINTERACTIVE=1` (`platforms/macos.py:18-44`).
- `install_applications()` — merges package lists and shells out to the package manager
  (`brew` + `brew --cask`, `apt-get`, `pacman` + `snap`, `apk`).
- `enable_sshd()` — early-returns unless `cfg['ssh']['sshd_enabled']`; `launchctl` on
  macOS, `systemctl` on Linux, no-op on Alpine.

`platforms/alpine.py` is explicitly test-only (docstring, line 7): no sudo, no sshd.

## Cross-cutting conventions

**all/personal/work merge.** Duplicated verbatim at five call sites —
`lib/config_files.py:9-13` and once per package manager in each platform's
`install_applications`:

```python
packages = []
if group['all']:
    packages = group['all']
if self.args.personal and group['personal']:
    packages += group['personal']
if self.args.work and group['work']:
    packages += group['work']
```

Two things to know: the `all` branch **aliases** rather than copies, so the subsequent
`+=` mutates the list inside the loaded config dict in place; and every group needs its
`all`/`personal`/`work` subkeys present even when empty (a missing key is a `KeyError`, an
empty one yields `None`, which the truthiness checks handle).

**`lib/cmd.py` — no shell.** `subprocess.run(cmd)` with a list and **no** `shell=True`.
Globs, pipes, redirects, and `$VAR` do not expand; a non-zero exit raises
`CommandRunnerError` carrying stderr. Output is captured and discarded on success.

The codebase builds argv with `'some command'.split(' ')`, which breaks on any value
containing a space — `lib/git.py:19` already special-cases `user.name` as an explicit list
for exactly this reason. Prefer a list literal when interpolating config values.

Because there's no shell, `$HOME`-style paths from `config.yml` must be run through
`os.path.expandvars` before use. Most call sites do (`lib/config_files.py:17-18`,
`lib/ssh.py:13`, `lib/vim.py:20-21`); `tools/oh_my_posh.py` does not — see breakage 5.

**`lib/manual_config.py` — module-level singleton.** A bare module dict `_steps`, no class.
Imported inconsistently as both `from lib import manual_config` and
`import lib.manual_config as manual_config`; both bind the same module object, so it works.
Any code that needs human follow-up calls `manual_config.add_step(group, step)` from
wherever it is — platform classes, `lib/shell.py`, `tools/oh_my_posh.py` all do.
`set_defaults` (`apply-config.py:108`) seeds the args/config-dependent baseline before the
pipeline runs.

**`lib/backup.py` — before destructive writes.** Steps that overwrite user files call
`backup.to_file` first, renaming any existing file to `<path>.bkp.<epoch>`
(`lib/config_files.py:19-20`, `lib/ssh.py:14`). `backup.is_needed` skips the backup when
source and destination already compare equal.

**Idempotence is uneven.** `shell.add_custom_shell_config` guards against re-adding its
`source` line (`lib/shell.py:14`), but `shell.add_cmd_to_rc_custom` (line 21) appends
unconditionally — so re-running the script duplicates the git-autocomplete and oh-my-posh
blocks inside `~/.rc-custom`.

## Known breakage

Verified by reading the code; **not** yet fixed. Also tracked in `tasks/TODO.md`.

1. **CLI platform names and config keys have drifted apart.** `platforms/manjaro.py:14`
   reads `cfg['manjaro_linux']` and `platforms/alpine.py:15` reads `cfg['alpine_linux']`,
   but `config.yml` declares `manjaro` and has no alpine section at all. `verify_platform_exists`
   (`apply-config.py:95`) checks the *CLI string* against the config, while `get_platform`
   accepts only `macos|manjaro|alpine|ubuntu` (the argparse positional itself is an
   unconstrained `str` — there is no `choices`). Net result:
   - `macos`, `ubuntu` → work
   - `manjaro` → passes validation, then `KeyError: 'manjaro_linux'`
   - `alpine` → `PlatformConfigMissing`
   - `alpine_linux` → `UnrecognizedPlatform`, including in the Docker flow, where
     `test/config.yml` (which *does* use the `alpine_linux` key) becomes `config.yml`
2. **`platforms/manjaro.py:29-30`** — `snap = platform['snap_applications']` is immediately
   overwritten by `snap = []`, so `snap['all']` raises `TypeError`. `snap_packages` is also
   only bound inside the first `if`, so it can be unbound at line 37.
3. **`platforms/ubuntu.py:30`** — the f-string nests `'` inside a `'…'` literal, which is
   PEP 701 syntax. This makes **Python 3.12+ a hard requirement**; the file is a
   `SyntaxError` on anything older.
4. **`test/config.yml` has no `ohmyposh` key**, but `tools/oh_my_posh.py:18` dereferences
   `cfg['ohmyposh']['install']` unconditionally → `KeyError` at pipeline step 8 of the
   Docker test.
5. **`tools/oh_my_posh.py` never expands `$HOME`.** `theme.dst` is `$HOME/.poshthemes/`
   and is passed straight to `wget -P` and into the `rc-custom` snippet. With no shell to
   expand it, `wget` creates a literal `./$HOME/` directory. `_update_rc_custom` also
   passes the theme *directory* as oh-my-posh's `--config`, which expects the `.omp.json`
   file.

## Adding to the config

**A package:** add it to the right platform section's `all`/`personal`/`work` list in
`config.yml`, using that package manager's exact name. Nothing in code needs to change.

**A platform:** add a class in `platforms/` implementing the three-method contract above,
add a branch to `get_platform`, and — critically — **name the `config.yml` top-level
section exactly the same string the CLI accepts.** That mismatch is the root cause of
breakage 1. Include all three of `all`/`personal`/`work` even if empty. Mirror the section
into `test/config.yml` if it should be reachable from the Docker flow.

**A manual follow-up step:** call `manual_config.add_step(group, step)` at the point the
need is detected; grouping strings are free-form and become the checklist headings.

## Repo facts

- No linter, formatter, type checker, or CI is configured. Tests are stdlib `unittest`,
  with only `lib/backup.py` and `lib/cmd.py` covered.
- Python 3.12+ (see breakage 3). Runtime deps are just `colorama` and `pyyaml`.
- `config.yml` is committed with `user_info` as `'TODO'`; `lib/config.py:4,30-33` treats
  `TODO` as a placeholder and interactively prompts for name and email.
- Recent history uses Conventional Commit prefixes (`feat:`) but it isn't enforced, and
  older commits don't. Note the default branch for PRs is `master`.
- `scripts/` (`nanowrimo`, `prz-count`) are standalone shell utilities unrelated to the
  config pipeline.

# TODO

Work queue for the v2 refactor described in `docs/DESIGN.md`. Read
`docs/CONVENTIONS.md` before changing code.

**How to use this file with an LLM:** task IDs are stable — say "implement T4" and
the session has everything it needs. Each task lists its dependencies and
acceptance criteria, so "done" is checkable rather than asserted. One task per
session where possible; they're sized to fit. When a task is done, check it off and
move it to `## Done` at the bottom with a one-line note. Add new work as `T<n+1>`
and never renumber existing IDs.

Legend: `[ ]` todo · `[~]` in progress · `[x]` done · **blocked by** = do those first

---

## P0 — foundation (unblocks everything else)

- [ ] **T1 · Skeleton + Action/Context/Probe.**
  Create `apply.py`, `lib/{actions,context,probe,planner,executor}.py`,
  `lib/steps/__init__.py`, `docs/`, `tests/`. Define frozen `Action`, `Context`,
  the `Probe` Protocol, and both `RealProbe` (caching) and `FakeProbe`.
  Empty `STEPS` registry. No steps yet.
  *Accept:* `python3 apply.py plan` runs and prints an empty plan; `python3 -m unittest`
  passes from two different cwds.

- [ ] **T2 · 3.9-safe entry point + version gate.**
  `apply.py` parses under 3.9. First real statement checks `sys.version_info` and,
  under 3.11, prints per-OS remediation and exits non-zero — no traceback.
  Subcommands `plan|apply|tui|bootstrap`, flags `--platform --personal --work
  --only --dry-run --explain`.
  **blocked by** T1.
  *Accept:* `python3.9 apply.py` prints the gate message, not a `SyntaxError`;
  `python3 apply.py --help` lists all subcommands.

- [ ] **T3 · `config.toml` schema + loader.**
  Port `config.yml` to the tool-centric schema in `docs/DESIGN.md`. Loader uses
  `tomllib`, validates, and **rejects unknown keys** with a message naming the key
  (typos in an LLM-authored config must fail loudly, not silently skip). Drop
  manjaro and alpine entries. Prompt for empty `user.name`/`user.email`.
  **blocked by** T1.
  *Accept:* unit tests for scope/platform resolution and for each rejection case;
  no `pyyaml` import remains.

- [ ] **T4 · Executor.**
  The only mutating module. Tuple `argv` (never `shell=True`), streamed output,
  `--dry-run`, one-shot root acquisition (`sudo` on Unix, elevation check on
  Windows), stop-and-report on failure.
  **blocked by** T1.
  *Accept:* a fake runner test asserts no `shell=True` and that dry-run executes
  nothing; a failing action exits non-zero with the remaining plan printed.

## P1 — steps (port v1 behavior onto the new architecture)

Each: pure planner, `FakeProbe` unit tests, registered in `STEPS`. All **blocked
by** T1–T4.

- [ ] **T5 · `packages` step + brew/apt/winget providers.**
  Resolve tools → provider argv. One batched query per run for installed state, not
  one per package. Handles `{cask = "..."}` inline tables.
  *Accept:* second run yields zero install actions; a tool absent for a platform
  produces nothing there.

- [ ] **T6 · `dotfiles` step.**
  Hash-compare src vs dst, back up before overwrite, unified diff in `--explain`.
  Per-platform `dst` (`~/.vimrc` vs `~/_vimrc`).
  *Accept:* unchanged file → no action; changed → one copy action plus a backup.

- [ ] **T7 · `shell_profile` step + sentinel rewriting.**
  Split `rc-custom` into `files/shell/common.sh` + `macos.sh` + `ubuntu.sh` +
  `profile.ps1`. Append one guarded block to the real rc file; rewrite between
  sentinels rather than appending. **Fixes the v1 duplication bug directly.**
  Also fix the payload bugs: `ls -G --color` (`-G` = colorize on BSD, suppress-group
  on GNU — split per platform), `./` on `PATH`, and `guf` hardcoding `master`.
  *Accept:* running the planner twice against a file already containing the block
  yields zero actions.

- [ ] **T8 · `git_config` step.**
  Diff `git config --global --get` against desired settings; emit only differing
  keys. `user.name` passed as a list element, never `.split(" ")`.
  *Accept:* a name containing a space round-trips correctly; matching config → no
  actions.

- [ ] **T9 · `ssh_keys` + `services` steps.**
  Keygen only when the keyfile is absent (v1 regenerated and backed up every run).
  sshd enable per platform: `launchctl` / `systemctl` / Windows service.
  *Accept:* existing key → zero actions.

- [ ] **T10 · `prompt` + `fonts` steps (oh-my-posh).**
  Rewrite `tools/oh_my_posh.py`. **Fixes three v1 bugs:** expand `~` in Python;
  point `--config` at the `.omp.json` *file*, not its directory; make the rc-file
  edit idempotent via T7's sentinels.
  *Accept:* theme path in the generated snippet is absolute and points to a file.

## P2 — TUI

- [ ] **T11 · `lib/term.py`.**
  Raw-mode keyreads (`termios`/`tty` on Unix, `msvcrt` on Windows), ANSI helpers,
  Windows VT enable via `ctypes`. Terminal restored on exit, exception, and
  `SIGINT`. Replaces colorama.
  **blocked by** T1.
  *Accept:* Ctrl-C mid-read leaves a usable terminal; non-tty is detected.

- [ ] **T12 · `lib/tui.py` — the interactive flow.**
  Six screens per `docs/DESIGN.md`: detect/confirm → step list → drill-down → confirm
  → apply w/ live progress → manual steps. Steps with an empty plan render as
  `up to date`. Non-tty falls back to explicit flags.
  **blocked by** T5–T11.
  *Accept:* full run on macOS and Ubuntu terminals; `apply.py tui < /dev/null`
  doesn't hang.

## P3 — testing

- [ ] **T13 · Delete v1 tests; add real planner tests.**
  Remove `test/test_cmd.py` (asserts `assertTrue(True)`) and `test/test_backup.py`
  (cwd-dependent, `rmtree`s a real directory). Every planner gets `FakeProbe`
  tests: no-op-when-applied, correct-delta-when-not, skipped-when-out-of-scope.
  Temp dirs, never cwd-relative.
  **blocked by** T5–T10.
  *Accept:* `python3 -m unittest` passes from any cwd and touches nothing outside
  a temp dir.

- [ ] **T14 · Golden plan tests.**
  Deterministic plan rendering for all 9 (platform × scope) combos into
  `tests/golden/`, with `--update-golden`. Sort output; inject the clock.
  **blocked by** T13.
  *Accept:* adding a tool to `config.toml` shows up as a one-line golden diff in
  exactly the affected platforms.

- [ ] **T15 · Optional `ubuntu:24.04` container smoke test.**
  Replaces `Dockerfile-test`. Real end-to-end run, then a second run asserting the
  plan is empty — **idempotence verified for real, not just unit-tested.**
  **blocked by** T5–T10.
  *Accept:* documented one-liner; second run reports no actions.

## P4 — platform completion and cleanup

- [ ] **T16 · Windows 11 support.**
  winget provider, PowerShell `$PROFILE`, `%USERPROFILE%` dotfiles, built-in
  OpenSSH keygen, elevation instead of sudo.
  **blocked by** T5–T10.
  *Accept:* plan renders on Windows; dotfiles land in the right place; no `sudo`
  anywhere in the Windows path.

- [ ] **T17 · macOS bootstrap subcommand.**
  `apply.py bootstrap` on stock 3.9: install Homebrew (`NONINTERACTIVE=1`) and
  `python@3.13`, then instruct re-run. Reads no config, so needs no TOML.
  **blocked by** T2.
  *Accept:* runs to completion under `/usr/bin/python3` on a machine without brew.

- [ ] **T18 · Delete v1.**
  Remove `platforms/` (incl. broken manjaro/alpine), `lib/` v1 modules, `tools/`,
  `config.yml`, `requirements.txt`, `Dockerfile-test`, `unittest_data/`, `test/`.
  Add `.gitignore` entries. Update `README.md` and `CLAUDE.md` to describe v2 and
  point at `docs/DESIGN.md` instead of restating it.
  **blocked by** T1–T17.
  *Accept:* no import of `yaml` or `colorama` anywhere; README commands all run.

## Backlog — not scheduled

- [ ] **T19 · `apply.py doctor`** — diagnose a machine (python version, provider
  present, PATH sanity) without planning.
- [ ] **T20 · Uninstall/revert** — sentinels already make shell edits removable;
  extend to dotfiles via the `.bkp.` backups.
- [ ] **T21 · Secrets/identity split** — work vs personal git identity per
  directory (`includeIf gitdir:`), so one machine can hold both.
- [ ] **T22 · macOS `defaults` step** — keyboard repeat, Dock, screenshot location.
  Absorbs the old "allow apps from anywhere" note (modern equivalent of
  `spctl --master-disable`, which is removed on current macOS).
- [ ] **T23 · iTerm2 light/dark script** — carried over from v1's TODO.
- [ ] **T24 · Extension lists as config** — VS Code and Firefox extensions are
  currently hardcoded manual steps in `lib/manual_config.py`; VS Code's are
  installable via `code --install-extension`.

---

## v1 bugs

All are **resolved structurally by v2**, not patched in place — recorded here so the
fix is verifiable and nothing is silently lost. Do not spend time fixing v1 except
for T0.

- [ ] **T0 · Stopgap: unbreak `manjaro` in v1** — *only if you need that machine
  before v2 lands; otherwise close as won't-fix with T18.* One-line key fix plus
  the `snap` shadowing.

| v1 bug | Location | Resolved by |
| - | - | - |
| CLI platform name ≠ config key; only `macos`/`ubuntu` ran | `platforms/manjaro.py:14`, `platforms/alpine.py:15` | T3 + T18 (single name, one registry) |
| `snap = []` shadows the config read → `TypeError`; `snap_packages` possibly unbound | `platforms/manjaro.py:29-30` | T18 (manjaro deleted) |
| PEP 701 f-string made the tool silently 3.12-only | `platforms/ubuntu.py:30` | T2 (explicit gate) |
| `test/config.yml` missing `ohmyposh` → `KeyError` | `test/config.yml` | T3 (validated schema) |
| `$HOME` never expanded → literal `./$HOME/` dir; `--config` given a dir not a file | `tools/oh_my_posh.py` | T10 |
| `add_cmd_to_rc_custom` appends unguarded → duplicate blocks on re-run | `lib/shell.py:21` | T7 (sentinels) |
| Bootstrap paradox: needs `pip install` that PEP 668 refuses | `requirements.txt` | T3 + T17 (zero-dep) |
| SSH key regenerated every run | `lib/ssh.py` | T9 |

## Done

- [x] Rewrote `CLAUDE.md` as an architecture doc; recorded the v1 bug inventory;
  fixed stale platform names in `README.md`.

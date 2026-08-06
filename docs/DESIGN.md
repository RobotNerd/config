# Design: config v2

Target-state architecture for this repo. Written as a spec to implement against;
once implemented it becomes the living architecture doc. Sequenced work lives in
`tasks/TODO.md`. Read `docs/CONVENTIONS.md` before changing code.

## Why v2

The tool's job is to configure a machine from scratch, but v1 cannot run on a
scratch machine, and its structure resists the three properties we actually want.

**Bootstrap paradox.** v1 needs `pip3 install pyyaml colorama` before it can do
anything. On Ubuntu 24.04 and Homebrew Python that install is refused outright by
PEP 668 (`EXTERNALLY-MANAGED`). So the tool requires exactly the bootstrapping it
exists to perform.

**Not idempotent.** Re-running duplicates shell config
(`lib/shell.py:21 add_cmd_to_rc_custom` appends with no containment check) and
re-runs every package install unconditionally. There is no way to preview.

**Adding a tool touches many places.** Package lists are nested
platform → manager → scope, so one tool spans N edits across N platforms, and
nothing ties "ripgrep on mac" to "ripgrep on windows" as one concept.

**Nothing that decides behavior is tested.** All 762 lines shell out immediately,
so the merge logic, platform dispatch, and idempotence checks have no seam to test
at. Coverage is `backup` and `cmd` only — and `test/test_cmd.py:11` asserts
`assertTrue(True)`.

**Windows 11 breaks the shared model.** No `sudo`, no rc-file to `source`, and
`lib/shell.py:35` raises `UnsupportedShell` for anything but bash/zsh/ash. Windows
is not a fifth platform class; it invalidates v1's assumptions.

## Goals

1. **Zero runtime dependencies.** Stdlib only. `python3 apply.py` works on a bare
   machine.
2. **Idempotent by construction.** Every run computes current state, diffs against
   desired state, and emits only the delta. Running twice is a no-op.
3. **Adding a tool is a 4-line config edit**, no code change.
4. **Three platforms, first-class**: macos, ubuntu (24.04), windows (11).
5. **Two scopes, composable**: personal, work, either, both.
6. **Safe to preview.** `--dry-run` is the default posture; nothing mutates until
   confirmed.
7. **LLM-maintainable.** Structure, docs, and tests optimized for an LLM making
   changes with a human reviewing a diff.

## Bootstrap contract

Zero-dep means `tomllib`, which is Python **3.11+**. Availability on our targets:

| Target | Stock interpreter | Status |
| - | - | - |
| Ubuntu 24.04 | 3.12 | works out of the box |
| Windows 11 | none preinstalled | `winget install Python.Python.3.13` |
| macOS | `/usr/bin/python3` = **3.9.6** | needs a real Python first |

So `apply.py` must stay **parseable and runnable under 3.9** even though the rest
of the tool is not:

- No `match`, no PEP 604 `X | Y` annotations, no PEP 701 nested-quote f-strings in
  `apply.py` itself. (The PEP 701 f-string at `platforms/ubuntu.py:30` is what
  silently made v1 3.12-only; do not reintroduce that pattern in the entry point.)
- First real statement is a version gate. Under 3.11 it does not traceback — it
  prints the exact remediation for the detected OS and exits non-zero.
- `apply.py bootstrap` is the one subcommand that runs on 3.9: it reads **no
  config** (so it needs no TOML), installs Homebrew + `python@3.13` on macOS, then
  tells the user to re-run under the new interpreter.
- **The gate must run before any `lib/` import.** Imports are resolved at module
  load, so a 3.9-parseable `apply.py` that imports a 3.11-only module still dies
  with `SyntaxError` before reaching the gate. Keep `apply.py`'s top-level imports
  to `sys`/`os` only and import `lib.*` inside the subcommand functions, after the
  gate has run.

Verified against the real stock interpreter on this machine: the gate pattern
prints cleanly and exits 2 under `/usr/bin/python3` (3.9.6), while
`platforms/ubuntu.py` is a hard `SyntaxError` there — which is precisely the
failure mode the gate replaces. Test with `/usr/bin/python3 apply.py` on macOS.

## Config

`config.yml` → **`config.toml`**. `tomllib` is stdlib; the existing config uses no
YAML-specific features (no anchors, aliases, or merge keys — verified), so nothing
is lost. Cost: TOML has no comment-preserving writer, so the file is human/LLM-edited
only, never machine-rewritten.

Schema inverts v1's nesting to be **tool-centric** — one block per tool, which is
what makes adding and removing tools cheap:

```toml
[meta]
min_python = "3.11"

[user]
name  = ""                      # "" prompts on first run
email = ""

# ── tools ──────────────────────────────────────────────────────────
# One block per tool. A platform key present = install there.
# A platform key absent = not installed there. scope defaults to "all".

[tools.tmux]
macos  = "tmux"
ubuntu = "tmux"

[tools.ripgrep]
macos   = "ripgrep"
ubuntu  = "ripgrep"
windows = "BurntSushi.ripgrep.MSVC"

[tools.docker]
macos.cask = "docker"           # inline table = provider-specific handling
ubuntu     = "docker.io"
windows    = "Docker.DockerDesktop"

[tools.nethack]
scope  = "personal"
macos  = "nethack"
ubuntu = "nethack-console"

[tools.veracrypt]
scope      = "personal"
macos.cask = "veracrypt"

# ── dotfiles ───────────────────────────────────────────────────────

[dotfiles.vimrc]
src = "files/vim/vimrc"
dst = { unix = "~/.vimrc", windows = "~/_vimrc" }

[dotfiles.nethackrc]
scope = "personal"
src   = "files/nethackrc"
dst   = { unix = "~/.nethackrc" }

# ── steps ──────────────────────────────────────────────────────────

[steps.git_config]
enabled = true
settings = { "pager.branch" = "false", "pager.diff" = "false", "init.defaultBranch" = "main" }

[steps.ssh_keys]
enabled   = true
algorithm = "ed25519"

[steps.sshd]
enabled = false
```

Rules: scope is `"all" | "personal" | "work"` (or a list). Platform keys are
`macos | ubuntu | windows`. Absence means "not applicable here" — never an error.
`~` is expanded by the tool via `pathlib.Path.expanduser()`, never by a shell.

## Architecture: plan / apply

The central change. Every step becomes a **pure planner** that reads system state
through an injected probe and returns declarative `Action`s. Nothing executes
during planning. This one seam delivers idempotence, dry-run, the TUI, and
testability simultaneously — they stop being four features and become consequences
of one design.

```
apply.py                  entry point; 3.9-safe version gate, arg parsing
config.toml               all declarative config
files/                    dotfile payloads (was config-files/)
lib/
  term.py                 ANSI + raw keyreads; Windows VT enable via ctypes
  tui.py                  interactive selector
  actions.py              Action dataclasses (frozen)
  planner.py              step registry; builds the Plan
  executor.py             the ONLY module that mutates; dry-run aware
  probe.py                read-only system queries behind a Protocol
  context.py              Context: platform, scopes, config, probe
  steps/
    __init__.py           STEPS registry: ordered list of planners
    packages.py  dotfiles.py  shell_profile.py  git_config.py
    ssh_keys.py  services.py  fonts.py  prompt.py
  providers/
    __init__.py           pick_provider(platform) -> Provider
    brew.py  apt.py  winget.py
docs/
  DESIGN.md  CONVENTIONS.md
tasks/TODO.md
tests/
```

### Action

```python
@dataclass(frozen=True)
class Action:
    kind: str               # "install" | "copy" | "append" | "run" | "mkdir"
    summary: str            # one line, shown in TUI and dry-run
    argv: tuple[str, ...] = ()
    path: Path | None = None
    content: str | None = None
    needs_root: bool = False
    reason: str = ""        # why this is needed; shown in --explain
```

### Planner contract

```python
def plan(ctx: Context) -> list[Action]:
    """Pure. Reads ctx.probe, never mutates, never shells out.
    Returns only the delta between current and desired state."""
```

Idempotence is not a feature bolted on — a planner that finds no delta returns
`[]`, so a second run produces an empty plan by construction. The rule that makes
this hold: **planners never call `subprocess`.** All system reads go through
`ctx.probe`, which is the single mockable seam.

```python
class Probe(Protocol):
    def installed_packages(self) -> frozenset[str]: ...
    def file_hash(self, p: Path) -> str | None: ...
    def file_contains(self, p: Path, needle: str) -> bool: ...
    def git_config(self, key: str) -> str | None: ...
    def which(self, exe: str) -> str | None: ...
    def env(self, key: str) -> str | None: ...
```

`RealProbe` caches per run (one `brew list` / `apt list --installed` /
`winget list`, not one per package — v1 shelled out per operation). `FakeProbe`
takes a dict and backs every unit test.

### Executor

The only module permitted to mutate the system. Fixes v1's `lib/cmd.py`:

- Never `shell=True`; `argv` is always a tuple, so the `'...'.split(' ')` bug class
  (which v1 already had to special-case at `lib/git.py:19`) is gone structurally.
- Streams output instead of capturing and discarding it.
- `--dry-run` prints actions and executes nothing.
- Root handling moves here: actions declare `needs_root`, and the executor
  acquires privilege once per run — `sudo` on Unix, and on Windows either a
  manifest-elevated re-exec or a clear "run as Administrator" error. v1's
  `cmd.run(['sudo','ls'])` prompt-primer in three `__init__`s disappears.
- On any failure: stop, print the remaining plan, and exit non-zero. Because
  planning is idempotent, the fix-and-rerun loop is safe — no resume logic needed.

### Providers

| Platform | Install | Query | Root |
| - | - | - | - |
| macos | `brew install` / `brew install --cask` | `brew list --formula/--cask` | sudo for some steps |
| ubuntu | `apt-get install -y` | `dpkg-query -W` | sudo |
| windows | `winget install --accept-*-agreements` | `winget list` | elevation, no sudo |

Provider resolves a tool's config value to argv: a bare string is the package
name; an inline table like `{cask = "docker"}` selects provider-specific handling.

### Shell profile, per platform

v1 wrote one `rc-custom` sourced from bash/zsh/ash. Windows has no equivalent, and
the file has real portability bugs — `ls -G --color` means *colorize* on BSD but
*suppress group* on GNU; `PATH` includes `./`; `guf` hardcodes `master`.

Split into `files/shell/common.sh` + `macos.sh` + `ubuntu.sh` +
`files/shell/profile.ps1`. Unix appends one guarded `source` line to the real rc
file; Windows writes the PowerShell `$PROFILE`. Both use a **sentinel block** so
edits are idempotent *and* removable:

```sh
# >>> managed by config (do not edit inside) >>>
source ~/.config/shell/common.sh
# <<< managed by config <<<
```

Rewriting between sentinels replaces rather than appends, which is the direct fix
for v1's duplication bug.

## TUI

Zero-dep, stdlib only, works on all three platforms.

- `lib/term.py`: raw mode via `termios`/`tty` on Unix and `msvcrt` on Windows;
  ANSI escapes for cursor and color (no colorama). On Windows, enable
  `ENABLE_VIRTUAL_TERMINAL_PROCESSING` through `ctypes` once at startup.
- **`curses` is deliberately not used** — it is absent from the Windows stdlib.
- Always restore the terminal via `try/finally` + `atexit`, including on `SIGINT`.
- If `not sys.stdout.isatty()`, skip the TUI and require explicit flags, so CI and
  pipes still work.

Flow, each screen driven by the same plan data:

```
┌─ config ─ ubuntu · personal+work ──────────────┐
│ Steps                                          │
│  [x] packages        42 to install, 3 present  │
│  [x] dotfiles         2 changed, 3 unchanged   │
│  [ ] ssh keygen       skip (key exists)        │
│  [x] git config       4 settings differ        │
│                                                │
│ ↑↓ move  space toggle  d diff  a apply  q quit │
└────────────────────────────────────────────────┘
```

1. **Detect & confirm** — platform auto-detected, scopes toggled.
2. **Step list** — each step's action count, computed by running planners. Steps
   with an empty plan render greyed as `up to date`, which makes idempotence
   visible rather than theoretical.
3. **Drill-down** — per-action detail; unified diff for dotfiles.
4. **Confirm** — full action list, root requirements called out.
5. **Apply** — live progress, streamed output, per-action ok/fail.
6. **Manual steps** — the surviving `manual_config` checklist.

CLI stays first-class and is what tests and LLMs drive:
`apply.py plan|apply|tui|bootstrap [--platform] [--personal] [--work] [--only STEP] [--dry-run]`.

## Testing

**Verdict on v1: not effective, and yes this project needs tests.** Not for
correctness theater — because changes will be authored by an LLM and reviewed as a
diff, so a fast honest signal is the main guardrail against a plausible-looking
change that would wreck a machine.

What's wrong with the current 3 tests:

- `test/test_cmd.py:11` asserts `assertTrue(True)` — it can only fail by raising.
- `test/test_backup.py` mutates the real filesystem at a **cwd-relative**
  `./unittest_data` and `shutil.rmtree`s it, so it only passes from the repo root.
- Neither touches the logic that decides what gets installed. The scope-merge
  block — duplicated at five call sites — has zero coverage, which is why the
  `manjaro.py:30` `snap = []` bug and the platform-key mismatch shipped unnoticed.

The plan/apply split makes the important logic pure, so it becomes testable
without a container:

| Layer | Test | Speed |
| - | - | - |
| Planners | unit, `FakeProbe`, no I/O | ms |
| Whole plan | **golden files** per (platform, scope) | ms |
| Config | schema validation, unknown-key rejection | ms |
| Executor | `argv` construction; a fake runner asserts no `shell=True` | ms |
| End-to-end | optional `ubuntu:24.04` container smoke | minutes, not required |

**Golden plan tests are the keystone.** For each of the 9 (platform × scope)
combinations, render the plan to deterministic text and compare to a checked-in
file under `tests/golden/`. This suits LLM-authored change better than assertions:
intent shows up as a readable diff (`ubuntu-personal.txt: + install ripgrep`),
`--update-golden` regenerates them, and an unintended change to another platform is
immediately visible. Requires sorting output and injecting the clock — v1 already
has an ambient-time bug here (`lib/backup.py:9` calls `time.time()` directly).

Also: run `unittest` from anywhere via `tmp_path`-style temp dirs, test Windows and
macOS planners on any host (probes are faked), and keep `pathlib` everywhere so
path assertions hold cross-platform.

**Alpine is dropped**, per your condition that it stays only if the current
strategy is kept — it isn't. Alpine also tests musl/ash, a combination you don't
run. Replaced by an optional `ubuntu:24.04` smoke test, which is a platform you
actually use.

## Working with an LLM on this repo

Structural choices specifically to make LLM-authored change safe and cheap:

1. **Config over code.** Adding a tool is 4 lines of TOML with no code path — the
   highest-frequency change carries the lowest risk.
2. **`docs/CONVENTIONS.md`** — the rules an LLM must not violate: planners are
   pure, only the executor mutates, no `shell=True`, no bare `subprocess`, no
   ambient `time`/`random`, entry point stays 3.9-safe. Short and prescriptive.
3. **One registry, one place.** `lib/steps/__init__.py` lists step order
   explicitly. No import-time magic, no decorators, no dynamic discovery — an LLM
   reading one file sees the whole pipeline. This replaces v1's implicit coupling
   where step order silently mattered.
4. **Golden files as reviewable intent** (above).
5. **`tasks/TODO.md` as the work queue** — stable task IDs (`T1`, `T2`) so a
   session can be told "do T7", with explicit acceptance criteria per task so
   "done" is checkable rather than asserted.
6. **Small files, one concern each.** Every step file is independently
   comprehensible; a change to `ssh_keys` cannot require reading `packages`.
7. **Keep `CLAUDE.md` pointing here** rather than duplicating — one source of
   truth, so the two can't drift.

## Deprecations

- **manjaro** — remove `platforms/manjaro.py` and its config. You no longer run it,
  and it's currently broken twice over (`KeyError: 'manjaro_linux'`, plus the
  `snap = []` shadowing).
- **alpine** — remove with the old test strategy.
- **`config.yml`, `requirements.txt`, `Dockerfile-test`** — superseded.
- The five bugs recorded in `tasks/TODO.md` are all resolved *structurally* by v2
  rather than patched in v1; `T0` keeps the one-line `manjaro` fix only as a
  stopgap if you need that machine before v2 lands.

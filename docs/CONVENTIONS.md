# Conventions

Rules for changing this repo. Prescriptive on purpose: violating any of these
breaks a property the design depends on. Architecture rationale is in
`docs/DESIGN.md`; sequenced work is in `tasks/TODO.md`.

## Hard rules

1. **Planners are pure.** A `plan(ctx) -> list[Action]` function must not mutate
   anything and must not call `subprocess`. All system reads go through
   `ctx.probe`. Violating this breaks dry-run, the TUI, and every unit test at once.

2. **Only `lib/executor.py` mutates.** No other module writes files, installs
   packages, or spawns processes. If you need a new kind of side effect, add an
   `Action` kind and handle it in the executor.

3. **Never `shell=True`.** Build `argv` as a tuple of separate arguments. Do not
   write `"cmd --flag val".split(" ")` — it breaks on any value containing a space,
   which v1 had to special-case for `user.name`.

4. **No ambient nondeterminism.** No `time.time()`, `datetime.now()`, or
   `random` inside planners — inject via `Context`. Golden tests depend on this.

5. **`apply.py` stays Python 3.9-parseable.** No `match`, no `X | Y` annotations,
   no nested-quote f-strings in the entry point. Everything under `lib/` may use
   3.11+ freely. A 3.9 interpreter must reach the version-gate message rather than
   a `SyntaxError`. Corollary: `apply.py` imports only `sys`/`os` at top level —
   `lib.*` imports go **inside** the subcommand functions, because a top-level
   import of a 3.11-only module crashes before the gate can run.

6. **Zero runtime dependencies.** Stdlib only, forever. No `pip install` may be
   required to run `plan`, `apply`, or `tui`. Test-only helpers are also stdlib
   (`unittest`, not `pytest`).

7. **Paths via `pathlib`, expanded in Python.** `Path(...).expanduser()`. Never
   rely on a shell to expand `~` or `$HOME` — there is no shell. v1's
   `tools/oh_my_posh.py` passed a literal `$HOME/...` to `wget` and created a
   `./$HOME/` directory.

8. **Idempotence is the planner's job.** Return only the delta. Text inserted into
   a user's file goes between sentinels and is rewritten in place, never appended
   blindly.

9. **Destructive writes back up first.** Any action overwriting an existing user
   file backs it up to `<path>.bkp.<timestamp>` (timestamp from `ctx`, per rule 4).

## Adding things

**A tool** — edit `config.toml` only. No code:

```toml
[tools.ripgrep]
macos   = "ripgrep"
ubuntu  = "ripgrep"
windows = "BurntSushi.ripgrep.MSVC"
```

Omit a platform to skip it there. Add `scope = "personal"` to limit it. Then
`python3 apply.py plan --platform ubuntu --personal` and confirm it appears;
`--update-golden` to record.

**A step** — new file in `lib/steps/`, exporting `plan(ctx)`. Register it in the
ordered `STEPS` list in `lib/steps/__init__.py`. Add unit tests with `FakeProbe`
covering: no-op when already applied, correct actions when not, and skipped when
its platform/scope doesn't apply.

**A platform** — new provider in `lib/providers/`. The platform's name must be
**identical** in the CLI, `config.toml` keys, and `pick_provider` — the one
mismatch in v1 silently broke two of its four platforms.

## Style

Match the existing code: 4-space indent, `snake_case`, module-level functions over
classes unless there's state, f-strings, double quotes. Type-annotate new code in
`lib/`. Docstrings only where the "why" isn't obvious — no restating the signature.
Keep files small and single-concern.

## Before you finish

- `python3 -m unittest` from the repo root **and** from another directory (tests
  must not depend on cwd).
- `python3 apply.py plan --platform <each> ` for every platform you touched.
- `python3.9 apply.py` still prints the version-gate message.
- Golden files updated and their diff reviewed — a diff in a platform you didn't
  intend to change means something is wrong.
- Never run `apply` (non-dry-run) to "verify" a change; it mutates the real
  machine. Dry-run and container tests are the verification path.

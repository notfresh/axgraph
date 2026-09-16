---
description: Symlink ~/.local/bin/ax → axgraph/bin/ax so `ax` is on your shell PATH (pip-install-style standalone install).
---

# /axgraph:install — Symlink `ax` into your shell PATH

This is the **standalone install path** — symlinking the axgraph wrapper into
`~/.local/bin/` so typing `ax` in a fresh shell works without manually
`export PATH=...`. It is the same as running `./install.sh` from the axgraph
repo root.

## What to do

1. **Locate the axgraph install root.** The host that loaded this plugin
   already knows where axgraph lives:
   - Kimi Code: `$KIMI_CODE_HOME/plugins/managed/axgraph/`
   - Claude Code: `~/.claude/plugins/axgraph/`
   - Standalone (git clone): wherever the user cloned it

   If the host exposes the plugin path (e.g. `$AX_GRAPH_ROOT` env var, or
   you can read it from the plugin metadata), use that. Otherwise ask the
   user.

2. **Run the install script.** From the axgraph repo root:

   ```bash
   ./install.sh
   ```

   The script will:
   - Detect `$AXGRAPH_ROOT` automatically (it's `$(dirname "$0")`-resolved)
   - Symlink `~/.local/bin/ax` → `<axgraph>/bin/ax`
   - Check whether `~/.local/bin` is on the user's PATH; if not, print the
     `export PATH=...` line they need to add
   - Print a one-line test command (`ax --version` should output `0.1.0`)

   The script is idempotent — re-running just refreshes the symlink. Safe to
   call after `git pull` or after the host upgrades axgraph.

3. **Tell the user what happened.** Surface:
   - Where the symlink landed (`~/.local/bin/ax → <axgraph>/bin/ax`)
   - Whether `~/.local/bin` is on their PATH (and if not, the exact export
     command to add)
   - How to uninstall (`rm ~/.local/bin/ax`)

## Important context

**This only affects the user's shell PATH.** It does NOT change how the
host (Kimi / Claude Code) runs `ax` internally — the host already knows the
plugin's install path and doesn't need a symlink. So:

- If the user installed axgraph via Kimi/Claude Code, `/axgraph:install`
  still helps: it gives them a way to use `ax` from their shell (e.g. for
  ad-hoc queries, scripts, cron jobs) without opening the host.
- If the user did `git clone` + `./install.sh` themselves, this slash command
  is just a convenience wrapper around the same script.

## What NOT to do

- Don't try to symlink into `/usr/local/bin/` without `sudo` — it fails on
  most systems and surprises the user.
- Don't add `~/.local/bin` to PATH automatically (e.g. by appending to
  `~/.bashrc`). Modifying shell rc files from a slash command is a
  surprising side effect — print the command and let the user decide.
- Don't use `cp` instead of `ln -s`. The symlink approach means `git pull`
  updates take effect without re-running install.
- Don't claim "PATH updated" if `install.sh` warned that `~/.local/bin`
  isn't on the current PATH — the symlink exists, but the user still needs
  the export for it to be useful in *this* shell. They can `source ~/.bashrc`
  in already-open shells.

## Reference

- `install.sh` — the underlying script (one source of truth, this command
  is just documentation for it)
- README.md §"Installed via Kimi Code / Claude Code — `ax` in your shell?"
  — longer explanation of why this is needed and the 3 workarounds

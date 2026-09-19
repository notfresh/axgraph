---
description: Install `ax` onto the user's shell PATH so it works from any terminal (POSIX: symlink via install.sh; Windows: shim via install.ps1).
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

2. **Detect the OS.** The two install scripts are not interchangeable —
   pick the right one based on the user's shell:

   ```powershell
   # PowerShell — single check that works for detection + dispatch
   if ($IsWindows -or ($env:OS -like '*Windows*')) {
       # → jump to step 3-Win
   } else {
       # → jump to step 3-POSIX
   }
   ```

   ```bash
   # POSIX shells (bash / zsh)
   if [[ "$(uname -s)" == *"Windows"* ]] || [[ -n "$WINDIR" ]]; then
       # → jump to step 3-Win (rare — usually Git Bash / WSL are POSIX)
   else
       # → jump to step 3-POSIX
   fi
   ```

   Picking the wrong branch will silently fail (running `install.sh` on
   Windows gives `bash: ./install.sh: No such file or directory` or similar).

### 3-POSIX (Linux / macOS / WSL / Git Bash)

From the axgraph repo root:

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

### 3-Win (Windows native — cmd / PowerShell)

From the axgraph repo root, in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

The `-ExecutionPolicy Bypass` is needed because Windows PowerShell's default
execution policy (`Restricted` for clients, `RemoteSigned` for servers)
blocks `.ps1` scripts by default. Bypassing only affects this one
invocation — it does not change the system policy. If the user has already
set `RemoteSigned` or `Unrestricted` system-wide, the flag is a no-op.

The script will:
- Detect `$AXGRAPH_ROOT` automatically from `$PSCommandPath`
- Generate `%USERPROFILE%\bin\ax.cmd` (or the directory passed as the first
  argument) — a small wrapper that calls `python %AX_GRAPH_ROOT%\bin\ax %*`
- Add that directory to the user's PATH via `[Environment]::SetEnvironmentVariable`
  (user-level, no admin required)
- Print a one-line test command (`ax --version` should output `0.1.0`)

The script is idempotent — re-running regenerates the shim and skips PATH
if the directory is already present.

**Note on new windows:** PowerShell / cmd processes inherit their PATH at
launch. The user must open a new shell window after install for `ax` to be
visible — current windows keep the old PATH.

3. **Tell the user what happened.** Surface:
   - **POSIX:** Where the symlink landed (`~/.local/bin/ax → <axgraph>/bin/ax`),
     whether `~/.local/bin` is on their PATH (and if not, the exact export
     command to add), and how to uninstall (`rm ~/.local/bin/ax`).
   - **Windows:** Where the shim landed (`%USERPROFILE%\bin\ax.cmd`),
     whether the directory was added to user PATH, and how to uninstall
     (`Remove-Item $env:USERPROFILE\bin\ax.cmd` and remove the directory
     from user PATH).

**Windows-specific gotchas:**

- PowerShell default `ExecutionPolicy` blocks `.ps1`. Always invoke with
  `-ExecutionPolicy Bypass` (or set the process scope via
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` before
  calling).
- PATH changes take effect only in **new** PowerShell / cmd windows —
  tell the user to open a fresh window.
- If `python` is not on the user's PATH, `ax.cmd` will fail with
  `'python' is not recognized`. Have them re-run the Python installer
  and check "Add Python to PATH", or install via the Microsoft Store
  Python 3.x.
- WSL / Git Bash users are **POSIX**, not Windows. They run `./install.sh`,
  not `install.ps1`, even if their Windows username is the host.
- The `ax.cmd` shim lives in the user's bin directory (default
  `%USERPROFILE%\bin`) and is regenerated on every `install.ps1` run. To
  uninstall, remove `ax.cmd` and the directory entry from user PATH.

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

- `install.sh` — POSIX install script (symlink-based)
- `install.ps1` — Windows install script (cmd shim + user PATH)
- README.md §"Installed via Kimi Code / Claude Code — `ax` in your shell?"
  — longer explanation of why this is needed and the 3 workarounds

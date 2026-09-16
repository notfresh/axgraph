# AX-GRAPH

> **Layered source-code graph (TOML) for any project.**
> Manual-graph discipline — humans author the graph, AI validates / extracts /
> diagnoses. Plugin form: installable into Claude Code and Kimi Code.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](VERSION)

## What is this?

axgraph lets you build a **layered code graph** of any Python project — stored
as plain TOML files in `.axgraph/` at the project root — and then query /
validate / diagnose that graph through a single CLI (`ax`) or four slash
commands in your AI agent.

Three layers, three questions:

| Layer | Granularity | Question it answers |
|---|---|---|
| Layer 1 | module / file | Where does the code live? |
| Layer 2 | cluster / subpackage | Who clusters with whom? |
| Layer 3 | feature / function / gitCommit | How is a feature implemented? What did this commit change? |

Plus a long-life metadata layer (`Layer-longlife.toml`) for principles,
constraints, decisions, invariants — the "why" of the code.

## Install

### Claude Code (Anthropic)

```bash
# Add the marketplace (one-time)
claude plugin marketplace add https://github.com/notfresh/axgraph

# Install the plugin
claude plugin install axgraph@axgraph
```

### Kimi Code (Moonshot)

```bash
# Direct from GitHub
kimi plugin install https://github.com/notfresh/axgraph
# Pin a tag:
kimi plugin install https://github.com/notfresh/axgraph/tree/v0.1.0
```

### Standalone CLI (no agent)

The wrapper needs `bin/ax` on your PATH. Two options:

**pip-install style (recommended)** — symlink once, use forever:

```bash
git clone https://github.com/notfresh/axgraph
cd axgraph
./install.sh                    # creates ~/.local/bin/ax → axgraph/bin/ax
ax --version                     # 0.1.0 — works from any cwd
```

The script checks whether `~/.local/bin` is on your PATH and prints the fix
(`export PATH=...`) if not. Re-run `./install.sh` after `git pull` to refresh
the symlink (it remains valid since it points at the file, not at a version
hash, but running it again is harmless and idempotent).

**Manual PATH** — if you prefer not to symlink:

```bash
git clone https://github.com/notfresh/axgraph
export PATH="$PWD/axgraph/bin:$PATH"
ax --help
```

To make it permanent: add the `export PATH=...` line to `~/.bashrc` (or your shell's rc file).

## Quick start (inside any project)

```bash
cd /path/to/your-project

# 1. Scaffold .axgraph/ in this project
ax init

# 2. Read the editing manual
cat .axgraph/SCHEMA.md

# 3. Author your first Layer-1 nodes (manual — see docs/SCHEMA.md §6)
$EDITOR .axgraph/base-dir-*/Layer-1-Graph.toml

# 4. Validate
ax query --validate

# 5. Pick a Python file and extract CALLS candidates
ax extract path/to/file.py
# → paste the candidates into Layer-3-Graph-<feature>.toml

# 6. Look up a node
ax query mod.agent -c -r
```

## Slash commands (when installed in Claude Code / Kimi Code)

| Command | Purpose |
|---|---|
| `/axgraph:init` | Scaffold `.axgraph/` in the current project |
| `/axgraph:query <id-or-keyword>` | Look up a node, list bases, validate |
| `/axgraph:purity <func-id>` | Function purity analysis (L0/L1/impure) |
| `/axgraph:diagnose <feature-id>` | Feature-chain cohesion + coupling verdict |

These are documented individually in `commands/`.

## Requirements

- **Python 3.10+** (3.11+ recommended). On 3.10, run `pip install tomli` (graph_query.py / call_candidates.py auto-fall-back; the plugin declares this in both manifests).
- **Node.js 18+** for the SessionStart hook (Claude Code path only; Kimi Code uses the declarative `sessionStart.skill` and does not need Node).
- No other runtime dependencies.

## Environment variables

| Variable | Used by | Default | Effect |
|---|---|---|---|
| `AX_GRAPH_DATA_DIR` | lib/graph_query.py | cwd or cwd/.axgraph | Override the data directory (where base-* subdirs live). Useful when running tools outside a project root. |
| `AX_GRAPH_PROJECT_ROOT` | lib/call_candidates.py | cwd or cwd/.axgraph parent | Override the project root (where the source code under analysis lives). Distinct from `AX_GRAPH_DATA_DIR`: one is the graph data, the other is the code being graphed. |

Both also accept a `--data-dir` flag on the relevant subcommand.

## What this is NOT

- **Not an auto-builder.** No tree-sitter, no MCP server, no SQLite. The
  project explicitly rejected automation — see `docs/AGENTS.md` §1 and
  the founding decision recorded there. axgraph is a discipline tool, not a
  scanning tool.
- **Not a runtime profiler.** It analyzes static structure (TOML) you author
  yourself. Dynamic call traces, runtime dependencies, control-flow graphs
  are out of scope.
- **Not a project-specific tool.** It started as the X-GRAPH for hermes-agent-plus
  (task 0012) and has since been generalized — see `docs/RELEASE.md` for the
  evolution.

## Documentation

| Doc | Purpose |
|---|---|
| [docs/SCHEMA.md](docs/SCHEMA.md) | Editing manual for `[[nodes]]` / `[[edges]]` |
| [docs/AGENTS.md](docs/AGENTS.md) | Iron rules for AI + human collaborators |
| [docs/How-to-update-graph.md](docs/How-to-update-graph.md) | Line-number drift handling |
| [docs/usage-skill-load.md](docs/usage-skill-load.md) | Worked example: skill-load feature |
| [docs/TODO.md](docs/TODO.md) | Future plans |
| [docs/RELEASE.md](docs/RELEASE.md) | Version history |

## Plugin layout

```
axgraph/
├── .claude-plugin/plugin.json      Claude Code manifest
├── kimi.plugin.json                Kimi Code manifest
├── bin/ax                          CLI wrapper (PATH)
├── lib/                            Python tools
│   ├── graph_query.py              Query / validate / base management
│   ├── purity.py                   Function purity analysis
│   ├── diagnose.py                 Feature-chain diagnosis
│   ├── update_graph.py             Per-node update tool
│   └── call_candidates.py          AST extractor for CALLS candidates
├── skills/using-axgraph/SKILL.md   Bootstrap skill (injected at session start)
├── commands/                       Slash commands (init/query/purity/diagnose)
├── hooks/                          Claude Code SessionStart hook
├── docs/                           README, SCHEMA, AGENTS, ...
└── VERSION
```

## License

MIT — see [LICENSE](LICENSE).

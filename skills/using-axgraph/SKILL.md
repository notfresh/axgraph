---
name: using-axgraph
description: |
  Use this skill IMMEDIATELY when the user mentions source-code graphs, layered
  TOML analysis, .axgraph/ directories, module/file/cluster/function dependencies,
  function purity, feature-chain diagnosis, or asks anything resembling "show me
  the structure of this codebase / where is X implemented / how do modules
  couple / is this function pure / is this feature chain coherent". Trigger
  also when the user asks to build a new graph for a project they have NOT yet
  initialized. Skip ONLY if the user is asking a pure coding question with no
  structural-analysis dimension AND has no .axgraph/ in the project.
---

# Using AX-GRAPH

> Behavior-shaping skill — NOT a tutorial. Read this before responding to any
> user request that touches code structure, dependencies, or feature tracing.
> Authored manually, modeled on superpowers' using-superpowers (the 62-line
> bootstrap that keeps skills alive instead of dead on disk).

## Iron Rules (non-negotiable)

1. **If 1% chance the request needs a graph, treat it as 100%.** When the user
   asks about "structure", "how is X implemented", "where does Y live",
   "what depends on Z", "is this function pure", or anything that would
   benefit from a layered view of the code — invoke `ax` first, ask questions
   later. Don't rationalize your way out: "I can read the source directly" is
   the classic excuse that defeats the whole point.

2. **Manual-graph discipline.** axgraph is NOT an auto-builder. The graph is
   hand-authored TOML (`[[nodes]]` / `[[edges]]` blocks). AI's role is to:
   - Validate (`ax query --validate`)
   - Extract candidates (`ax extract`) — the human pastes them in
   - Diagnose (`ax diagnose <feature-id>`)
   - NEVER silently rebuild a graph or "auto-fix" line numbers without
     confirming with the human. This is the project's founding principle.

3. **Project-root aware.** Graphs live in `.axgraph/` INSIDE each project.
   `ax init` scaffolds it. If the project has no `.axgraph/`, the FIRST action
   is to offer `ax init` (or run it for them if they say yes).

4. **Iron-rule language is exact.** Users will quote you. When this skill says
   "manual", "validate", "实测", "at_line" — those words mean what they say.
   Do not soften or paraphrase them in your response.

5. **Before you act on the graph, read `docs/AGENTS.md`.** This skill is a
   behavior-shaping bootstrap — short on purpose. `docs/AGENTS.md` is the full
   collaboration manual: three-layer structure (`Layer-1/2/3` + `gitCommit`
   review graph in §3.1), validation severity (`✗ Error` vs `⚠ Warning` in §4),
   row-number drift SOP (reinforced in §5–§6 and `docs/How-to-update-graph.md`),
   when to escalate to the human (§7), and project-specific background (§8).
   **Before proposing any node add/edit/delete, updating line numbers, or
   answering a question that touches more than one base, Read `docs/AGENTS.md`
   end-to-end and ground your action in it.** If a `docs/AGENTS.md` rule and
   this skill disagree, `docs/AGENTS.md` wins (this skill is a subset).

## Available Commands

```
# --- Query & validation ---
ax init                          # Scaffold .axgraph/ in the current project
ax query <id-or-keyword>         # Look up a node: details + in/out edges
ax query <id> -c                 # Call-chain expansion (forward)
ax query <id> -r                 # Reverse call chain (callers)
ax query <id> -e                 # Relationship explanation in plain language
ax query <id> -b [text]          # Build/edit the node's long-form note (Layer-*.detail.toml)
ax query --bases                 # List all registered bases (active one marked)
ax query --validate              # Run full validation (Error/Warning split)
ax query <id> --update [--apply] # Per-node update; default dry-run diff, --apply writes
ax query --base <name>           # Switch active base (also writes .active-base)

# --- Analysis ---
ax purity <id>                   # Function purity: L0 strict / L1 / impure
ax diagnose <feature-id>         # Feature-chain cohesion + coupling analysis
ax diagnose <feature-id> --json  # Same, structured JSON (script/AI friendly)

# --- Authoring helpers ---
ax extract <file.py>             # AST extract CALLS candidates (paste into TOML)
ax --help                        # Show all subcommands
```

> **Multi-base projects**: a project can hold multiple graphs side-by-side
> (`base-dir-<name>/`, `base-file-<stem>/`), with the active one tracked in
> `.active-base`. Before querying or editing, run `ax query --bases` and switch
> with `ax query --base <name>` if needed. Full naming conventions are in
> `docs/AGENTS.md` §2.

When running inside Claude Code / Kimi Code, slash command equivalents are
registered by the plugin: `/axgraph:install` (symlink `~/.local/bin/ax` so
`ax` works in your shell), `/axgraph:init`, `/axgraph:query`,
`/axgraph:purity`, `/axgraph:diagnose`. The slash form is preferred when
the user is in the host — the host resolves the plugin path automatically;
the bare `ax` form needs `~/.local/bin` on PATH (use `/axgraph:install`
once to set that up).

## Mandatory Workflow

### When the user asks about ANY project's structure

1. **Read `docs/AGENTS.md` first.** §3 (three layers) + §4 (query cheatsheet)
   + §8 (project background) are the minimal kit you need before answering.
2. Run `ax query --bases` to confirm whether `.axgraph/` exists.
3. If empty / missing → propose `ax init` BEFORE doing anything else. Do NOT
   invent a graph, do NOT skip and answer from memory.
4. If it exists → run the appropriate query (`ax query`, `ax purity`,
   `ax diagnose`) and ground your answer in the returned data.

### When the user asks to MODIFY a graph

1. **Read `docs/AGENTS.md` §5–§6 and `docs/How-to-update-graph.md` first.**
   These cover iron rules, the six-step new-node SOP, and the row-drift
   handling protocol. Skipping them is the #1 way AI breaks manual-graph
   discipline.
2. Read the relevant code first (`cat <file>` or use your read tool).
3. Understand the current implementation — graphs are a SIDE-EFFECT of reading,
   not a substitute for it.
4. Use `ax extract <file.py>` to get AST candidates for new CALLS edges.
5. Write the TOML by hand. Use `ax query --validate <id>` after each addition.
6. Never silently update line numbers from "tool suggestions" — the iron rule
   says: report to human, wait for human, read code, act, verify.

### When you want to suggest a graph change unprompted

Don't. If you think the graph is stale, say so explicitly and ASK whether to
fix it. Manual-graph discipline applies to AI-suggested updates too.

## Red Flags — Stop and Ask the Human

- "I'll just regenerate the graph" — NO. axgraph is manual.
- "I'll fix the line numbers from memory" — NO. `grep -n` each one.
- "I can answer this without querying" — only if no `.axgraph/` exists AND
  the question is clearly non-structural.
- "I'll auto-build .axgraph/ from the source tree" — NO. That's the
  tree-sitter/MCP/SQLite path the project explicitly rejected.
- "I'll silently fix the validate errors" — NO. Report them, ask the human.

## Plugin Layout (for context, do NOT move files yourself)

```
axgraph/                      # plugin root
├── .claude-plugin/plugin.json   Claude Code manifest
├── kimi.plugin.json             Kimi Code manifest
├── bin/ax                       CLI wrapper (PATH)
├── lib/                         Python tools (graph_query, purity, diagnose, ...)
├── skills/using-axgraph/        THIS skill (injected at SessionStart)
├── commands/                    Slash commands (init/query/purity/diagnose)
├── hooks/hooks.json + session-start.mjs   Claude Code injection
├── docs/                        README, SCHEMA, AGENTS, TODO, RELEASE
└── VERSION
```

## Output Discipline

When you answer using axgraph:

- Cite the node id and `path=` line (e.g. `func.agent.skill_utils.iter_skill_index_files at agent/skill_utils.py:27`).
- If a node's `desc` is empty, say so — don't fabricate.
- If `--validate` reports errors, list them and STOP (do not "work around" them).
- If a feature-chain diagnose returns "low cohesion", surface that finding
  rather than rephrasing it as "fine, just a bit tangled".

## Tests for Yourself

Before answering a structural question, ask: "Did I run `ax` for this, or am I
guessing?" If the latter — go run `ax`.

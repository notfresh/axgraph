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

## Available Commands

```
ax init                          # Scaffold .axgraph/ in the current project
ax query <id-or-keyword>         # Look up a node: details + in/out edges
ax query <id> -c                 # Call-chain expansion (forward)
ax query <id> -r                 # Reverse call chain (callers)
ax query --bases                 # List all registered bases
ax query --validate              # Run full validation
ax purity <id>                   # Function purity: L0 strict / L1 / impure
ax diagnose <feature-id>         # Feature-chain cohesion + coupling analysis
ax extract <file.py>             # AST extract CALLS candidates (paste into TOML)
ax --help                        # Show all subcommands
```

## Mandatory Workflow

### When the user asks about ANY project's structure

1. Run `ax query --bases` to confirm whether `.axgraph/` exists.
2. If empty / missing → propose `ax init` BEFORE doing anything else. Do NOT
   invent a graph, do NOT skip and answer from memory.
3. If it exists → run the appropriate query (`ax query`, `ax purity`,
   `ax diagnose`) and ground your answer in the returned data.

### When the user asks to MODIFY a graph

1. Read the relevant code first (`cat <file>` or use your read tool).
2. Understand the current implementation — graphs are a SIDE-EFFECT of reading,
   not a substitute for it.
3. Use `ax extract <file.py>` to get AST candidates for new CALLS edges.
4. Write the TOML by hand. Use `ax query --validate <id>` after each addition.
5. Never silently update line numbers from "tool suggestions" — the iron rule
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

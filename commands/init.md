---
description: Initialize .axgraph/ in the current project (scaffolds dirs, copies SCHEMA.md + AGENTS.md, creates an empty base).
---

# /axgraph:init — Scaffold .axgraph/ in the current project

The user wants to start tracking the structure of THIS project with axgraph.
This is the entrypoint — every other command assumes `.axgraph/` already exists.

## What to do

1. **Confirm cwd is the project root.** Run `pwd` and `ls` to see what's there.
   If a `.axgraph/` directory already exists, **stop** and tell the user — don't
   overwrite. They can `rm -rf .axgraph` if they really want to start over.

2. **Run the scaffold.** Use:

   ```bash
   ax init
   ```

   For a single-file graph instead, use:

   ```bash
   ax init --type file --source path/to/file.py
   ```

3. **Show the user what was created.** Print the resulting `.axgraph/`
   directory tree (e.g. `ls -la .axgraph/`).

4. **Hand off to the next step.** Tell them to read `.axgraph/SCHEMA.md` for
   the editing manual and `.axgraph/AGENTS.md` for the iron rules. Then point
   them at `ax extract <file.py>` as the first concrete action — pick a
   representative file in their project and run it.

## What NOT to do

- Do not auto-populate the graph with nodes/edges. **axgraph is manual.**
  The scaffold creates an empty `Layer-1-Graph.toml` with comments showing
  the format — the user authors the content.
- Do not run `--validate` on an empty graph expecting "success" — that's
  noise. Empty is empty; valid means "no errors", and an empty graph has no
  errors by construction.
- Do not suggest adding tree-sitter / MCP / SQLite / auto-build tools. The
  project's founding decision (see docs/AGENTS.md §1) explicitly rejected
  these. If the user asks for them, point them at docs/AGENTS.md.

## Reference

- Plugin layout: see the `using-axgraph` skill (injected at SessionStart)
- Iron rules: docs/AGENTS.md (also copied to `.axgraph/AGENTS.md` on init)
- Editing manual: docs/SCHEMA.md (also copied to `.axgraph/SCHEMA.md`)

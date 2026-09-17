---
description: Query a node or list bases in the current project's .axgraph/ (full power of lib/graph_query.py).
---

# /axgraph:query — Look up a node, list bases, or validate

This is the primary "where is X / what depends on Y" tool. Forwards to
`lib/graph_query.py` with full flag support.

## Common forms

```bash
ax query --bases                          # list all registered bases, mark default
ax query <node-id>                        # exact lookup: details + in/out edges
ax query <keyword>                        # fuzzy (exact → contains → difflib)
ax query '%skill%'                        # LIKE wildcard on id+path
ax query <id> -c                          # call-chain expansion (forward)
ax query <id> -r                          # reverse call chain (callers)
ax query <id> -e                          # human-readable relation explanation
ax query <id> -d                          # append Layer-*.detail.toml description
ax query --validate                       # run full validation across all bases
ax query --validate -l 3                  # validate only Layer-3 files
ax query --validate <id>                  # validate one node + its edges
ax query <keyword> -s                     # list mode (matches only, no expansion)
```

`$ARGUMENTS` from the slash command is appended after `ax query`. So the user
types `/axgraph:query mod.agent -c` and you run `ax query mod.agent -c`.

## Output format

`path= 文件:行号` (with space after `=`) is **clickable in VSCode terminal**.
Always include the `path=` line when citing a node in your reply.

## Mandatory pre-flight

1. Run `ax query --bases` first. If the user's project has no `.axgraph/`,
   **stop** and tell them to run `/axgraph:init` first. Don't fabricate a
   graph.
2. If `--validate` returns errors (✗ Error), surface them in your reply
   **before** answering the structural question. Errors mean the graph is
   in a broken state — you can't trust `CALLS` edges pointing to wrong lines.

## What NOT to do

- Don't paraphrase a node's `desc` field — quote it. Empty `desc` means
  empty; say so.
- Don't answer structural questions from memory when a node exists for the
  thing in question. The graph is the source of truth.
- Don't silently "fix" dangling edges. The iron rule says: report → ask →
  read code → fix → validate.

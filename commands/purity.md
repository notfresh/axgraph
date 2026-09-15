---
description: Analyze a function's purity — L0 (strict pure) / L1 (engineering pure) / impure — with evidence.
---

# /axgraph:purity — Function purity analysis

Forwards to `lib/purity.py`. Answers: "Is this function safe to refactor /
memoize / parallelize?"

## Common forms

```bash
ax purity <func-id>                  # analyze one function
```

`$ARGUMENTS` is the function id (e.g. `func.agent.skill_utils.iter_skill_index_files`).

## Output

The tool prints one of three tiers plus an evidence list:

| Tier | Meaning | When to use |
|---|---|---|
| **L0 严格纯** | Strictly pure: no I/O, no global state, deterministic on inputs | Trivial to test/memoize/parallelize |
| **L1 工程纯** | Engineering-pure: depends on injected state, but no observed side effects within the project | Safe to refactor with the existing dependencies preserved |
| **非纯** | Impure: I/O, network, file system, global mutation, etc. | Refactor carefully; expect to mock side effects in tests |

The evidence list shows the calls the function makes and whether each is
pure/non-pure (one level deep — transitive purity is NOT propagated).

## How to use the result

- **L0**: When the user asks "can I memoize this?" → yes.
- **L1**: When the user asks "is this safe to parallelize across N workers?"
  → only if the injected dependencies are also thread-safe; check the evidence.
- **非纯**: surface the side effects the tool identified. Don't just say
  "impure" — show the I/O sites.

## Pre-flight

1. Confirm `.axgraph/` exists (`ax query --bases`). If not → tell the user
   to run `/axgraph:init` first.
2. The target function must have `kind = "function"` and a `path` with a
   valid line number, otherwise the tool will report "definition not found".

## What NOT to do

- Don't run `ax purity` on `module` / `file` / `cluster` nodes — it's
  function-only.
- Don't claim a function is "pure" without citing the L0/L1/非纯 verdict
  from the tool.
- Don't generalize: if the tool says non-pure, say non-pure. Even if "it
  looks pure to me" — the tool's evidence list is the source of truth.

---
description: Diagnose a feature chain's cohesion/coupling (forwards to lib/diagnose.py).
---

# /axgraph:diagnose — Feature-chain diagnosis

Forwards to `lib/diagnose.py`. Answers: "Is this feature coherent or does it
sprawl across too many modules?"

## Common forms

```bash
ax diagnose <feature-id>                       # human-readable verdict
ax diagnose <feature-id> --json                # structured output for scripts
```

`$ARGUMENTS` is the feature id (e.g. `feature.skill-load`).

## What it reports

- **Internal dependency density** (how tightly the implementing functions
  call each other vs. how often they reach outside the chain)
- **Cohesion signal**: high if most edges stay inside the chain; low if the
  chain is a thin slice through many unrelated modules
- **Coupling hotspots**: which functions are reached from outside the chain
  most often
- A plain-language verdict: "high cohesion, low coupling" or "sprawls across
  6+ modules — consider splitting"

## How to use the result

- **High cohesion, low coupling**: feature is well-factored. Don't propose
  refactoring it.
- **Low cohesion**: feature is doing too much. Surface the spanning modules
  to the user and ask whether to split.
- **High external coupling**: the feature is depended on by many other
  things. Refactoring it has ripple effects — list the dependents.

## Pre-flight

1. The feature must be a `feature.*` node (kind = "feature"), not a
   `function` / `module` / `file`. Run `ax query <id>` first if unsure.
2. `.axgraph/` must exist; otherwise the user needs `/axgraph:init`.

## What NOT to do

- Don't run on non-feature nodes — the tool will refuse (or worse, return
  garbage on `mod.*` / `file.*`).
- Don't soften the verdict. If diagnose says "low cohesion", say low
  cohesion. Don't rewrite it as "could be tightened".

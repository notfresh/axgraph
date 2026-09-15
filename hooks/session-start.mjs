#!/usr/bin/env node
/**
 * axgraph SessionStart hook for Claude Code
 *
 * Runs once per session start. Reads skills/using-axgraph/SKILL.md and injects
 * it as additionalContext via stdout JSON. This is the "soul" of the plugin —
 * without this, the SKILL.md is a dead file on disk and the model has no idea
 * axgraph is available.
 *
 * Output schema (Claude Code v2.1+):
 *   { "hookSpecificOutput": { "hookEventName": "SessionStart",
 *                             "additionalContext": "<markdown body>" } }
 *
 * Edge cases:
 *   - SKILL.md missing  → exit 0, no output (plugin broken; don't crash session)
 *   - stdin unreadable  → exit 0 (some Claude Code versions don't pipe stdin)
 *   - any thrown error  → caught and swallowed (hook MUST NOT block session)
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
// hooks/session-start.mjs  →  ../skills/using-axgraph/SKILL.md
const skillPath = join(__dirname, "..", "skills", "using-axgraph", "SKILL.md");

try {
  const skillBody = readFileSync(skillPath, "utf8");
  const banner = `# axgraph plugin loaded

You now have the axgraph code-graph toolkit installed. Read the following before
responding to any user request — these are non-negotiable behavioral rules:

`;
  const payload = {
    hookSpecificOutput: {
      hookEventName: "SessionStart",
      additionalContext: banner + skillBody,
    },
  };
  process.stdout.write(JSON.stringify(payload));
} catch (err) {
  // Don't crash the session. Empty stdout = no injection, plugin is inert
  // (still better than blocking the user from using Claude Code).
  process.stderr.write(`axgraph hook: ${err.message}\n`);
  process.exit(0);
}

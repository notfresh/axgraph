# Releasing axgraph

How to ship a new version. axgraph is a **Claude Code / Kimi Code plugin**
that ships as a GitHub repo — the release story is "git tag + GitHub
release", not "PyPI upload".

## TL;DR — typical patch iteration

```bash
# 1. Make changes, commit, push
git add -A
git commit -m "fix(purity): handle empty source files"
git push origin master

# 2. Bump VERSION
echo "0.1.1" > VERSION
git add VERSION
git commit -m "bump: 0.1.1"
git push origin master

# 3. Tag the release
git tag v0.1.1
git push origin v0.1.1

# 4. (Recommended) Create a GitHub release so users on the 'latest release'
#    install URL get the new version
gh release create v0.1.1 --generate-notes
```

After step 3+4, anyone who installed via
`https://github.com/notfresh/axgraph` (the "latest release" URL form) will be
**prompted to upgrade** the next time they use the plugin. Users who pinned
`/releases/tag/v0.1.0` stay on that version until they explicitly reinstall.

## Versioning

Follow SemVer 2.0.0:

| Change | Bump | Example |
|---|---|---|
| Breaks plugin contract (manifest fields renamed, commands removed, hooks changed) | **major** | `0.x.y → 1.0.0` |
| Adds new commands / manifest fields / slash commands | **minor** | `0.1.0 → 0.2.0` |
| Bug fixes, doc updates, refactors with no behavior change | **patch** | `0.1.0 → 0.1.1` |

Three places to keep in sync when bumping:

1. `VERSION` (the source of truth — `bin/ax --version` reads this)
2. `kimi.plugin.json` → `"version": "0.x.y"`
3. `.claude-plugin/plugin.json` → `"version": "0.x.y"`

If you only bump one and forget the others, `ax --version` and the host's
Installed-tab display will disagree. **Bump all three or none.**

## Git tag vs GitHub release

Kimi Code supports two URL forms for pinning versions (per the
`/plugins install` documentation):

- `https://github.com/notfresh/axgraph` — latest release; falls back to
  default branch if no release exists
- `https://github.com/notfresh/axgraph/releases/tag/v0.1.1` — pinned to a
  specific tag

| Workflow | What users get | What you need to do |
|---|---|---|
| **No tag, push to master only** | Users on "latest release" URL see nothing (no release exists, fallback to master) | Nothing extra; they have to reinstall from the bare URL to refresh |
| **Tag only** (`git tag v0.1.1 && git push origin v0.1.1`) | Users on "latest release" URL see **no change** because latest release is still v0.1.0 | Tag is just a commit pointer — not a release |
| **Tag + GitHub release** (`gh release create v0.1.1`) | Users on "latest release" URL see v0.1.1 in the prompt and can upgrade | Tag + release; `gh` is the missing step |

**Always do the third row.** A tag without a GitHub release doesn't count as
a release in the GitHub Releases sense — `latest release` resolves to the
**most recent GitHub release**, not the most recent tag.

## What users experience after you push

Kimi Code's installed-plugin flow (per the official docs):

1. User installs via any of the 4 URL forms.
2. Kimi clones into `$KIMI_CODE_HOME/plugins/managed/axgraph/`.
3. Plugin is loaded — but plugin changes **only apply after `/reload` or
   `/new`**, the current session does not update.
4. When a new version is published, **Kimi prompts the user the next time
   they use the old version** (official plugin behavior; community
   plugins installed via GitHub URL also follow this).
5. To upgrade, user re-runs `kimi plugin install <url>` (this overwrites the
   managed copy), then `/reload`.

You (the maintainer) don't have to do anything special to "push" an update —
the GitHub release is the trigger.

## Iteration rhythm recommendations

| If your change is… | Recommended flow |
|---|---|
| Bug fix, single file, low risk | Commit → push → `gh release create vX.Y.Z` immediately. Users get prompt next session. |
| New feature, changes manifest fields, might break | Commit to a branch (`feat/foo`); test yourself by `kimi plugin install <branch URL>`; once happy, merge to master + tag + release |
| Breaking change | Major version bump. Add a "Migration" section to README. Pin users get the change only when they re-install (which they should re-read the migration for) |
| Experimental, don't want to disturb users | Push to a branch; users on master are unaffected. They only get it if they explicitly install the branch URL |

## Managed copy gotcha

Kimi copies the plugin into `$KIMI_CODE_HOME/plugins/managed/axgraph/`
on install. **Editing that directory directly does nothing** — next time
the plugin is re-installed or refreshed, Kimi re-clones from the GitHub URL
and overwrites. To test a local change without pushing:

```bash
# Make your edits in this repo (e.g. /root/projects/axgraph)
/usr/bin/python3 bin/ax --version   # test standalone

# When ready, push to GitHub, then in Kimi:
/plugins install https://github.com/notfresh/axgraph/tree/<branch>/<subdir>
# or for the master branch:
/plugins install https://github.com/notfresh/axgraph
```

There is no "watch mode" — Kimi does not auto-reload on file change.

## VERSION drift detection (TODO)

A future automation: a CI check that diffs `VERSION` against
`kimi.plugin.json` and `.claude-plugin/plugin.json`, fails the build if they
disagree. Not implemented yet — manual bumps are small enough to keep
three-way consistent. If releases start slipping, file an issue.

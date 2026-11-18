# KitSprout Claude Code plugins

**English** | [繁體中文](README.zh-TW.md)

Claude Code plugins by KitSprout.

```
/plugin marketplace add KitSprout/claude-plugins
/plugin install <plugin>@kitsprout
```

## Plugins

| Plugin | What it does | Type |
|---|---|---|
| [`handoff`](plugins/handoff) | Writes a handoff file before you switch sessions, so a new session continues from one file ("Read <path> and continue"). | skill, hook |
| [`debate`](plugins/debate) | Runs a subagent debate or multi-reviewer challenge on a design, plan or decision, with a judge that verifies sources. | skill |

Make sure you trust a plugin before installing or updating it: plugins can run hooks and commands on your machine.

## Repository layout

```
.claude-plugin/marketplace.json   the marketplace: every plugin's entry
plugins/<name>/                   small plugins live here, one folder each
  .claude-plugin/plugin.json      name, version, settings
  skills/ hooks/ commands/ agents/
  evals/                          test suite for `claude plugin eval`, when the plugin has one
  README.md  LICENSE
.github/workflows/validate.yml    checks on every pull request
```

Larger tools, with their own code, tests and releases, live in their own repositories and keep their plugin in a subfolder. This marketplace lists them by source, pinned to a release:

```json
{
  "name": "<tool>",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/KitSprout/<tool>.git",
    "path": "plugin",
    "ref": "v1.0.0",
    "sha": "<commit of that release>"
  }
}
```

A new release of such a tool reaches users only when its `ref` and `sha` are updated here.

## Conventions

- **Names are permanent.** A plugin's `name` is how installs find it. Change `displayName` to relabel it; if a rename cannot be avoided, add `"renames": {"old": "new"}` to `marketplace.json` so existing installs migrate.
- **Versions.** Raise `version` in `plugin.json` with every change users should receive.
- **Tests.** A plugin with an `evals/` folder documents how to run it and its latest results in its README.
- **Translations.** Every `README.md`, at the root and in each plugin, has a `README.zh-TW.md` beside it; when they differ, the English file wins. Keep both in step when you change either.
- **Before every push:** no personal data, keys, passwords, private hostnames or machine identifiers in any file. CI runs a generic secret scan; it cannot know what is private to you.

## Checks

`.github/workflows/validate.yml` checks on every pull request that JSON files parse, every local entry points to a folder whose `plugin.json` has the same name, every folder under `plugins/` is listed, every README has a `README.zh-TW.md`, external entries carry `ref` and `sha`, `claude plugin validate` passes for the marketplace and each plugin, model-free plugin checks pass, and no secrets are committed.

## License

MIT, see [LICENSE](LICENSE). Each plugin folder carries its own copy.

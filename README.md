# SP Data360 Mastery

An Agent Skill that makes AI coding agents expert in **Salesforce Personalization** — the Data 360–native personalization product sold with Marketing Cloud Next (formerly Einstein Personalization).

Every platform fact comes from current official Salesforce documentation and is cited inline. The skill also guards against the most common failure mode: answering with **Marketing Cloud Personalization (MCP)** knowledge. MCP (formerly Interaction Studio / Evergage) is a different product with different objects, SDK behavior and reporting.

## What's inside

| File | Covers |
|---|---|
| [SKILL.md](SKILL.md) | Product guardrails, answer workflow, routing, and the facts agents most often get wrong |
| [references/implementation-playbook.md](references/implementation-playbook.md) | Jump-start for a new customer: discovery checklist, architecture choices by channel and site type, setup order, use-case patterns, measurement plan, go-live checklist |
| [references/platform-and-setup.md](references/platform-and-setup.md) | Architecture, licensing, permissions, Personalization Setup, DMOs, limits, feature timeline |
| [references/web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md) | Salesforce Interactions SDK, sitemap, consent, identity, Personalization module, flicker defense, Decisioning API |
| [references/sitemap-templates.md](references/sitemap-templates.md) | Copy-ready multi-page / server-rendered starter sitemap, CMP-agnostic consent adapter, optional SPA add-on, catalog/cart/order event formats |
| [references/decisioning.md](references/decisioning.md) | Profile and item data graphs, personalization points, content schemas, decisions, targeting rules, recommenders |
| [references/wpm-experiences-campaigns.md](references/wpm-experiences-campaigns.md) | Web Personalization Manager, experience templates, personalization campaigns, experimentation |
| [references/measurement-and-attribution.md](references/measurement-and-attribution.md) | Engagement signals and metrics, attribution, Pipeline and Attribution Intelligence, reporting |
| [references/mobile-and-channels.md](references/mobile-and-channels.md) | Engagement Mobile SDK, server-side decisioning, batch decisions, Agentforce, Einstein Studio |
| [references/sp-vs-mcp.md](references/sp-vs-mcp.md) | How to tell Salesforce Personalization and MCP apart, and what never to say about SP |
| [references/troubleshooting.md](references/troubleshooting.md) | Symptom → cause → confirm → fix playbook |
| [references/sql-cookbook.md](references/sql-cookbook.md) | Data 360 SQL for personalization reporting |

## Install

Clone into a folder named `sp-data360-mastery` so the folder matches the skill's `name`.

**Cursor — all projects**

```bash
git clone https://github.com/Lior-SF/SP-Data360-Mastery.git ~/.cursor/skills/sp-data360-mastery
```

**Cursor — a single project** (run from the project root)

```bash
git clone https://github.com/Lior-SF/SP-Data360-Mastery.git .cursor/skills/sp-data360-mastery
```

**Claude Code**

```bash
git clone https://github.com/Lior-SF/SP-Data360-Mastery.git ~/.claude/skills/sp-data360-mastery
```

## Update

```bash
git -C ~/.cursor/skills/sp-data360-mastery pull
```

Releases are tagged (`v1.0.0`, …); see [CHANGELOG.md](CHANGELOG.md) for what changed.

## How it works

- The agent loads the skill automatically when a prompt concerns Salesforce Personalization; the description in `SKILL.md` lists the trigger terms.
- `SKILL.md` holds the guardrails and routing. The agent reads only the reference files a question needs.
- When the Salesforce Docs MCP server is available, the skill tells the agent to re-check volatile facts (limits, UI labels, new features) against live documentation before answering.

## Accuracy model

- **Baseline:** Salesforce release 264 (Winter '27) documentation, verified September 2026.
- **`[src](url)`** — the fact is supported by that official page.
- **`(UNVERIFIED)`** — useful, but not confirmed in documentation.
- **`(Field-observed, undocumented)`** — behavior seen in real implementations but absent from documentation. Re-test after SDK upgrades.
- **Sources:** restricted to Salesforce Personalization help, the Salesforce Personalization developer guide, the Salesforce Interactions SDK (Data 360) guide, Data 360 help, and release notes. MCP pages are cited only to explain differences.
- **Verification:** each reference file was researched from the documentation, then independently re-verified claim by claim, including an explicit check that every cited page belongs to Salesforce Personalization rather than MCP.

## Report a problem or contribute

- **Wrong or outdated fact:** open an issue with the **Incorrect or outdated fact** template. An official source link is required.
- **Missing topic:** use the **Missing topic** template.
- **Changes:** follow [CONTRIBUTING.md](CONTRIBUTING.md). Every pull request runs `scripts/validate_skill.py`.

## Disclaimer

A community knowledge base, not official Salesforce documentation. Salesforce documentation remains authoritative, and features, limits and UI labels change with each release. The skill contains no customer data and no forward-looking statements.

Maintained by [@Lior-SF](https://github.com/Lior-SF).

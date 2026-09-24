# SP Data360 Mastery

## TL;DR

- **What:** an open [Agent Skill](https://agentskills.io) (`SKILL.md` plus reference files) that turns an AI agent into a Salesforce Personalization (Data 360 / Marketing Cloud Next) expert. The same folder works in any client that loads that format, including Cursor, Claude Code, GitHub Copilot, Codex, and Gemini CLI. The full client list is at [agentskills.io/clients](https://agentskills.io/clients).
- **Why trust it:** every documented fact cites current official Salesforce docs, and every file was independently re-verified. Lessons from real implementations that the docs don't state are labeled `(Field-observed, undocumented)`.
- **Guards against the #1 mistake:** answering with Marketing Cloud Personalization (Interaction Studio / Evergage) knowledge.
- **Use it for:**
  - jump-starting a new customer (discovery, architecture by site type and channel, setup order, go-live)
  - Web SDK and sitemaps, WPM, decisions and recommenders
  - identity resolution, consent, attribution and reporting SQL
  - troubleshooting
- **Install (shared folder):**

  ```bash
  git clone https://github.com/Lior-SF/SP-Data360-Mastery.git ~/.agents/skills/sp-data360-mastery
  ```

  GitHub Copilot and Gemini CLI read that path. Cursor, Claude Code, and Codex use their own folders; the table below has each one. Then ask the agent about Salesforce Personalization.
- **Update:** `git -C ~/.agents/skills/sp-data360-mastery pull` (use the path you cloned into)
- **Found something wrong?** [Open an issue](https://github.com/Lior-SF/SP-Data360-Mastery/issues/new/choose) with an official source link.

## About

An open Agent Skill that makes AI agents expert in **Salesforce Personalization** — the Data 360–native personalization product sold with Marketing Cloud Next (formerly Einstein Personalization). It follows the [Agent Skills specification](https://agentskills.io/specification): one `SKILL.md` and a `references/` folder. Nothing in the skill is specific to Cursor or Claude.

Every platform fact comes from current official Salesforce documentation and is cited inline. The skill also guards against the most common failure mode: answering with **Marketing Cloud Personalization (MCP)** knowledge. MCP (formerly Interaction Studio / Evergage) is a different product with different objects, SDK behavior and reporting.

## What's inside

| File | Covers |
|---|---|
| [SKILL.md](SKILL.md) | Product guardrails, answer workflow, routing, and the facts agents most often get wrong |
| [references/implementation-playbook.md](references/implementation-playbook.md) | Jump-start for a new customer: discovery checklist, architecture choices by channel and site type, setup order, use-case patterns, measurement plan, go-live checklist |
| [references/platform-and-setup.md](references/platform-and-setup.md) | Architecture, licensing, permissions, Personalization Setup, DMOs, limits, feature timeline |
| [references/data-360-foundations.md](references/data-360-foundations.md) | Data 360 data layer for personalization: data stream → DSO → DLO → DMO, mapping, identity DMOs, match and reconciliation rules, resolution outputs, data graphs, data-layer QA queries |
| [references/web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md) | Salesforce Interactions SDK, sitemap, consent, identity, Personalization module, flicker defense, Decisioning API |
| [references/sitemap-templates.md](references/sitemap-templates.md) | Copy-ready multi-page / server-rendered starter sitemap, CMP-agnostic consent adapter, optional SPA add-on, catalog/cart/order event formats |
| [references/decisioning.md](references/decisioning.md) | Profile and item data graphs, personalization points, content schemas, decisions, targeting rules, recommenders |
| [references/wpm-experiences-campaigns.md](references/wpm-experiences-campaigns.md) | Web Personalization Manager, experience templates, personalization campaigns, experimentation |
| [references/measurement-and-attribution.md](references/measurement-and-attribution.md) | Engagement signals and metrics, attribution, Pipeline and Attribution Intelligence, reporting |
| [references/mobile-and-channels.md](references/mobile-and-channels.md) | Engagement Mobile SDK, server-side decisioning, batch decisions, Agentforce, Einstein Studio |
| [references/sp-vs-mcp.md](references/sp-vs-mcp.md) | How to tell Salesforce Personalization and MCP apart, and what never to say about SP |
| [references/troubleshooting.md](references/troubleshooting.md) | Symptom → cause → confirm → fix playbook |
| [references/sql-cookbook.md](references/sql-cookbook.md) | Data 360 SQL for personalization reporting |
| [references/field-guide-web.md](references/field-guide-web.md) | Field-verified web lessons the docs don't state: consent wiring, browser identity capture, sitemap engineering, SPA hardening, WPM anchors, offline sitemap testing |
| [references/field-guide-data.md](references/field-guide-data.md) | Field-verified data lessons the docs don't state: identity resolution design, connector mapping traps, child-record targeting, SQL diagnosis, credits, rollout, privacy sign-offs |

## Install

Clone into a folder named `sp-data360-mastery` so the folder matches the skill's `name`. The files are the same for every client. Only the parent directory changes.

**Shared path** (GitHub Copilot and Gemini CLI both read this)

```bash
git clone https://github.com/Lior-SF/SP-Data360-Mastery.git ~/.agents/skills/sp-data360-mastery
```

For one project, clone into `.agents/skills/sp-data360-mastery` at the repo root. Commit that folder if the team should share the skill.

| Client | All your projects | This project only |
|---|---|---|
| Cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| GitHub Copilot | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/`, `.agents/skills/`, or `.claude/skills/` |
| Codex | `~/.codex/skills/` | `.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |

Cursor also loads skills placed in the Claude and Codex directories. Gemini CLI can install from the git URL:

```bash
gemini skills install https://github.com/Lior-SF/SP-Data360-Mastery.git --consent
```

Other products on the [client list](https://agentskills.io/clients) use the same `SKILL.md`. Put the clone in the skills directory that product documents.

An agent that does not discover skills on its own can still use the repo: clone it anywhere and tell the agent to read `SKILL.md` and follow it, opening a file under `references/` only when `SKILL.md` routes there.

A web chat with no skill upload and no access to the clone will not pick this up by itself. Claude.ai and Cowork load skills enabled on the claude.ai account, not the `~/.claude/skills/` folder on your machine.

## Update

```bash
git -C ~/.agents/skills/sp-data360-mastery pull
```

Use the path you cloned into. Releases are tagged (`v1.0.0`, …); see [CHANGELOG.md](CHANGELOG.md) for what changed.

## How it works

- Clients that implement Agent Skills load the skill when a prompt matches the description in `SKILL.md`.
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

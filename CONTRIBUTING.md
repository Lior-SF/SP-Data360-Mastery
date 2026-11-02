# Contributing

This skill is only useful if agents can trust it. Every change must keep it accurate, product-correct and safe to publish.

## Ground rules

1. **Salesforce Personalization, not MCP.** Salesforce Personalization (SP) is the Data 360–native product sold with Marketing Cloud Next. Marketing Cloud Personalization (MCP, formerly Interaction Studio / Evergage) is a different product. Never describe MCP behavior as SP behavior. MCP belongs in [references/sp-vs-mcp.md](references/sp-vs-mcp.md) and "MCP confusion traps" sections. Anywhere else, label an MCP citation "MCP" on the same line. The validator also accepts any heading (level 1 to 3) that says "MCP", and it checks `SKILL.md`, `README.md`, `CONTRIBUTING.md` and `references/`.
2. **Cite official sources.** Every non-obvious fact ends with `[src](url)` pointing at an official page (`help.salesforce.com` or `developer.salesforce.com`). Workshop sources (`partnerworkshops.salesforce.com`) and third-party sites are secondary: use them only as hints, and put `(workshop source)` or `(third-party)` on the same line. They don't count toward a file's 10 required citations.
3. **Label what isn't documented.** Use these labels exactly:

   | Label | Meaning |
   |---|---|
   | `(UNVERIFIED)` | Useful, but not confirmed in documentation or by a test |
   | `(Field-observed, undocumented)` | Seen in real implementations, absent from documentation |
   | `(Field-verified)` | Confirmed by testing in an org, not stated in documentation |
   | `(inference)` | Reasoned from cited documentation, not stated by it |
   | `(workshop source)` / `(third-party)` | Secondary source, see rule 2 |
   | `(verbatim)` / `doc sample (verbatim)` | Copied from an official page or sample |
4. **Publish nothing private.** The repository is public. Never add:
   - customer or project names, websites or page names
   - org IDs, tenant hosts or record IDs
   - credentials
   - email addresses
   - internal conversations or named employees
   - roadmap or forward-looking statements

   Use placeholders such as `<POINT_ID>`, `<POINT_API_NAME>`, `<TENANT_ENDPOINT>`, `<TARGET_SELECTOR>`, `<TEMPLATE_API_NAME>`, `<SIGNAL_METRIC_NAME>`, `<REGISTRABLE_DOMAIN>`, `<CMP_NAME>`, `<PAGE_TYPE>`, `<DATA_SPACE>`, `<ID_NAME>` and `<ID_TYPE>`.

## Which sources count

| Source | Authoritative for SP? |
|---|---|
| Salesforce Help articles under **Salesforce Personalization** (`id=mktg.persnl_…`, `id=mktg.mc_persnl_…`) | Yes |
| Salesforce Personalization developer guide (`developer.salesforce.com/docs/marketing/einstein-personalization/…`) | Yes |
| Salesforce Interactions SDK guide (`developer.salesforce.com/docs/data/salesforce-interactions-sdk/…`) | Yes |
| Data 360 help (data graphs, calculated insights, identity resolution, reports) and release notes | Yes |
| Salesforce Help articles under **Marketing Cloud Personalization** (`id=mktg.mc_pers_…`) | No — MCP |
| MCP developer guide (`developer.salesforce.com/docs/marketing/personalization/…`) | No — MCP |

Watch the prefixes: `mc_persnl_` is SP, `mc_pers_` is MCP. Prefer the current release; when behavior changed, say so and name the release.

## Where knowledge goes

| Topic | File |
|---|---|
| Guardrails, routing, the most-missed facts | `SKILL.md` (keep under 500 lines) |
| New-customer discovery, architecture, setup order, use-case patterns, go-live | `references/implementation-playbook.md` |
| Setup, permissions, licensing, DMOs, limits | `references/platform-and-setup.md` |
| Documented Data 360 data layer: streams, DLOs, DMOs, mapping, identity DMOs, rulesets, match and reconciliation rules, unified outputs, data graphs, data-layer QA SQL | `references/data-360-foundations.md` |
| Web SDK, sitemap, consent, identity, Decisioning API | `references/web-sdk-and-sitemap.md` |
| Sitemap templates (multi-page starter, CMP adapter, SPA add-on), event formats | `references/sitemap-templates.md` |
| Data graphs, points, content schemas, decisions, recommenders | `references/decisioning.md` |
| Decisions through the Connect API: endpoints, input schema, rule-tree JSON, GET-to-PUT conversion, headless authoring workflow, decision QA, data graph record lookup | `references/headless-decisions.md` |
| Calculated, streaming and real-time insights: which type, SQL rules, adding to a data graph, use in targeting rules, merge fields and recommenders | `references/calculated-insights.md` |
| WPM, experience templates, campaigns, experiments | `references/wpm-experiences-campaigns.md` |
| Engagement signals, attribution, analytics, reporting | `references/measurement-and-attribution.md` |
| Mobile, server-side, batch, Agentforce | `references/mobile-and-channels.md` |
| SP vs MCP differences | `references/sp-vs-mcp.md` |
| Failure modes and fixes | `references/troubleshooting.md` |
| SQL patterns | `references/sql-cookbook.md` |
| Field-verified web lessons not in the docs (consent wiring, browser identity, sitemap engineering, SPA, WPM anchors, sitemap tests) | `references/field-guide-web.md` |
| Field-verified data and operations lessons not in the docs (identity resolution, connector mapping, targeting, SQL diagnosis, credits, rollout, privacy) | `references/field-guide-data.md` |

Keep each reference file at 500 lines or fewer (the validator fails above 500) and link every reference file directly from `SKILL.md`.

Field lessons must be:
- **Generic:** no customer, site, page, identifier, consent-category or tenant names; conditional wording for site-type-specific advice ("If the site is an SPA…").
- **Labeled:** `(Field-observed, undocumented)` unless a doc states it, with `[src](url)` on the documented building blocks it relies on.
- **Reproducible:** state the check that shows the behavior (console, network, SQL or UI path) so others can re-test it after an SDK upgrade or release.

When a field lesson only refines a topic that already lives in another reference, add a one-line pointer there instead of duplicating it.

## Style

- Write for an expert reader: dense, scannable, no filler.
- Put exact UI labels, API names and field names in backticks, copied verbatim.
- Use one term per concept. Say:
  - "Salesforce Personalization (SP)" and "Marketing Cloud Personalization (MCP)"
  - "Data 360" (formerly Data Cloud)
  - "content schema" (formerly response template)
  - "Dynamic Content" (formerly Manual Content)
  - "personalization point", "decision", "targeting rule", "experience", "WPM"
- Tag SQL `field-verified` only if it ran in an org, otherwise `doc-derived (untested)`. SQL copied from an official page is `doc sample (verbatim)`.

## Workflow

1. Create a branch.
2. Edit, citing a source for every fact.
3. Run the validator:

   ```bash
   python3 scripts/validate_skill.py --strict
   ```

   To block customer names locally, list them one per line in `~/.config/sp-data360-mastery/customer-terms.txt`. This file lives **outside** the repository. The validator also reads `.customer-terms.txt` in the repository root as a fallback (git-ignored, never commit it), and `--terms-file <path>` replaces both defaults. Don't keep a terms file inside the skill folder, and don't zip or copy that folder with one inside. Add `--require-terms` to fail when no terms were loaded.

   CI runs the same command with `--strict`. It reads the terms from the `BANNED_TERMS` repository secret, and adds `--require-terms` when that secret exists. Pull requests from forks get no secrets, so they run **without** the customer-term check. A maintainer must run it locally before merging them.
4. Add an entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md).
5. Open a pull request and complete the checklist. CI must pass, and a code owner reviews it.

## Releases

After each Salesforce release (Spring, Summer, Winter):

1. Re-verify limits, UI labels and new features against the release notes.
2. Update the baseline release everywhere it is stated:
   - `README.md` (Accuracy model)
   - `SKILL.md` (the baseline sentence in "Live verification and source rules")
   - the release placeholder in `.github/ISSUE_TEMPLATE/incorrect-fact.yml`
   - the `release=` pins in `[src]` links and the "Baseline" lines in the reference files
3. Move `Unreleased` entries into a new version in `CHANGELOG.md`, following semantic versioning:
   - **major:** restructured files
   - **minor:** new knowledge
   - **patch:** corrections
4. Tag the version (`git tag vX.Y.Z && git push --tags`) and publish a GitHub release.

## What is checked, and by whom

The validator (`scripts/validate_skill.py`) checks:
- `SKILL.md` frontmatter, name, description length (1024 characters at most) and length (500 lines at most)
- relative links and `#anchors`, and `§N` cross-references (including `web §` and `data §` for the field guides)
- every reference file is linked from `SKILL.md` and listed in the README, this file and the issue template
- reference size (500 lines at most) and at least 10 official `[src]` citations per file
- MCP pages are cited only where the MCP rule above allows
- credentials, tenant hosts, org and record IDs, email addresses and private customer terms, in every text file

Reviewers check what the validator can't:
- every non-obvious fact has a source, and the source says what the text says
- labels are used correctly (rule 3), and SQL tags are honest
- terminology (see Style), and no roadmap or forward-looking statements
- no personal names other than the maintainer, and no hints of a specific customer or use case

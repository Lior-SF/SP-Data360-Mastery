# Contributing

This skill is only useful if agents can trust it. Every change must keep it accurate, product-correct and safe to publish.

## Ground rules

1. **Salesforce Personalization, not MCP.** Salesforce Personalization (SP) is the Data 360–native product sold with Marketing Cloud Next. Marketing Cloud Personalization (MCP, formerly Interaction Studio / Evergage) is a different product. Never describe MCP behavior as SP behavior. MCP belongs in [references/sp-vs-mcp.md](references/sp-vs-mcp.md) and "MCP confusion traps" sections; anywhere else, an MCP citation must be explicitly labeled "MCP" on the same line.
2. **Cite official sources.** Every non-obvious fact ends with `[src](url)` pointing at an official page.
3. **Label what isn't documented.** Use `(UNVERIFIED)` for unconfirmed statements and `(Field-observed, undocumented)` for behavior seen in real implementations but absent from documentation.
4. **Publish nothing private.** The repository is public. Never add:
   - customer or project names, websites or page names
   - org IDs, tenant hosts or record IDs
   - credentials
   - internal conversations or named employees
   - roadmap or forward-looking statements

   Use placeholders such as `<POINT_ID>`, `<POINT_API_NAME>`, `<TENANT_ENDPOINT>`, `<TARGET_SELECTOR>`, `<TEMPLATE_API_NAME>` and `<SIGNAL_METRIC_NAME>`.

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
| Web SDK, sitemap, consent, identity, Decisioning API | `references/web-sdk-and-sitemap.md` |
| Sitemap templates (multi-page starter, CMP adapter, SPA add-on), event formats | `references/sitemap-templates.md` |
| Data graphs, points, content schemas, decisions, recommenders | `references/decisioning.md` |
| WPM, experience templates, campaigns, experiments | `references/wpm-experiences-campaigns.md` |
| Engagement signals, attribution, analytics, reporting | `references/measurement-and-attribution.md` |
| Mobile, server-side, batch, Agentforce | `references/mobile-and-channels.md` |
| SP vs MCP differences | `references/sp-vs-mcp.md` |
| Failure modes and fixes | `references/troubleshooting.md` |
| SQL patterns | `references/sql-cookbook.md` |
| Field-verified web lessons not in the docs (consent wiring, browser identity, sitemap engineering, SPA, WPM anchors, sitemap tests) | `references/field-guide-web.md` |
| Field-verified data and operations lessons not in the docs (identity resolution, connector mapping, targeting, SQL diagnosis, credits, rollout, privacy) | `references/field-guide-data.md` |

Keep each reference file under 500 lines and link every reference file directly from `SKILL.md`.

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
- Tag SQL `field-verified` only if it ran in an org, otherwise `doc-derived (untested)`.

## Workflow

1. Create a branch.
2. Edit, citing a source for every fact.
3. Run the validator:

   ```bash
   python3 scripts/validate_skill.py
   ```

   To block customer names locally, list them one per line in `.customer-terms.txt`. The file is git-ignored and must never be committed. CI reads the same list from the `BANNED_TERMS` repository secret.
4. Add an entry under `Unreleased` in [CHANGELOG.md](CHANGELOG.md).
5. Open a pull request and complete the checklist. CI must pass, and a code owner reviews it.

## Releases

After each Salesforce release (Spring, Summer, Winter):

1. Re-verify limits, UI labels and new features against the release notes.
2. Update the baseline release in `README.md`.
3. Move `Unreleased` entries into a new version in `CHANGELOG.md`, following semantic versioning:
   - **major:** restructured files
   - **minor:** new knowledge
   - **patch:** corrections
4. Tag the version (`git tag vX.Y.Z && git push --tags`) and publish a GitHub release.

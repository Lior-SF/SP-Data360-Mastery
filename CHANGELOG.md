# Changelog

Notable changes to this skill. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.1] - 2026-09-24

### Changed

- `SKILL.md` routing: an explicit identity resolution row. Questions about rulesets, match rules, party identification, unification timing, reruns and reconciliation now go straight to `field-guide-data.md` §1, the identity events in the Web SDK reference and the identity SQL checks.

## [1.2.0] - 2026-09-24

Field-knowledge release. It captures lessons verified in production implementations that the official docs don't state, written generically and labeled "Field-observed, undocumented" unless a doc confirms them.

### Added

- `references/field-guide-web.md`: field-verified web lessons that the docs don't state:
  - consent wiring: CMP adapter sources and precedence, cookie parsing, empty and unparseable answers, persistent listeners, ceiling sizing, handler order, replay guards, memos written only after transmission, consent categories as a profile attribute
  - identity capture in the browser: auth-signal probing, byte-for-byte identifiers, append-only data layers with positional logout suppression, login bursts, intent-armed logout, persisted binding, storage-key versioning, cross-tab staleness, memos keyed to the anonymous ID, re-sends after rotation
  - sitemap engineering: page types vs eligibility, segment-boundary and hostname matching, locale handling, guarded module initialization, `.catch` on `init()`, version banner, re-injection safety
  - SPA hardening, WPM anchors, and offline sitemap testing (scenario harness, stub fidelity, mutation self-test, versioned test assets)
- `references/field-guide-data.md`: field-verified data and operations lessons:
  - identity resolution design: party identifiers, the cross-object "Match to" pitfall, case sensitivity, limits, real-time prerequisites, full-rerun triggers and batching, pre-run checks, Is Anonymous, reconciliation
  - website connector schema and mapping traps: Sync Schema and Add Events, optional-only schema changes, refresh modes, automapping, Replace Mapping, event-group `eventType`, envelope fields, `deviceId` mappings
  - child-record targeting (`Count` > `0`), data graph edits, SQL diagnosis and a web-to-CRM acceptance query
  - credits, rollout and UAT practice, and privacy decisions that need sign-off
- Both guides registered in `SKILL.md` (routing row and a "Field-verified lessons" summary), `README.md`, `CONTRIBUTING.md` (with a rule that field lessons must be generic, labeled and reproducible) and the incorrect-fact issue template. Existing references gained one-line pointers or short fixes where the topics already live: Web SDK, sitemap templates, troubleshooting (including a new "content shows for some users only" symptom), implementation playbook, platform and setup, decisioning, WPM, measurement and SQL cookbook.
- WPM bookmarklet: Google Chrome steps in `references/wpm-experiences-campaigns.md`, a troubleshooting symptom for `?sf_personalization_wpm` doing nothing or erroring on launch, and the bookmarklet fallback under "Opening WPM" in `SKILL.md`.

### Changed

- Opt Out correction: `references/web-sdk-and-sitemap.md` §3 and `references/sitemap-templates.md` §3 no longer say that an explicit init-time `Opt Out` records an opt-out for undecided visitors. Consent Log rows are documented only for the first event after opt-in and on revocation, so whether that `Opt Out` writes a row is now marked undocumented.

## [1.1.0] - 2026-09-24

Generality and QA release. A blind QA ran 24 new-customer questions against v1.0.1 using only the skill, and independent graders checked every answer against the official docs. This release applies the fixes, and a regression QA of 10 questions confirmed no bias toward single-page apps, banners, industries or any past customer.

### Added

- `references/sitemap-templates.md`: a multi-page / server-rendered starter sitemap as the primary template (no polling, no `reinit()`), a CMP-agnostic consent adapter with vendor calls as placeholders, an optional SPA add-on for client-side routing only, and the documented catalog, cart, order and identity event formats with their landing DMOs. Registered in `SKILL.md`, `README.md`, `CONTRIBUTING.md` and the incorrect-fact issue template.

### Changed

- De-biased web guidance toward multi-page sites: `SKILL.md` site-type table (each site type gets its own guidance; SPA handling is an optional add-on), new facts (`reinit()` is for virtual navigation, with two narrow one-time exceptions, documented commerce events, first-event identity rule), a routing row for the templates and a checklist item for architecture, industry and item type.
- Web SDK and sitemap: the SPA-flavored annotated sitemap replaced by a link to the templates; tag placement and `cookieDomain` guidance; CMP adapter summary; commerce event summary; `Order Item` mapping note for Maximize Revenue; first-event identity consequence; an architecture → rendering-method table in §9.
- Troubleshooting: triage snippet no longer calls `reinit()`; new "multi-page site records duplicate page views or decisions" symptom; the first-view consent replay marked optional on multi-page sites.
- Decisioning: targeting-rule operator note, per-request context scope (UTM captured from the current URL only; MCP `UTM Parameter Mapping` has no SP counterpart), `anchorType` and context-variable operator support.
- Platform and setup: Card recommender limit attributed to the limits page, add-on naming variants; WPM permission-set conflict quoted from both pages and aligned with `wpm-experiences-campaigns.md`.

- `SKILL.md`: channel-neutral feedback model and engagement ↔ log join; license channel test; MCP migration facts; frequency capping described as a pattern; experiment rollout and rate-metric notes; connector-level engagement tracking; profile-extension wording without loyalty assumptions; frontmatter description trimmed under the 1,024-character limit.
- Measurement: every standard engagement DMO with a Personalization Log foreign key, a non-web attribution pattern, a corrected Pipeline Intelligence statement, dashboard notes and neutral recipe placeholders.
- Platform and setup: license channel test, the engagement DMO list, and Data 360 consent controls for server-side and batch decisions.
- Mobile and channels: mobile landing DMO, a server-side caller checklist, and the batch → Marketing Cloud Engagement activation, scheduling and ID mapping.
- Decisioning: Account/B2B design options, the calculated-insight inclusion rule, the targeting-operator caveat, a "recently viewed" recipe and a frequency-capping pattern (§8.1).
- WPM and experiments: overlay gaps, template-type note, primary-metric eligibility, participant counts and winner rollout.
- SQL cookbook: how to switch the engagement source, plus a Recommendations query (Q4b).
- SP vs MCP: the MCP catalog export is sandbox-only, and the MCP connector has no profile backfill.
- Experience Cloud: the "UNVERIFIED" path replaced with the documented options (Aura Web SDK via header markup and Relaxed CSP, the enhanced LWR native Data Cloud integration with `set-consent`, Agentforce Orchestrator referencing SP points), discovery questions, an architecture row, a `SKILL.md` site-type row and narrower gap wording (WPM and SP rendering on Experience Cloud stay undocumented).
- Server-side decisions: no-profile requests with `ContextOnly`, `unifiedIndividualId` for experiment partitioning and `correlationId` in the Web SDK Decisioning API section, the server-side caller checklist and the `SKILL.md` headless row.
- Server-side engagement: Data 360 Ingestion API streaming for view, click and outcome events in the server-side caller checklist, the measurement non-web pattern and the playbook.
- Consent: `getConsents()` entries read through `consent.purpose` / `consent.status`, and a caveat that a `consents` Promise resolving `[]` isn't a documented shape (Web SDK reference and sitemap template).
- Placeholders: banner-specific names replaced with `<TARGET_SELECTOR>`, `<POINT_API_NAME>`, `<TEMPLATE_API_NAME>` and `<SIGNAL_METRIC_NAME>` across references, troubleshooting and `CONTRIBUTING.md`.

## [1.0.1] - 2026-09-24

### Changed

- `SKILL.md` implementation defaults:
  - Real-time identity matching behavior: `Exact`, with `Exact Normalized` for phone and email; case sensitivity is opt-in.
  - The shared-device risk when a browser stays bound to a member after sign-out.
  - Consent compliance ownership, and the risk of mapping `Opt In` to an always-active category.

## [1.0.0] - 2026-09-24

### Added

- `SKILL.md` with the rules that keep answers on Salesforce Personalization rather than MCP, the answer workflow, routing, and the facts agents most often get wrong.
- Reference files, each researched from official documentation and then independently re-verified claim by claim:
  - platform and setup
  - Web SDK and sitemap
  - decisioning
  - WPM, experiences and campaigns
  - measurement and attribution
  - mobile and channels
  - SP vs MCP
  - troubleshooting
  - SQL cookbook
- `scripts/validate_skill.py` and a CI workflow that check structure, links, citations and publication safety.
- Issue templates, a pull request template and code owners.

[Unreleased]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Lior-SF/SP-Data360-Mastery/releases/tag/v1.0.0

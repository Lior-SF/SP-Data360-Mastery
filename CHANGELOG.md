# Changelog

Notable changes to this skill. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.8.1] - 2026-10-08

### Changed

- `references/headless-decisions.md` §2, §6 and the gaps list: how `PUT` treats `decisions[]` is now field-verified. Sending every existing decision plus a new one adds it. An existing decision sent back under the same `name` keeps its `id` and `createdDate`. A body that omits an existing decision is rejected as a whole (`You cannot update records for the PersonalizationPoint object.`). A decision without `targetingRules` reads back as `null`. Still open: matching by name or position, deleting through the API, and priority on write.

## [1.8.0] - 2026-10-08

### Added

- `references/headless-decisions.md`: a guide to reading, QA'ing and writing a personalization point's decisions through the Connect REST API, without the decision wizard.
  - Endpoints, the v67.0 requirement for `targetingRules`, raw output with `X-Chatter-Entity-Encoding: false`, and the `_HttpMethod` override.
  - The documented `PersonalizationPointInput` schema: decision, attribute-value and merge-field inputs, enums and constraints.
  - The rule tree written through `PUT` and rendered in the wizard (Field-verified), with a generic example.
  - Converting a `GET` response into a `PUT` body: `contextName` and read-only keys are rejected or not in the input schema (Field-verified), plus a small converter script.
  - A safe workflow (test point, backup, full decision list, `Draft` first, Test Mode check), the QA checklist, and open questions: replace vs merge, priority on write, decision IDs on update.

### Changed

- The decision JSON section added to `references/field-guide-data.md` §3.1 in 1.7.0 moved to the new guide; `field-guide-data.md` §3, `decisioning.md` §6.3 and §6.4, and `SKILL.md` point to it. Its "headless authoring (UNVERIFIED)" note is replaced by the field-verified `PUT` results.

## [1.7.0] - 2026-10-08

### Added

- `references/field-guide-data.md` §3.1: reading a personalization point's decisions as JSON through the Connect REST API (`GET`/`PUT`/`DELETE /personalization/personalization-points/{idOrName}`, `POST` to create), raw output with `X-Chatter-Entity-Encoding: false`, and a QA checklist for the decisions. The decision shape, the rule tree (`Group`, `Field`, `RelatedField`), the stored operator names seen and the `{{{<MERGE_FIELD_NAME>}}}` token form are labeled field-observed. Headless authoring with `PUT` is labeled unverified.
- Pointers from `references/decisioning.md` §6.3, §6.4 and the gaps list, and from `SKILL.md`.

## [1.6.1] - 2026-09-30

Repository review: the text added in 1.4.0 to 1.6.0 was fact-checked independently against the release 264 documentation, and the gaps it found are fixed.

### Fixed

- **Wrong claim from 1.5.1.** `references/field-guide-data.md` §1.4 and `references/field-guide-web.md` §1.3 said the Data 360 Web SDK connector mapping sends the `identity` event's `dateTime` to Individual Last Modified Date. Both documented mappings send it to Created Date only. Mapping it to Last Modified Date as well stays, now labeled as an addition to the documented mappings (Field-observed).
- `references/calculated-insights.md`, `SKILL.md`, `references/decisioning.md`, `references/sql-cookbook.md`:
  - Real-time insights: the 264 pages document `Sum` and `Count` only, while a 262 release note adds `Min` and `Max` (June 2026). The skill now states the conflict and says to check the builder.
  - Streaming insights can be added to a data graph (the skill said this was undocumented). Only how a decision evaluates them is undocumented.
  - A calculated insight is described as scheduled, which SP calls "near real time", instead of just "batch".
  - The "profile graph must be real-time" wording on one SP page is flagged as stale, as in `decisioning.md` §1.2.
  - Citations moved to the pages that state the fact: the limits page (4 nested insights, 30 manual runs per 24 hours, streaming sources), the relative-time page (365+ day windows), the create-graph page (refresh intervals) and the streaming-insight page (the `Processing` status).
  - Edit rules are split into measures and dimensions. Unlabeled reasoning is tagged `(inference)`.
- `references/field-guide-data.md`:
  - The `cdp_sys_*` device fields are documented on the connector mapping page, so they're no longer labeled field-observed.
  - The same-source Source Priority fallback is stated exactly, and Ignore Empty Values is described as documented only for `Most Frequent` and `Source Priority`.
- `references/field-guide-web.md` §1.3: the related Individual node behavior is labeled `(inference)`.
- `references/troubleshooting.md`: lookup-key formats for the `cdpGetDataGraphByLookup` Flow action are documented (an unbracketed example on the Flow page, bracketed forms for Apex and the Query API); only "both bracketed keys worked" is field-observed. Added the documented fallback from a real-time graph to the standard graph, and `noCache`, as a check when a lookup looks stale.
- `references/platform-and-setup.md`: the `PersonalizationSchema` object reference is now a source for the shared platform-event and sharing objects.

### Added

- `scripts/validate_skill.py` checks that every reference file is listed in the README, `CONTRIBUTING.md` and the "Incorrect or outdated fact" issue template, and that cross-references such as `decisioning.md §1.6` point at real numbered headings.

### Changed

- `SKILL.md` description names calculated and real-time insights.
- `README.md` adds insights to "Use it for", documents the `(inference)` label and states what was independently verified.
- `CONTRIBUTING.md` and the issue template list `references/calculated-insights.md`.

## [1.6.0] - 2026-09-30

### Added

- `references/calculated-insights.md`, a consolidated guide to calculated, streaming and real-time insights with data graphs in Salesforce Personalization:
  - which insight type to use, and why a calculated insight isn't for real-time decisions;
  - SQL authoring rules, data-space naming, schedule behavior, validation, and the narrow edit rules;
  - real-time insight authoring, approximate time windows, and the data subject rights lag;
  - adding an insight to a profile or item graph (root only, primary key as a dimension, 5 measures, array shape) and why freshness is two clocks;
  - use in targeting rules, merge fields (sort criteria) and rule-based recommenders, with the Top Sellers and Co-Bought patterns;
  - a decision table, limits, cost, a list of behaviors to test before promising them, and a troubleshooting checklist.
- `references/troubleshooting.md`: new symptom for a calculated insight that is missing, stale or empty in a rule or merge field.

### Changed

- `SKILL.md`: routing row and an "Insights" facts section; the measurement row now covers reporting insights only.
- `README.md`, `references/decisioning.md`, `references/measurement-and-attribution.md`: pointers to the new guide.

## [1.5.2] - 2026-09-29

### Changed

- `references/field-guide-web.md` §1.3 (consent categories as a profile attribute):
  - A text **Contains** condition on the root consent field is available and works in the decision wizard.
  - Put the consent field on the Unified Individual root and target that field. The related Individual node lists every browser's row, so a condition there matches if any browser ever granted the category.
  - Step 5 points to the `dateTime` → Last Modified Date mapping that `Last Updated` needs.
  - The pattern is verified end to end: a consent change on one browser reached the real-time root value and the decision within seconds.

## [1.5.1] - 2026-09-29

### Changed

- `references/field-guide-data.md` §1.4:
  - `Last Updated` picks the latest record by Last Modified Date, needs that field mapped from the stream, and breaks ties alphabetically.
  - Map the web `identity` event's `dateTime` to Individual Last Modified Date as well as Created Date. (Corrected in 1.6.1: this isn't what the Data 360 Web SDK connector mapping does; it maps `dateTime` to Created Date only.) Without it, the unified consent showed the alphabetically first value. With it, the real-time root followed the latest browser.
  - `Last Updated` compares records and has no Ignore Empty Values, so check that a nightly-refreshed CRM record without the field can't blank it, or use Source Priority with the web stream first.
- `references/troubleshooting.md`: read the real-time graph record with the **Data Cloud Get Data Graph By Lookup** Flow action (lookup key formats that worked), and compare Query Editor, the Data Graph view and the real-time lookup when they disagree.

## [1.5.0] - 2026-09-28

### Added

- Field-verified consent and sign-in freshness lessons:
  - `references/field-guide-web.md` §2.4: the profile upsert sent with the sign-in bind doesn't reach the unified profile, so re-send it once the device is linked; refresh decisions after a new sign-in or an in-place sign-out, with the cases to skip; label refresh page events through `onActionEvent` by returning a copy.
  - §1.2: refresh decisions once after a consent change, debounced against duplicate CMP events.
  - §1.3: gating display on the browser's live consent, upgraded from inference to verified (fails closed, no `personalization-view` while hidden).
  - `references/field-guide-data.md` §1.2: test members accumulate devices past the data graph's 100-record default, and the unified value is reconciled across all of them.
  - `references/troubleshooting.md`: a "consent change or sign-in isn't reflected in the decision" symptom.
  - A `SKILL.md` summary line.

### Changed

- Author named as Lior Omri in `LICENSE`, the README and `SKILL.md` metadata.
- `README.md`: an "Example prompts" section grouped by task, and a sample prompt in the TL;DR.

## [1.4.4] - 2026-09-24

### Added

- MIT `LICENSE`, `license: MIT` in the `SKILL.md` frontmatter, and a license line in the README.

## [1.4.3] - 2026-09-24

### Changed

- `README.md`: the skill is the open Agent Skills format, not a Cursor or Claude Code plugin. Install instructions cover the shared `~/.agents/skills/` path plus Cursor, Claude Code, GitHub Copilot, Codex, and Gemini CLI.

## [1.4.2] - 2026-09-24

### Fixed

- Fact and consistency corrections from the 2026-09-24 audit:
  - Data graph cap is 25 standard plus 25 real-time everywhere.
  - `dataCloud.timeTracking` is a documented `init` option.
  - Website connector wait time cites both the 15-minute / 1-hour ingest page and the 2–3 minute (300 ms real-time) limits row, and records that they disagree.
  - The copy-ready sitemap always calls `updateConsents()` first, keys the identity memo to `getAnonymousId()`, and sends `IDNameWeb`.
  - Recommendation default (12) vs maximum (24), diagnostic `511` vs `512`, calculated-insight measure scope, and Personalization Log `std__*` field API names.
  - Dynamic Content and content schema used as the current names.

## [1.4.1] - 2026-09-24

### Changed

- `README.md`: a TL;DR section at the top covering what the skill is, why to trust it, what to use it for, a one-line install, updating and reporting issues.

## [1.4.0] - 2026-09-24

### Added

- Test-experience hygiene:
  - `references/wpm-experiences-campaigns.md`: the risk of leftover `Enabled` POC or test experiences, naming conventions, the pre-go-live sweep with `Show All Personalization Experiences`, returning test decisions to `Draft`, a data check through the Personalization Log, and an experience register.
  - Also a go-live checklist item in `references/implementation-playbook.md`, an "old, test or unexpected content appears" symptom in `references/troubleshooting.md`, and a summary under WPM in `SKILL.md`.

## [1.3.0] - 2026-09-24

### Added

- `references/data-360-foundations.md`: the documented Data 360 data layer SP depends on (data stream → DSO → DLO → DMO, categories, refresh modes, formula fields, mapping rules, naming, data spaces), the identity DMOs and web identity mappings, rulesets, match methods and advanced settings, real-time matching, unified and link outputs, consolidation rate, reconciliation rules and their effect on targeting, data graphs, a stage-by-stage QA checklist with `doc-derived (untested)` SQL, and generic field lessons. Routed from `SKILL.md` (new row and the identity resolution row), README, CONTRIBUTING and the incorrect-fact issue template.

### Changed

- Consistency fixes from the verification pass:
  - `Exact` matching ignores letter case unless `Case Sensitive` is on (`field-guide-web.md`), and the Help and Apex API docs disagree on that setting's scope (`field-guide-data.md`).
  - The real-time Unified Individual graph requirement is scoped to WPM, with the doc disagreement noted (`web-sdk-and-sitemap.md`).
  - Data graph limits are 25 standard plus 25 real-time (`implementation-playbook.md`).
  - Party is also mapped on the web email and phone contact points (`field-guide-data.md`).

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

[Unreleased]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.8.1...HEAD
[1.8.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.8.0...v1.8.1
[1.8.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.7.0...v1.8.0
[1.7.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.6.1...v1.7.0
[1.6.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.5.2...v1.6.0
[1.5.2]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.5.1...v1.5.2
[1.5.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.4.4...v1.5.0
[1.4.4]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.4.3...v1.4.4
[1.4.3]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.4.2...v1.4.3
[1.4.2]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.4.1...v1.4.2
[1.4.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.4.0...v1.4.1
[1.4.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.2.1...v1.3.0
[1.2.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Lior-SF/SP-Data360-Mastery/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Lior-SF/SP-Data360-Mastery/releases/tag/v1.0.0

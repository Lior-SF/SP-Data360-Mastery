---
name: sp-data360-mastery
description: >-
  Expert, citation-backed knowledge of Salesforce Personalization (SP), the
  Data 360-native personalization product in Marketing Cloud Next (formerly
  Einstein Personalization): setup, permissions and licensing, the Salesforce
  Interactions Web SDK and sitemap, consent and identity, profile and item data
  graphs, personalization points, content schemas, decisions, targeting rules,
  recommenders, Web Personalization Manager (WPM), experience templates,
  personalization campaigns, experiments, engagement signals, attribution,
  Personalization Intelligence dashboards, the Decisioning API, the Engagement
  Mobile SDK, batch decisions and Data 360 SQL reporting. Use when a prompt
  involves Salesforce Personalization, Data 360 or Data Cloud personalization,
  personalization points or decisions, WPM, sitemaps, engagement signals or
  attribution, and whenever an answer must be kept separate from Marketing Cloud
  Personalization (MCP, Interaction Studio, Evergage).
---

# SP Data360 Mastery

Answer Salesforce Personalization (SP) questions with verified, current facts. SP is the Data 360–native product sold with Marketing Cloud Next. It is **not** Marketing Cloud Personalization (MCP, formerly Interaction Studio / Evergage). Answering an SP question with MCP knowledge is the most common and most damaging error.

## Product guard: SP or MCP?

Decide which product the prompt is about before answering.

| Signal | Salesforce Personalization (SP) | Marketing Cloud Personalization (MCP) |
|---|---|---|
| Core objects | personalization points, decisions, targeting rules, content schemas, recommenders | campaigns, experiences, web templates, Einstein Recipes |
| Data layer | Data 360 DMOs, data graphs, identity resolution | MCP's own datasets and user profiles |
| Web authoring | Web Personalization Manager (WPM), experience templates built in the app | Visual Editor, template code (server-side/client-side) |
| Web SDK | Salesforce Interactions SDK with the Data 360 and Personalization modules | Evergage / Interactions beacon with MCP sitemap features |
| Help article IDs | `mktg.persnl_…`, `mktg.mc_persnl_…` | `mktg.mc_pers_…` |
| Developer guide | `…/docs/marketing/einstein-personalization/…`, `…/docs/data/salesforce-interactions-sdk/…` | `…/docs/marketing/personalization/…` |

- If the prompt mixes vocabularies ("Einstein Recipe for my personalization point"), say which product each term belongs to and map it to the SP equivalent using [references/sp-vs-mcp.md](references/sp-vs-mcp.md).
- `SalesforceInteractions`, "sitemap" and "content zone" exist in both products with different behavior. Never reuse MCP semantics for them.
- MCP-only features don't exist in SP: native frequency capping, Einstein Recipes, Gears and campaign template code. Don't claim SP has them. To cap frequency in SP, build a targeting rule over the visitor's view engagements.

## Answer workflow

1. **Scope.** Classify the prompt: SP, MCP, Data 360 platform, or another cloud. For MCP, say so and don't answer from this skill.
2. **Route.** Read only the reference file(s) the question needs (table below). For troubleshooting, always add [references/troubleshooting.md](references/troubleshooting.md).
3. **Verify volatile facts.** If Salesforce documentation tools are available (for example a Salesforce Docs MCP server), re-check limits, UI labels, licensing numbers and anything release-dependent against live docs. Follow the source rules below.
4. **Answer precisely.**
   - Use exact UI labels and API names, and give step sequences in order.
   - Cite the official page when you state a non-obvious fact.
   - Keep labels such as `(UNVERIFIED)` and `(Field-observed, undocumented)` when you repeat those statements.
5. **Don't invent.** If neither the references nor live docs cover something, say it's undocumented and give a concrete way to confirm it: a console check, a SQL query, a UI path, or a Support case.

## Routing

| Question is about… | Read |
|---|---|
| Licensing, credits, editions, permission sets, Personalization Setup, foundational data, Personalization DMOs, limits, feature timeline | [references/platform-and-setup.md](references/platform-and-setup.md) |
| Web SDK deployment, `init` options, consent, identity events, sitemap, SPA handling, flicker defense, Personalization module, auto view/click tracking, Decisioning API | [references/web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md) |
| Profile/item data graphs, personalization points, content schemas, decisions, targeting rules, merge fields, recommenders, real-time layer | [references/decisioning.md](references/decisioning.md) |
| WPM, display methods, experience templates, preview/publish, personalization campaigns, experiments and experimentation APIs | [references/wpm-experiences-campaigns.md](references/wpm-experiences-campaigns.md) |
| Engagement signals and metrics, attribution models, Attribution/Pipeline Intelligence, Tableau, Data 360 reports, calculated insights | [references/measurement-and-attribution.md](references/measurement-and-attribution.md) |
| Engagement Mobile SDK, server-side decisioning, batch decisions for segments, Agentforce, Einstein Studio | [references/mobile-and-channels.md](references/mobile-and-channels.md) |
| "Is this SP or MCP?", migration, terminology mapping | [references/sp-vs-mcp.md](references/sp-vs-mcp.md) |
| Anything broken: not rendering, duplicated, zero rows, save errors | [references/troubleshooting.md](references/troubleshooting.md) |
| SQL for views, clicks, CTR, unique or unified individuals, point/decision breakdowns | [references/sql-cookbook.md](references/sql-cookbook.md) |

## Mental model

```text
Data 360
  data streams -> DLOs -> DMOs -> identity resolution (Unified Individual)
  profile data graphs (standard | real-time), item data graphs, calculated insights, segments
        |
Personalization service
  personalization point = data space + profile data graph + personalization type + content schema
  decisions (priority order) -> targeting rules -> Dynamic Content attributes or recommender output
        |
Channels
  Web: Salesforce Interactions SDK + sitemap + WPM experiences (experience templates)
  Mobile: Engagement Mobile SDK      Server: Decisioning API      Batch: decisions for segments
        |
Feedback into Data 360
  personalization-view / personalization-click -> Website Engagement DMO
  decision records -> Personalization Log DMO
        |
Measurement
  engagement signals + metrics -> attribution models -> Attribution Intelligence
  Pipeline Intelligence (CRM Analytics) | Query Editor / calculated insights / Data 360 reports
```

## Facts agents most often get wrong

Each fact is detailed and cited in the linked reference.

### Platform and setup — [platform-and-setup.md](references/platform-and-setup.md)

- `Personalization Setup` has four tabs:
  - `Foundational Setup` deploys the Personalization DMOs, a log ingestion stream and two calculated insights (`Daily Personalization Uniques`, `Daily Personalization Requests`). Both insights must be scheduled manually and they consume credits.
  - `Data Graph Defaults`
  - `Use Case Setup`
  - `Advanced Setup`
- Permissions:
  - `Personalization Admin` and `Personalization User` are the two standard permission sets. `Personalization User` can't create engagement signals, attribution models or batch decisions.
  - Setup also requires adding `Access Personalization Platform` to the `Data Cloud Salesforce Connector` permission set.
  - Dashboards need `Personalization Intelligence User`.
- The billable unit is the personalization decision. License credit allowances and attribution-model quotas are in the reference.
- Renames:
  - content schema (formerly response template)
  - Dynamic Content (formerly Manual Content)
  - Data 360 (formerly Data Cloud)
  - Some API names still use the old terms.

### Web SDK and consent — [web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md)

- **Consent:** the Web SDK stores and sends nothing until it receives an explicit `Opt In`. `consents` is required in `init`, and `consents: []` means no tracking. MCP instead tracks by default.
  - The only documented purpose is `Tracking`; MCP's `Personalization` purpose doesn't apply.
- **Initialization order:** `SalesforceInteractions.Personalization.Config.initialize(...)` must run **before** `SalesforceInteractions.init(...)`.
- **Flicker defense defaults:** `redisplayTimeoutMilliseconds: 2000` and `renderPersonalizationAfterTimeoutElapsed: false`. A response that arrives after the timeout is not rendered.
- **`init` options:** documented options are `consents`, `cookieDomain` and, for SP, `personalization.dataspace`. Treat any other option as undocumented.
- **Where event data goes:**
  - Profile data belongs in `user.attributes`, with an `eventType` such as `identity`, `partyIdentification` or `contactPointEmail`.
  - Fields placed under `interaction.attributes` become engagement fields, so no contact point is created.
  - `user.identities` is MCP's identity model.
- **`isMatch`:** must return a boolean. MCP allows a Promise; in SP a returned Promise is truthy and matches every page.
- **Page type names:** a sitemap page type `name` is both the WPM `Current Page Type` binding and the `sourcePageType` on events. Renaming it silently breaks experiences and reports.
- **Fetching on the web:** call `SalesforceInteractions.Personalization.fetch([...])`; `fetchDecisions` is the mobile SDK method. Dynamic Content values arrive in each personalization's `attributes`, not in `data`.
- **Personalization events:** web renders emit `personalization-view` and `personalization-click` (`userEngagement`) into the Website Engagement DMO.
- **Decisioning API:** `POST https://{tenantSpecificEndpoint}/personalization/decisions`, with an authenticated variant. All points in one request must share a profile data graph, and overload returns HTTP 429.

### Decisioning — [decisioning.md](references/decisioning.md)

- **Standard vs real-time data graphs:** a point on a **standard** profile data graph skips the profile lookup and is evaluated against a blank anonymous profile unless the caller supplies profile data, so profile-based targeting rules evaluate false. Use a **real-time** profile data graph for live web targeting; WPM lists only points built on one.
- **Personalization type:** choosing a type fixes the point's shape: Recommendations (recommender output) or Dynamic Content (attributes stored on the decision; still `ManualContent` in the API).
- **Real-time graph joins:** real-time profile data graphs join child objects only through the parent object's primary key. Design loyalty and other profile data to relate to Individual or Unified Individual, not through Party Identification values.
- **Targeting context:** targeting rules can use request context as well as profile data: `Scheduling`, `Source`, `UTM Parameters` and `Visit Context` (page type).
- **Decision evaluation:** only `Live` decisions (not `Draft`) are evaluated, in priority order, and one decision is returned per point.
- **No default decision:** when nothing qualifies, an SP personalization point returns no decision and the diagnostic `NO_DECISION_QUALIFIED`. Build an explicit catch-all decision if the slot must never be empty. Marketing Cloud Next message dynamic content, unlike SP points, does have a default variation.
- **Documented limits:**
  - 25 decisions per point
  - 50 targeting conditions per decision
  - 10 recommenders per org
  - 12 recommendations returned by default, 24 maximum
  - 60,000 recommendation requests per minute per tenant
  - 20 active batch jobs per org

  The full table is in [platform-and-setup.md](references/platform-and-setup.md).

### WPM, campaigns, experiments — [wpm-experiences-campaigns.md](references/wpm-experiences-campaigns.md)

- **Opening WPM:** append `?sf_personalization_wpm` to the site URL; for sandboxes also add `&sf_personalization_wpm_env=prod_sandbox`. Third-party cookies must be allowed.
- **Display methods:** `Replace a Content Zone`, `Use Content Zone Handler`, `Replace an Element`, `Add Before an Element`, `Add After an Element` and `Add an Overlay`.
- **Selectors:** element targets are CSS selectors. An element that has only an `id` must be targeted as `#id`.
- **Publishing:** nothing goes live until `State` is `Enabled` and you `Save`. Previewing a specific decision ignores its targeting rules.
- **Experience templates:** since release 262 they are built in the app, not in the sitemap.
- **Campaigns:** personalization campaigns support Dynamic Content schemas on the web channel only.
- **Experiments:** Bayesian, with at least 1,000 participants per cohort. The first cohort is the control, and settings are locked after `Start`. `Winner Found` is a recommendation; you switch traffic manually.

### Measurement — [measurement-and-attribution.md](references/measurement-and-attribution.md)

- **Signals and the Personalization Log:** a signal can be an attribution funnel stage only if it has an active relationship to the Personalization Log DMO. Website Engagement has no personalization point field, so filter by point through the Personalization Log relationship.
- **Web connector schema:** the relationship joins Website Engagement `PersonalizationContentId` to the Personalization Log `Id`. If the event schema lacks `personalizationContentId`, or it isn't mapped to the Website Engagement DMO, views and clicks can't be attributed.
- **Funnels vs CTR:** attribution funnels are individual-based. The entrance stage counts individuals, and later stages count conversions within the attribution window. Funnel conversion differs from raw event click-through rate (CTR).
- **Custom attribution:** 2–4 stages, `First Touch` or `Last Touch`, per-org and per-data-space model limits. Predefined attribution needs the Product Browse, Shopping Cart and Product Order engagement objects.
- **CRM Analytics:** Pipeline Intelligence explicitly requires CRM Analytics. For the Attribution Intelligence `Analytics` tab, the dependency is neither documented nor excluded; its only listed permission is `Personalization Intelligence User`. Confirm in the target org.
- **Compound metrics:** only one COUNT metric divided by another (`Divide By`).
- **Reporting CTR:** Data 360 reports on calculated insights can't use formulas. Compute CTR in calculated insight SQL, Query Editor or Tableau.

## Implementation defaults

Apply these unless the user's constraints say otherwise; explain the trade-off when you deviate.

- **Placement:** ask the site team for a dedicated, stable, empty placeholder element with an `id`, and target it with WPM `Replace an Element`. Avoid anchors that exist only in some user states.
  - For framework-rendered components (React, Angular, Vue), SP recommends registering a Content Zone Handler so the framework, not DOM replacement, renders the content.
  - Don't also declare a sitemap content zone for the same slot; that creates two placement paths.
  - SP flicker defense hides the elements that enabled experiences target. The MCP behavior of hiding content-zone selectors doesn't apply.
- **SPAs:** call `reinit()` after the new route's DOM settles (debounce plus a hard ceiling), block concurrent calls, and make one-time patches idempotent so the sitemap can be re-injected safely.
- **Consent:** feed `consents` from the consent manager as a promise that always settles. Events before opt-in are dropped, so replay the first page view once after opt-in, and only if it was suppressed.
- **Identity:** `partyIdentification` `IDName`/`IDType` must match the identity resolution match rule exactly.
  - Never send placeholder values ("NA", "null") as identifiers.
  - Call `resetAnonymousId()` before binding a different member on the same device.
  - Real-time identity resolution runs only `Exact` or `Exact Normalized` match rules. Fuzzy rules take effect in the next scheduled run.
- **Templates:**
  - Scope CSS class names to the template.
  - Size from the container: `width: 100%; align-self: stretch`, and container queries rather than viewport breakpoints.
  - Hide empty variables.
  - Keep creative images consistent with the layout the template already draws.
- **Banner reporting:** a two-stage `personalization-view` → `personalization-click` attribution funnel, with signals filtered through the Personalization Log by point, reports a single banner. Use Query Editor or a calculated insight for raw event counts and CTR.

## Live verification and source rules (SP vs MCP)

When documentation tools are available, verify against sources in this order:

1. Salesforce Help articles under **Salesforce Personalization**: IDs `mktg.persnl_…` and `mktg.mc_persnl_…`.
2. The Salesforce Personalization developer guide: `developer.salesforce.com/docs/marketing/einstein-personalization/…`.
3. The Salesforce Interactions SDK guide (Data 360 module): `developer.salesforce.com/docs/data/salesforce-interactions-sdk/…`.
4. Data 360 help (data graphs, calculated insights, identity resolution, reports) and release notes (`rn_persnl_…`).

Pages under `developer.salesforce.com/docs/marketing/personalization/…` and help IDs `mktg.mc_pers_…` are **MCP**. Use them only to explain differences. The prefixes are one letter group apart: `mc_persnl_` is SP, `mc_pers_` is MCP. The baseline for this skill is release 264 (Winter '27); if live docs differ, trust live docs and say what changed.

## Answer quality checklist

- [ ] The answer is about SP, and MCP terms are flagged and mapped.
- [ ] Exact labels, API names and step order match the references or live docs.
- [ ] Limits and licensing numbers were re-checked when tools were available.
- [ ] Undocumented behavior is labeled, and a way to confirm it is given.
- [ ] Troubleshooting answers include a concrete check: console, DOM, network or SQL.
- [ ] No customer-specific names or identifiers are carried from one conversation into general guidance.

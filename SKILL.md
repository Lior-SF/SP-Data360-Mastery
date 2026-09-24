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
  Mobile SDK, batch decisions, Data 360 SQL reporting, and a playbook for
  new implementations on any site type or channel. Use when a prompt
  involves Salesforce Personalization, Data 360 or Data Cloud personalization,
  personalization points or decisions, WPM, sitemaps, engagement signals or
  attribution, and whenever an answer must be kept separate from Marketing Cloud
  Personalization (MCP, Interaction Studio, Evergage).
license: MIT
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
- MCP-only features don't exist in SP: native frequency capping, Einstein Recipes, Gears and campaign template code. Don't claim SP has them. To cap frequency in SP, count the experience's own view events in a time-windowed real-time insight and gate the decision on it, with no catch-all decision on that point. This is a pattern built from documented parts, not a feature; the steps and limits are in [decisioning.md](references/decisioning.md) §8.1.

## Answer workflow

1. **Scope.** Classify the prompt: SP, MCP, Data 360 platform, or another cloud. For MCP, say so and don't answer from this skill.
2. **Establish context.**
   - The answer may depend on channel and site type: multi-page/server-rendered web, single-page app, framework-rendered components, Experience Cloud (Aura or enhanced LWR), headless, native mobile, server-side or outbound. If the prompt doesn't state it and it matters, ask, or answer for each relevant context.
   - Never assume a single-page app, a specific framework, a banner use case, or any previous customer's setup.
   - For a new customer or new use case, start from [references/implementation-playbook.md](references/implementation-playbook.md).
3. **Route.** Read only the reference file(s) the question needs (table below). For troubleshooting, always add [references/troubleshooting.md](references/troubleshooting.md).
4. **Verify volatile facts.** If Salesforce documentation tools are available (for example a Salesforce Docs MCP server), re-check limits, UI labels, licensing numbers and anything release-dependent against live docs. Follow the source rules below.
5. **Answer precisely.**
   - Use exact UI labels and API names, and give step sequences in order.
   - Cite the official page when you state a non-obvious fact.
   - Keep labels such as `(UNVERIFIED)` and `(Field-observed, undocumented)` when you repeat those statements.
6. **Don't invent.** If neither the references nor live docs cover something, say it's undocumented and give a concrete way to confirm it: a console check, a SQL query, a UI path, or a Support case.

## Routing

| Question is about… | Read |
|---|---|
| Starting a new customer or use case: discovery questions, architecture choices by channel and site type (including Experience Cloud), setup order, use-case patterns, measurement plan, go-live checklist | [references/implementation-playbook.md](references/implementation-playbook.md) |
| Licensing, credits, editions, permission sets, Personalization Setup, foundational data, Personalization DMOs, limits, feature timeline | [references/platform-and-setup.md](references/platform-and-setup.md) |
| Identity resolution and unification best practice: rulesets, match rules, party identification design, "Match to", case sensitivity, real-time vs scheduled unification, billable full reruns, reconciliation, anonymous vs known, shared devices | [references/field-guide-data.md](references/field-guide-data.md) §1 first, then [references/data-360-foundations.md](references/data-360-foundations.md) (documented ruleset, match and reconciliation mechanics, outputs), [references/web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md) (identity events) and [references/sql-cookbook.md](references/sql-cookbook.md) (identity checks) |
| Data 360 foundations: data stream → DSO → DLO → DMO, mapping, identity DMOs, match and reconciliation rules, resolution outputs, data graphs, data-layer QA queries | [references/data-360-foundations.md](references/data-360-foundations.md) |
| Web SDK deployment, script placement, `init` options, consent (any CMP), identity events, sitemap API, SPA handling, flicker defense, Personalization module, auto view/click tracking, Decisioning API | [references/web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md) |
| Copy-ready sitemap: multi-page / server-rendered starter, CMP adapter, optional SPA add-on; catalog/cart/order/identity event formats and landing DMOs | [references/sitemap-templates.md](references/sitemap-templates.md) |
| Profile/item data graphs, personalization points, content schemas, decisions, targeting rules, merge fields, recommenders, real-time layer | [references/decisioning.md](references/decisioning.md) |
| WPM, display methods, experience templates, preview/publish, personalization campaigns, experiments and experimentation APIs | [references/wpm-experiences-campaigns.md](references/wpm-experiences-campaigns.md) |
| Engagement signals and metrics, attribution models, Attribution/Pipeline Intelligence, Tableau, Data 360 reports, calculated insights | [references/measurement-and-attribution.md](references/measurement-and-attribution.md) |
| Engagement Mobile SDK, server-side decisioning, batch decisions for segments, Agentforce, Einstein Studio | [references/mobile-and-channels.md](references/mobile-and-channels.md) |
| "Is this SP or MCP?", migration, terminology mapping | [references/sp-vs-mcp.md](references/sp-vs-mcp.md) |
| Anything broken: not rendering, duplicated, zero rows, save errors | [references/troubleshooting.md](references/troubleshooting.md) |
| SQL for views, clicks, CTR, unique or unified individuals, point/decision breakdowns | [references/sql-cookbook.md](references/sql-cookbook.md) |
| Field-verified gotchas, tricks and patterns not in the official docs: consent wiring, browser identity capture, sitemap engineering, SPA hardening, WPM anchors, offline sitemap tests (web); identity resolution design, connector mapping traps, child-record targeting, SQL diagnosis, credits, rollout, privacy sign-offs (data) | [references/field-guide-web.md](references/field-guide-web.md), [references/field-guide-data.md](references/field-guide-data.md) |

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
  views / clicks / outcomes carrying personalizationContentId -> an engagement DMO with an FK to Personalization Log
    (web: Website Engagement or Product Browse Engagement; app/other: the Event Type chosen in connector tracking,
     or Media / Lead / Social Message / Sales Order Product Engagement)
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
  - `Use Case Setup`: `Maximize Product Revenue` (commerce) or `Maximize Article Clicks` (content). It can't deploy into a data space that already has a profile data graph, or twice to the same data space.
  - `Advanced Setup`
- Permissions:
  - `Personalization Admin` and `Personalization User` are the two standard permission sets. `Personalization User` can't create engagement signals, attribution models or batch decisions.
  - Setup also requires adding `Access Personalization Platform` to the `Data Cloud Salesforce Connector` permission set.
  - Dashboards need `Personalization Intelligence User`.
- The billable unit is the personalization decision. License credit allowances and attribution-model quotas are in the reference. The Personalization Card covers SP inside Salesforce apps; web, mobile apps and other channels outside Salesforce clouds need the full Personalization License.
- Renames:
  - content schema (formerly response template)
  - Dynamic Content (formerly Manual Content)
  - Data 360 (formerly Data Cloud)
  - Some API names still use the old terms.
- **MCP migration:** the MCP catalog CSV export is for sandbox data spaces only, and MCP must never be an ongoing catalog source. The Data 360 MCP connector syncs only users who engage after it's deployed. See [sp-vs-mcp.md](references/sp-vs-mcp.md) §5.

### Web SDK and consent — [web-sdk-and-sitemap.md](references/web-sdk-and-sitemap.md)

- **Consent:** the Web SDK stores and sends nothing until it receives an explicit `Opt In`. `consents` is required in `init`, and `consents: []` means no tracking. MCP instead tracks by default.
  - The only documented purpose is `Tracking`; MCP's `Personalization` purpose doesn't apply.
- **Initialization order:** `SalesforceInteractions.Personalization.Config.initialize(...)` must run **before** `SalesforceInteractions.init(...)`.
- **`reinit()` is for virtual navigation.** Multi-page sites re-run the sitemap on every page load and need no navigation `reinit()`. The SP example sitemap's polling block is labelled "SPA Websites" and must not be copied into them.
  - Two narrow, one-time uses apply on any site: applying `setCookieDomain()` after `init`, and an optional replay of the first page view after a late consent opt-in ([troubleshooting.md](references/troubleshooting.md)).
- **Commerce events are documented:** `CartInteractionName.AddToCart` / `RemoveFromCart` (`lineItem`), `ReplaceCart` (`lineItems`), `OrderInteractionName.Purchase` (`order.id`, `order.totalValue`, `lineItems`). Catalog interactions cover products, categories, articles or any item (`catalogObject.type` is free text). Formats: [sitemap-templates.md](references/sitemap-templates.md).
- **Identity on the first event:** profile data on the first action event of a new device suppresses the automatic anonymous identity event; send `partyIdentification` in a separate `sendEvent`.
- **Flicker defense defaults:** `redisplayTimeoutMilliseconds: 2000` and `renderPersonalizationAfterTimeoutElapsed: false`. A response that arrives after the timeout is not rendered.
- **`init` options:** documented options are `consents`, `cookieDomain`, `personalization.dataspace`, and `dataCloud.timeTracking` (Summer '26). Treat any other option as undocumented.
- **Where event data goes:**
  - Profile data belongs in `user.attributes`, with an `eventType` such as `identity`, `partyIdentification` or `contactPointEmail`.
  - Fields placed under `interaction.attributes` become engagement fields, so no contact point is created.
  - `user.identities` is MCP's identity model.
- **`isMatch`:** must return a boolean. MCP allows a Promise; in SP a returned Promise is truthy and matches every page.
- **Page type names:** a sitemap page type `name` is both the WPM `Current Page Type` binding and the `sourcePageType` on events. Renaming it silently breaks experiences and reports.
- **Fetching on the web:** call `SalesforceInteractions.Personalization.fetch([...])`; `fetchDecisions` is the mobile SDK method. Dynamic Content values arrive in each personalization's `attributes`, not in `data`.
- **Personalization events:** web renders emit `personalization-view` and `personalization-click` (`userEngagement`) into the Website Engagement DMO.
- **Connector-level engagement tracking (web and mobile):** `Personalization Engagement Tracking` → `Add Tracking Event` → `Content Schema` → `Event Type` → per-field `Mapping Type` → View/Click/Dismiss action names; configured once per content schema. The chosen `Event Type` decides the landing engagement DMO.
- **Decisioning API:** `POST https://{tenantSpecificEndpoint}/personalization/decisions`, with an authenticated variant. All points in one request must share a profile data graph, and overload returns HTTP 429.

### Decisioning — [decisioning.md](references/decisioning.md)

- **Standard vs real-time data graphs:** a point on a **standard** profile data graph skips the profile lookup and is evaluated against a blank anonymous profile unless the caller supplies profile data, so profile-based targeting rules evaluate false. Use a **real-time** profile data graph for live web targeting; WPM lists only points built on one.
- **Personalization type:** choosing a type fixes the point's shape: Recommendations (recommender output) or Dynamic Content (attributes stored on the decision; still `ManualContent` in the API).
- **Real-time graph joins:** real-time profile data graphs join child objects only through the parent object's primary key. Relate profile-extension data (for example tiers, preferences, account or subscription attributes) to Individual or Unified Individual, not through Party Identification values.
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
  - If the string does nothing or WPM errors, often because a redirect or router dropped it, launch WPM from the loaded page with the documented bookmarklet `javascript:SalesforceInteractions.Personalization.launchWpm()`.
  - Chrome steps are in the WPM reference, and diagnosis is in [troubleshooting.md](references/troubleshooting.md).
- **Display methods:** `Replace a Content Zone`, `Use Content Zone Handler`, `Replace an Element`, `Add Before an Element`, `Add After an Element` and `Add an Overlay`.
- **Selectors:** element targets are CSS selectors. An element that has only an `id` must be targeted as `#id`.
- **Publishing:** nothing goes live until `State` is `Enabled` and you `Save`. Previewing a specific decision ignores its targeting rules.
- **Test-experience hygiene:** an `Enabled` POC or test experience keeps serving real visitors.
  - Prefix test assets (`TEST_`, `POC_`).
  - Before go-live, sweep every page type with `Show All Personalization Experiences`, disable leftovers, and return test decisions to `Draft`.
  - Details are in the WPM reference and [troubleshooting.md](references/troubleshooting.md).
- **Experience templates:** since release 262 they are built in the app, not in the sitemap.
- **Campaigns:** personalization campaigns support Dynamic Content schemas on the web channel only.
- **Experiments:** Bayesian, with at least 1,000 participants per cohort (check the Experiment Summary participant totals). The first cohort is the control, and settings are locked after `Start`. `Winner Found` (95% range entirely above control) is a recommendation; roll out manually, or automate through the Experiment Connect API.

### Measurement — [measurement-and-attribution.md](references/measurement-and-attribution.md)

- **Signals and the Personalization Log:** a signal can be an attribution funnel stage only if it has an active relationship to the Personalization Log DMO. Website Engagement has no personalization point field, so filter by point through the Personalization Log relationship.
- **Engagement ↔ log join:** attribution needs an engagement DMO whose `PersonalizationContentId` joins the Personalization Log `Id`. This foreign key is documented on Website, Website Item, Product Browse, Shopping Wishlist (and Item), Shopping Cart Product, Sales Order Product, Media, Lead, Social Message and Promotion Engagement. If the event schema or stream mapping lacks `personalizationContentId`, views and clicks can't be attributed on any channel.
- **Funnels vs CTR:** attribution funnels are individual-based. The entrance stage counts individuals, and later stages count conversions within the attribution window. Funnel conversion differs from raw event click-through rate (CTR).
- **Custom attribution:** 2–4 stages, `First Touch` or `Last Touch`, per-org and per-data-space model limits. Predefined attribution needs the Product Browse, Shopping Cart and Product Order engagement objects.
- **CRM Analytics:** Pipeline Intelligence explicitly requires CRM Analytics. For the Attribution Intelligence `Analytics` tab, the dependency is neither documented nor excluded; its only listed permission is `Personalization Intelligence User`. Confirm in the target org.
- **Compound metrics:** only one COUNT metric divided by another (`Divide By`). Experiment summaries store `RATE` metrics, so a CTR-style primary metric is viable (strongly implied, not stated).
- **Reporting CTR:** Data 360 reports on calculated insights can't use formulas. Compute CTR in calculated insight SQL, Query Editor or Tableau.

## Implementation guidance by context

Apply the guidance that matches the customer's channels and site type, and explain the trade-off when you deviate. For a new customer, work through [references/implementation-playbook.md](references/implementation-playbook.md) first.

### All implementations

- **Consent:** feed `consents` from the consent manager as a promise that always settles. Events before opt-in are dropped, so replay the first page view once after opt-in, and only if it was suppressed.
  - The SDK trusts whatever consent status the sitemap passes, and compliance stays with the site owner. Mapping `Opt In` to an always-active "strictly necessary" category opts every visitor in, including those who declined everything. Get privacy sign-off on the category mapping.
- **Identity:** `partyIdentification` `IDName`/`IDType` must match the identity resolution match rule exactly.
  - Never send placeholder values ("NA", "null") as identifiers.
  - Call `resetAnonymousId()` before binding a different signed-in user on the same device.
  - In real-time matching, every criterion runs as `Exact` except phone and email, which run as `Exact Normalized`, whatever the scheduled match method. Fuzzy matching applies only in scheduled runs. Case-sensitive matching is an opt-in advanced criteria setting; without it, `AbC1` and `abc1` match.
  - **Shared devices:** if a browser stays bound to a known customer after sign-out, real-time decisions keep resolving to that customer's unified profile. The next person on the device then sees that customer's personal content. Either rotate the anonymous ID on logout or suppress personal content for signed-out sessions.
- **Measurement:** design it per use case before building.
  - One placement's performance: a two-stage view → click attribution funnel, with signals filtered through the Personalization Log by point. Use the engagement DMO and action values of the placement's channel, for example `personalization-view` / `personalization-click` on Website Engagement, or `catalog-object-view-start` / `catalog-object-click` on Product Browse Engagement.
  - Raw event counts and CTR across points or decisions: Query Editor or a calculated insight.
  - Causal lift: an experiment.
  - Commerce outcomes: predefined attribution with the commerce engagement objects.

### Web: placement and templates

- **Hooks:** target stable, site-owned hooks: a sitemap content zone with a `selector`, or an `id` or `data-*` attribute targeted in WPM (an element with only an `id` is `#id`). Avoid generated class names, selector chains through parent component names, and anchors that exist only in some user states (that segment silently loses renders and views).
- **One path per slot:** either a content zone with `Replace a Content Zone`, or WPM element targeting with no zone declared for that element. Never both.
- **Flicker defense:** SP flicker defense hides the elements that enabled experiences target. MCP's hiding of content-zone selectors doesn't apply.
- **Templates:**
  - Scope CSS class names to the template.
  - Size from the container: `width: 100%` and `align-self: stretch` when the parent is a flex column, plus container queries rather than viewport breakpoints.
  - Hide empty variables.
  - Keep creative images consistent with the layout the template already draws.

### Web: by site type

| Site type | What changes |
|---|---|
| Multi-page or server-rendered | Every navigation is a full page load, so the SDK evaluates the sitemap again on its own: no polling, no `reinit()`. Match page types on URL path or stable DOM markers, and target stable `#id` placeholders with WPM element methods. Start from the multi-page starter in [sitemap-templates.md](references/sitemap-templates.md). |
| Client-side routing (SPA, or SSR framework with client navigation) | Add the optional SPA add-on: `reinit()` on virtual navigation; the documented pattern polls `window.location.href`. Hardening (field-observed): wait for the new route's DOM, cap the wait, block concurrent calls, and make one-time patches idempotent. |
| Framework-rendered components (React, Angular, Vue, including hydrated SSR) | Register a Content Zone Handler so the framework renders the content; WPM then offers `Use Content Zone Handler`. |
| Experience Cloud (Aura / enhanced LWR) | Aura: Web SDK pasted in **Edit Header Markup**, with Relaxed CSP and the SDK URL in Trusted URLs. Enhanced LWR: the native Data Cloud integration, with consent sent through `set-consent` on every page load. SP points reach authenticated users through Agentforce Orchestrator. WPM on Experience Cloud is undocumented. See **Experience Cloud sites** in [implementation-playbook.md](references/implementation-playbook.md). |
| Headless site or no website | No sitemap or WPM. Use the Decisioning API server-side or the Engagement Mobile SDK in apps. With no profile (anonymous, no JavaScript), send `executionFlags: ["ContextOnly"]` and decide on URL/UTM, anchor and custom context. Send views and clicks back through the Data 360 Ingestion API. |
| Outbound (email, files, other systems) | Batch personalization decisions for segments, activated from the output DMO. |

## Field-verified lessons

Seen in real implementations and absent from the docs, so re-test after SDK upgrades and releases. Full lists: [field-guide-web.md](references/field-guide-web.md) and [field-guide-data.md](references/field-guide-data.md).

- **Consent adapter:** read the CMP's live state with its persisted cookie as fallback, and match categories as exact tokens. Treat an empty or unparseable answer as "not decided yet", and size the consent ceiling from measured cold loads (web §1.1).
- **Consent handler:** call `updateConsents()` synchronously first, every time. Decide the first-view replay only from `getConsents()`, and write "sent" memos only after `Opt In` (web §1.2).
- **Append-only data layers:** read the newest entry, and suppress re-binding positionally after logout, never with a timer. Persist the bound user in `localStorage` to detect user switches (web §2.2–§2.3).
- **After `resetAnonymousId()`:** the new device is a new Individual, so re-send the profile attributes decisions depend on, and key memos to `getAnonymousId()` (web §2.4).
- **Page types classify pages; decisions target people:** never split page types by consent or audience, and match paths on segment boundaries (web §3.1).
- **Sitemap robustness:** use top-level `var` or an IIFE (re-injection), swap listeners on re-injection, guard `Personalization.Config.initialize`, and end the `init()` chain with `.catch` (web §3.3–§3.4).
- **Identity resolution:** keep "Match to" empty on party-identifier criteria, send `isAnonymous` on every `identity` event, and batch changes that trigger billable full reruns (data §1).
- **Connector mapping:** after **Update Schema**, run **Sync Schema** per stream. Under Partial refresh, omit unknown values instead of sending `""` (data §2).
- **Child-record targeting:** "has at least one matching row" is `Related Attributes` `Count` `Is Greater Than` `0`, with every row condition in its WHERE (data §3).

## Live verification and source rules (SP vs MCP)

When documentation tools are available, verify against sources in this order:

1. Salesforce Help articles under **Salesforce Personalization**: IDs `mktg.persnl_…` and `mktg.mc_persnl_…`.
2. The Salesforce Personalization developer guide: `developer.salesforce.com/docs/marketing/einstein-personalization/…`.
3. The Salesforce Interactions SDK guide (Data 360 module): `developer.salesforce.com/docs/data/salesforce-interactions-sdk/…`.
4. Data 360 help (data graphs, calculated insights, identity resolution, reports) and release notes (`rn_persnl_…`).

Pages under `developer.salesforce.com/docs/marketing/personalization/…` and help IDs `mktg.mc_pers_…` are **MCP**. Use them only to explain differences. The prefixes are one letter group apart: `mc_persnl_` is SP, `mc_pers_` is MCP. The baseline for this skill is release 264 (Winter '27); if live docs differ, trust live docs and say what changed.

## Answer quality checklist

- [ ] The answer is about SP, and MCP terms are flagged and mapped.
- [ ] The answer states the channel and site architecture it assumes (multi-page, SSR with hydration, SPA, headless, app), or covers each relevant one, plus the industry and item type (product, article, offer, service) when they matter; no SPA, retail, banner or loyalty default was assumed.
- [ ] Exact labels, API names and step order match the references or live docs.
- [ ] Limits and licensing numbers were re-checked when tools were available.
- [ ] Undocumented behavior is labeled, and a way to confirm it is given.
- [ ] Troubleshooting answers include a concrete check: console, DOM, network or SQL.
- [ ] No customer-specific names or identifiers are carried from one conversation into general guidance.

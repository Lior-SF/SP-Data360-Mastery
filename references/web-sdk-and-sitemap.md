# Web SDK, Sitemap, Consent, Identity and the Personalization Module

## Scope

- Copy-ready templates (multi-page starter, CMP adapter, optional SPA add-on) and the commerce event table: [sitemap-templates.md](sitemap-templates.md).
- Browser side of Salesforce Personalization (SP): Data 360 website connector, Salesforce Interactions SDK (Web SDK) with its Data 360 module and the SP Personalization module, sitemap API, consent, identity, flicker defense, Web Personalization Manager (WPM) rendering, engagement tracking, content zone handlers, Decisioning API, debugging.
- Authoritative: SP developer guide (`developer/einstein-personalization`), Interactions SDK Data 360 docs (`developer/data-cloud`), SP Help (`persnl_*`, `mc_persnl_*`), Data 360 Help, release notes. Release 264.0.0 unless stated.
- Marketing Cloud Personalization (MCP, ex-Interaction Studio/Evergage) sources — `developer/personalization` and Help pages with the "Marketing Cloud Personalization" breadcrumb, including the "Marketing Cloud Next for Personalization" migration guide (`mc_pers_mcn_for_pers_*`) — are cited only in explicit MCP ≠ SP statements or flagged contradictions.
- Tags: (UNVERIFIED) = not confirmed in docs; (Field-observed, undocumented) = seen in real SDK behavior or console logs, absent from docs.

## 1. Deployment: website connector, beacon, schema, sitemap, data streams

- SP Help "Add the Web SDK with the Personalization Module to Your Site" has no steps; it links to the dev guide [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_websdk_ep_module.htm&release=264.0.0&type=5).
- SP extends `SalesforceInteractions` with a `Personalization` object; web requests reach SP "through the Decisioning API" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-web-experiences.html).

### Setup sequence (SP dev guide) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html)

1. **Data space**: Data Cloud Setup → Data Management → **Data Spaces** → **New**. Prefix starts with a letter, ≤3 alphanumerics, immutable after save; extra data spaces need the Data Spaces add-on license.
2. **Website connector**: Data Cloud Setup → **Websites & Mobile Apps** → **New** → **Connector Name**, Connector Type **Website** → **Save**.
3. **Event schema (JSON)**: **Upload Schema** with `https://cdn.c360a.salesforce.com/cdp/schemas/250/web-connector-schema.json` or a custom file. **Update Schema** only adds; it "must retain all previous events and fields". New fields must be optional (`isDataRequired: false`) and existing fields can't be updated or renamed [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html); each existing stream then needs **Sync Schema** (new fields) or **Add Events** (new events) and new mappings [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-update-mobile-web-datastream.html) ([field-guide-data.md](field-guide-data.md) §2).
4. **Install SDK**: connector **Integration Guide** section → copy the CDN URL → `<script>` in `<head>` → call `SalesforceInteractions.init`.
5. **Sitemap**: build `sitemap.js` (Sitemap Editor in the Salesforce Interactions SDK Launcher Chrome extension, or the Sitemap Builder below) → connector **Sitemap** section → **Upload** → review → **Save**.
6. **Data stream**: Data Streams → **New** → **Website** → connector → events. One `Engagement` stream consolidates all engagement events; each profile event gets its own `Profile` stream. Set data space and **Refresh Mode** (`Incremental`/`Partial`) per profile event → **Deploy**. Incremental blanks the fields an update omits; Partial keeps them, per device ID [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html). Under Partial, omit unknown values instead of sending `""` (inference: an empty string overwrites).
7. **Map DLOs → DMOs** via **Start Data Mapping**:

| Web connector DLO | Key mappings (SP guide) |
| --- | --- |
| `identity` → Individual | `deviceId`→Individual ID (PK); `dateTime`→Created Date; `firstName`; `lastName`; `isAnonymous`→Is Anonymous; `userName`→External Record ID |
| `partyIdentification` → Party Identification | `deviceId`→Party + Party Identification ID (PK); `IDName`→Identification Name; `IDType`→Party Identification Type; `userId`→Identification Number |
| `contactPointEmail` / `contactPointPhone` | `deviceId`→PK + Party; `email`→Email Address; `phoneNumber`→Telephone Number |
| Catalog → Product Browse Engagement | `id`→Product; `interactionName`→Engagement Channel Action; `personalizationId`→Personalization; `personalizationContentId`→Personalization Content |
| Cart / Cart Item / Order | Shopping Cart Engagement / Shopping Cart Product Engagement / Product Order Engagement; `deviceId`→Individual |
| Consent Log | "Not mapped" (SP guide) |
| Order Item | "Not mapped" in the SP guide; the starter mapping sends it to Sales Order Product Engagement, which Maximize Revenue and order-line insights need [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_profile_dg_for_max_rev.htm&release=264.0.0&type=5) |
| `contactPointAddress` | "Don't map" |

- Mapping canvas traps (Field-observed): automapping pre-fills by name and synonyms, so review every row; map `interactionName` → Engagement Channel Action (never Engagement Channel Type) for custom `userEngagement` events too, and `deviceId` → both Party and Party Identification ID. Details: [field-guide-data.md](field-guide-data.md) §2.

- Replace a sitemap later with **Upload | Replace Sitemap** on the website record page [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_configure_website_connector.htm&release=264.0.0&type=5).
- Data 360 Help calls the tag "a JavaScript beacon script (or CDN script)"; connecting needs the System Administrator profile or Data Cloud Architect; creating the stream needs the Data Cloud Architect permission set [src](https://help.salesforce.com/s/articleView?id=data.c360_a_web_mobile_app_connector.htm&release=264.0.0&type=5).
- The SDK and uploaded sitemap are hosted together on the CDN [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-salesforce-web-sdk.html); website connectors use streaming ingestion [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_schedule.htm&release=264.0.0&type=5).
- Schema version conflict: SP guide links `/250/`; the Data 360 module page links `/260/web-connector-schema.json` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-salesforce-cdp-module-of-the-salesforce-web-sdk.html).
- **Salesforce Data 360 Sitemap Builder** (Chrome extension, low/no-code; release 260) generates sitemap and schema [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_building.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_data_360_sitemap_builder.htm&release=260&type=5).
  - Tabs: `Settings` (data space, logging level, how the sitemap reacts to URL changes), `Consent Management`, `Page Types`, `Resolvers` (Element Selection or Custom JavaScript), `Profile Attributes` (SDK sends `deviceId` by default), `Events`, `Schema` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_tabs.htm&release=264.0.0&type=5).
  - Modes: `Configure`, `Inject` (local test before deploy), `Debug` (Data 360 event structure and decisioning payloads), `Review & Download` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_modes.htm&release=264.0.0&type=5).
- WPM access: append `?sf_personalization_wpm` (or `&sf_personalization_wpm`); sandboxes use `sf_personalization_wpm&sf_personalization_wpm_env=prod_sandbox`; disable popup blockers if the login window doesn't open [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_access_web_personalization_manager.htm&release=264.0.0&type=5). Needs third-party cookies and "a Personalization Admin or Personalization User permission set" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_prerequisites.htm&release=264.0.0&type=5); the access page's permission table instead names a "Web Personalization Manager user permission set" (doc conflict; see [platform-and-setup.md](platform-and-setup.md) §3).
- WPM lists only personalization points in the data space configured in the site's sitemap [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5), and only points built on a **real-time** profile data graph [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5).

### Tag placement and cookie domain

- Documented: copy the CDN script from the connector's **Integration Guide**, add it with a `<script>` tag in `<head>`, then call `init` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html). The SDK and sitemap ship together from the CDN [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-salesforce-web-sdk.html).
- Undocumented for SP: `async`/`defer`, tag-manager deployment, CSP host lists. Guidance (inference): load early in `<head>` on every template, including checkout and confirmation pages; late loading (async, or a tag manager firing on DOM-ready) risks flicker and a missed first page event. If a tag manager is mandated, fire on its earliest trigger on every page and test flicker and first-page events.
- `cookieDomain` sets the domain of the first-party identity cookies and defaults to the current site's domain [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html). Set it to the registrable domain (e.g. `example.com`) to share one anonymous ID across subdomains; separate registrable domains can't share cookies and stitch only through known-user identity resolution (inference from cookie rules). Set it in `init`: `setCookieDomain()` later needs `reinit()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html).

## 2. `SalesforceInteractions.init`

```ts
init(sdkConfig: SdkConfig): Promise<void>   // resolves "when the SDK is successfully initialized and ready"
```

| Option | Type / default | Status |
| --- | --- | --- |
| `consents` | `Consent[]` or `Promise<Consent[]>`; **Required**; SDK waits for the Promise before tracking | Documented [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html) |
| `cookieDomain` | string; defaults to the current site's domain | Documented [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html) |
| `personalization.dataspace` | string; required in practice with >1 data space; if omitted, `fetch` uses `default` | SP docs only; absent from the Data 360 `init` table [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html) |
| `dataCloud.timeTracking` | `enabled` `false`; `thresholds` (30 s `LOW_INTEREST`, 60 s `HIGH_INTEREST`); `eventTypes` `['catalog']`; `activityTimeoutMillis` `5000` (min 1000); `minimumActivityTimeToRegister` `300`; `maxSessionDurationMillis` `3600000`; `sendPageExitWithoutThreshold` `false`; `maxEventsPerSession` `20` | Documented (Summer '26) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-time-tracking.html) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_cdp_2026_summer_web_sdk_time_tracking.htm&release=262.0.0&type=5) |
| `bfcacheAutoReinit` | boolean | In no doc collection; `false` accepted (Field-observed, undocumented) |

- Flow: `init()` completes, then `initSitemap()` in `.then()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
- `SalesforceInteractions.Personalization.Config.initialize(...)` must be called **before** `SalesforceInteractions.init` because "module initialization must occur before the sitemap is initialized" (§7) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html).
- Outside the sitemap use `window.getSalesforceInteractions()`; it resolves the right instance when an advanced feature customizes the global namespace [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
- `setCookieDomain()` after init has no effect until `reinit()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html).
- Time tracking counts only active time (mouse, click, scroll, keyboard), attaches to the first matching `eventTypes` event, emits `eventType` `{contextType}Time` (e.g. `catalogTime`) with `interactionName` `timeOnPage` or `pageExit`, category `Engagement`, and respects consent. `SalesforceInteractions.DataCloud.stopTimeTracking()` stops it; restarting requires re-init [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-time-tracking.html).

## 3. Consent API

| Constant | Value |
| --- | --- |
| `SalesforceInteractions.ConsentPurpose.Tracking` | `Tracking` |
| `SalesforceInteractions.ConsentStatus.OptIn` | `Opt In` |
| `SalesforceInteractions.ConsentStatus.OptOut` | `Opt Out` |

- Only documented Web constants; no `Pending` status. Consent object: `provider` (Required, CMP name), `purpose` (Required), `status` (Required: `Opt In` | `Opt Out`) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html).

```ts
updateConsents(consents: Consent | Consent[]): void
getConsents(): ConsentWithMetadata[]   // [{ consent: {...}, lastUpdatedTime: Date, lastSentTime: Date }]
```

- Read `consent.purpose` and `consent.status` on each `getConsents()` entry, not top-level fields [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html).

- **Default with no consent = no tracking.** The SDK "doesn't store or transmit any collected data until it has been granted explicit consent" and "waits for a valid `Opt In` signal before beginning data collection"; a `Promise` for `consents` is the recommended pattern [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html). `consents` is **Required**; `consents: []` = no tracking until `updateConsents()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html). The SDK sends events "only if a customer has consented"; on revocation it "immediately stops emitting events" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-salesforce-interactions-web-sdk.html). The MCP-breadcrumb migration guide states the same as "defaults to opt-out … all users are treated as opted-out" (see traps).
- The SP example sitemap hard-codes `ConsentStatus.OptIn` in `init` — reference only, never ship it [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html).
- `OnConsentRevoke` (`interactions:onConsentRevoke`, detail `{consent, lastUpdateTime, lastSentTime?}`) fires on `Opt In` → `Opt Out`; `OnShutDown` fires when the SDK shuts down, e.g. on an `Opt Out` update [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).
- `consents` is attached "to the first event captured after a customer consents to tracking or when a customer revokes consent" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html); Consent Data adds it is "typically included in subsequent events" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html).
- Each entry translates to `eventType = "consentLog"` (category `Engagement`) with `provider`, `purpose`, `status` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). The SP mapping guide leaves Consent Log unmapped [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html).
- Web ≠ Mobile: the Engagement Mobile SDK defaults to `Consent.pending` (2.x: events collected locally until opt-in/out; 3.x: SDK-managed, can't be set manually) [src](https://developer.salesforce.com/docs/data/data-cloud-engagement-mobile-sdk/guide/c360a-api-engagement-mobile-sdk-consent-management-v2.html) [src](https://developer.salesforce.com/docs/data/data-cloud-engagement-mobile-sdk/guide/c360a-api-engagement-mobile-sdk-consent-management-v3.html). Don't assume a Web pending queue.
- (Field-observed, undocumented): `init()` resolves before a pending `consents` Promise settles; events are dropped, not queued, while not opted in; `getConsents()` returns `Opt In` while the Consent Log DLO row holds `opt-in`.

### Connecting any consent manager (CMP-agnostic)

- Documented contract: pass `consents` as a Promise resolving to `Consent[]` (the init page recommends it "for a third-party Consent Management Platform (CMP) to load"), or `[]` plus `updateConsents()` later; call `updateConsents()` from the CMP's change handler, "directly from your OneTrust or custom consent management provider's code" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html).
- Third-party (verify in the vendor's docs): CMPs typically expose a read of the stored decision, a callback or DOM event on first decision and change, sometimes a ready signal; some implement the IAB TCF API. Wrap them in a three-member adapter (`provider`, `read()` → `true | false | null`, `subscribe(cb)`); keep all vendor code inside it.
- Map exactly one privacy-approved category/purpose to `Tracking`, never an always-granted one; always let the Promise settle (stored decision, first decision, or `[]` after a ceiling) (inference). `[]` is documented only as a direct `consents` value for an undecided user [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html); the Promise "must resolve with an array of consent data objects" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html), so test a Promise that resolves `[]`, or resolve with an explicit `Opt Out` after privacy sign-off (whether an init-time `Opt Out` with no prior opt-in writes a `consentLog` row is undocumented: rows are documented only for the first event after opt-in and on revocation [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html); confirm in the Consent Log DLO before reporting on it). Adapter code: [sitemap-templates.md](sitemap-templates.md) §2–§3.
- Field lessons (Field-observed, undocumented): CMP adapter hardening, change-handler order, replay guards, no second Consent Log row for an unchanged verdict, and consent categories stored as an `identity` attribute for targeting: [field-guide-web.md](field-guide-web.md) §1.

## 4. Identity

- First-party cookie `__sfid_${domainHash}_` holds a random `anonymousId`, reused across sessions [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html). Other spellings: `_sfid_${domainHash}` in the API index (UNVERIFIED this pass); `_sfid_*` and `_sfic_*` on the MCP-breadcrumb cookie page [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_cookie_id_sdk_diffs.htm&release=264.0.0&type=5). Match cookies with a `_sfid_` prefix test.

| Method / event | Behavior |
| --- | --- |
| `getAnonymousId()` / `setAnonymousId(id)` | Read/overwrite the cookie id (e.g. `"efc9953d6515dc7f"`); a new id fires `OnSetAnonymousId` `{newAnonymousId}` |
| `resetAnonymousId()` | Deletes the cookie and mints a new id ("effectively starts a new session"); fires `OnResetAnonymousId` |
| `getCookieDomain()` / `setCookieDomain(d)` | Share across subdomains (`cookieDomain: "domain.com"`); set before init, or `reinit()` afterwards |
| `clearPersistedIdentities()` | Clears known identities (e.g. `loyaltyId`, `email`) from SDK storage; fires `OnClearPersistedIdentities` |

Sources: [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html)

- The beacon injects `category`, `dateTime`, `deviceId` (PK of profile events), `eventId` (PK of engagement events), `eventType`, `sessionId` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). Doc payloads show identical 16-hex `deviceId`/`sessionId` values [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html); `deviceId` == `anonymousId` is implied by format only (UNVERIFIED).
- **Automatic anonymous identity event**: when the anonymous id changes (first visit, `setAnonymousId` with a new value, `resetAnonymousId`) and the first action event after the change carries no `user.attributes.eventType`, the SDK sends a minimal `identity` event with `isAnonymous: true` on the first `onEventSend` batch; nothing is sent if the visitor leaves first; the record can later be merged or overwritten [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html). Consequence (inference): don't attach `user.attributes` (e.g. `partyIdentification`) to the first page interaction via `onActionEvent` on a new device, since that suppresses the automatic identity event; send known-user attributes in a separate `sendEvent` after `initSitemap`, once per user per session, and only when opted in.
- **Profile events**: `sendEvent({ user: { attributes: { eventType, ... } } })`. `eventType` Required; starts with a letter; alphanumerics/underscores only; no trailing or consecutive `_`; ≤80 chars. Send only when attributes are first discovered or change; `interaction` + `user` can share one call [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html).

| `user.attributes.eventType` | Attributes (translation table) |
| --- | --- |
| `identity` | `firstName`, `lastName`, `isAnonymous` (all Required) |
| `contactPointEmail` | `email` (not marked Required) |
| `contactPointPhone` | `phoneNumber` (Required) |
| `partyIdentification` | `IDNameWeb`, `IDType`, `userId` (all Required) |

Source: [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html)

- Doc contradictions:
  - `isAnonymous`: translation table says `0` = anonymous, `1` = known; the automatic event sends `isAnonymous: true` for anonymous visitors [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html). Ingestion counts `0`, `No`, `N`, `F`, `False` or empty as known, and an unmapped Is Anonymous as known [src](https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5), so `1` = anonymous is the majority convention and the translation table is the outlier. Send it on every `identity` payload (strings if the schema field is Text) and verify against your DLO.
  - Party ID name: translation table `IDNameWeb`; SP mapping guide DLO field `IDName` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html). Use the field name in your uploaded schema.
  - Email: User Data `onActionEvent` example sets `emailAddress`; translation table maps `email` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html).
- **Known-user matching for SP**: real-time identity resolution custom match rule — Object `Party Identification`, Field `Identification Number`, Match Method `Exact`, Match on Blank unchecked, plus chosen Party Identification Type/Name values; DLO→DMO mapping must exist first [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5). Real-time IR supports exact and exact-normalized matching for email and phone; fuzzy is batch only [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_add_recommended_rules_to_ir_ruleset.htm&release=264.0.0&type=5). A party identifier matches only when Identification Number, Identification Name and Party Identification Type are all identical; all five Party Identification fields must be mapped, and Match on Blank isn't allowed [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5). On standard-field criteria, Match on Blank over-merges frequently empty fields [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5).
- Field lessons: identity resolution design, limits, full-rerun triggers and real-time prerequisites (if scheduled runs don't merge web with CRM, real-time won't either): [field-guide-data.md](field-guide-data.md) §1. Browser capture (append-only data layers, logout signals, persisted binding, byte-for-byte identifiers, memo keying): [field-guide-web.md](field-guide-web.md) §2.
- Data 360: real-time runs execute all criteria as exact/exact-normalized regardless of configured method, ignore Match on Blank, and the data is re-unified in the next scheduled run [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_real_time.htm&release=264.0.0&type=5). The real-time data graph refreshes from the Unified Individual DMO every 24 hours ("during the pilot period" wording) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_configure_real_time_matching.htm&release=264.0.0&type=5).
- **Which individual decisions evaluate**:
  - For web personalization through WPM, the profile data graph must be real-time with the Unified Individual as primary DMO [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5). Point pages also allow standard graphs for callers that supply the profile, and the docs disagree on this; see [decisioning.md](decisioning.md) §1.2.
  - Real-time pipeline: request carries point IDs and an individual ID → SP calls the Data 360 profile API for the real-time profile → targeting → decision → log to Data 360 [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5).
  - Decisioning API: `context.individualId` is the profile key; `unifiedIndividualId` "isn't used for profile lookup", only for experiment partitioning [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html).
  - The Web `fetch` example returns `"individualId": "ba8f56683e2ca01c"` (anonymousId-shaped) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html). Inference: web decisions key on the source Individual (`deviceId`) resolved through real-time IR (UNVERIFIED as an explicit statement).
  - Batch output `ProfileID__c` is "the unified individual ID … (if available) or the individual ID" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/batch-personalization-output-dmo.html).
  - Standard (non-real-time) profile data graph: no profile lookup; unless the profile data graph JSON is passed, SP evaluates a blank anonymous profile and profile-based rules evaluate false [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5).

## 5. Sitemap API and event specifications

```ts
initSitemap(siteMapConfig: SiteMapConfig): boolean
```

| Key | Doc status | Fields |
| --- | --- | --- |
| `global` (GlobalPageConfig) | "Required" in the Data 360 table; omitted in the SP example | `listeners`, `locale`, `onActionEvent`; `contentZones` (SP) |
| `pageTypeDefault` (DefaultPageConfig) | optional; used when no PageConfig matches | `name`, `listeners`, `locale`, `onActionEvent`; `interaction` (SP example) |
| `pageTypes[]` (PageConfig) | "Required" | `name` (Required, unique), `isMatch: () => Boolean` (Required), `interaction`, `listeners`, `locale`, `onActionEvent`; `contentZones` (SP) |

Sources: [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html)

- `global` is merged into the applied PageConfig/DefaultPageConfig and isn't applied when nothing matches [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html).
- **Page-type match order — doc contradiction**: the `initSitemap` table says "Multiple page configurations can match a single page. These configurations are merged together" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html); `OnPageMatchStatusUpdated` says "the very first page type to successfully match … is given the status `selected`" and evaluation of the rest stops [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html). Order `pageTypes` most-specific first and keep `isMatch` mutually exclusive.
- `interaction` is extracted and sent automatically when a config matches; wrap values in functions (resolvers) for lazy evaluation. `onActionEvent(event)` runs for every event and must return it [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html).
- Resolvers (return lazy functions; optional `transform`): `fromCanonical()`, `fromHref()`, `fromItemProp(itemProp)`, `fromJsonLd(path?)` (examples spell `fromJsonLD`), `fromMeta(name)`, `fromSelector(sel)`, `fromSelectorMultiple(sel)`, `fromSelectorAttribute(sel, attr)`, `fromSelectorAttributeMultiple(sel, attr)`, `fromWindow(path)`. Listener: `listener('click', selector, handler)` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html).
- **Content zones** (SP only; absent from the Data 360 sitemap reference): `{ name: String (Required), selector: String (optional CSS) }` in `global.contentZones` (doc examples `global_popup`, `global_infobar` without selector) or `pageTypes[].contentZones`; exposed to WPM [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-content-zones.html). The MCP-breadcrumb migration guide contradicts this (traps).
- `sendEvent({ interaction?, user?, account? })`; `interaction` needs at least a valid `name`. The SDK adds `source {pageType, url, urlReferrer, channel:"Web", locale}`, `pageView` (`1` page load / `0` user action), `time` (epoch ms), `consents`, `user.anonymousId` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html).
- `dateTime` comes from the browser clock (`toISOString()`) and can be skewed; the same page calls `time` a "server timestamp" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html).

| Source in SDK event | Web connector `eventType` | Category |
| --- | --- | --- |
| Catalog interaction (`catalogObject.id`/`type` → `id`/`type`) | `catalog` | Engagement |
| Cart interaction + each line item | `cart` + child `cartItem` (`cartEventId`) | Engagement |
| Order interaction + line items | `order` + child rows (`orderEventId`) | Engagement |
| `consents[]` | `consentLog` | Engagement |
| `user.attributes` | value of `user.attributes.eventType` | Profile |

Source: [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html)

- **Commerce events are documented**: `CartInteractionName.AddToCart` / `RemoveFromCart` (`lineItem: { catalogObjectType, catalogObjectId, quantity }`), `ReplaceCart` (`lineItems`, `[]` = empty cart) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-cart-interaction.html); `OrderInteractionName.Purchase` / `Return` / `Cancel` / `Preorder` / `Exchange` / `Ship` / `Deliver` (`order: { id, totalValue }`, optional `currency`, `lineItems`) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-order-interaction.html). Full format table, landing DMOs and doc quirks: [sitemap-templates.md](sitemap-templates.md) §5.
- Required on every translated event: `category`, `dateTime` (`yyyy-MM-dd'T'HH:mm:ss.SSS'Z'` only; used for partitioning), `deviceId`, `eventId`, `eventType` (schema `developerName`), `sessionId`, `interactionName`. Custom `attributes.*` → `attributeCustomFieldN` and must be added to the schema manually [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html).
- Catalog constants: `SalesforceInteractions.CatalogObjectInteractionName.ViewCatalogObject` = `View Catalog Object`; also `ViewCatalogObjectDetail`, `QuickViewCatalogObject`, `ShareCatalogObject`, `ReviewCatalogObject`, `CommentCatalogObject`, `FavoriteCatalogObject` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-catalog-interaction.html).
- Custom events: define in the schema first (a deployed custom schema can't be edited or have fields deleted); omitted `eventType` defaults to `name`; field names camel-case (`attributes.myNum` → `attributesMyNum`) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-custom-events.html).
- `SalesforceInteractions.CustomEvents`: `OnBeforeEventSend`, `OnClearPersistedIdentities`, `OnConsentRevoke`, `OnEventSend`, `OnException`, `OnInit`, `OnInitSitemap`, `OnPageMatchStatusUpdated`, `OnResetAnonymousId`, `OnSetAnonymousId`, `OnShutDown`. Values use `interactions:`, yet the page's listener example uses `salesforce:onEventSend` — bind via the constants [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).

## 6. Single-page applications (SPA)

- Applies only when routes change without a full page load. Multi-page / server-rendered sites re-run the sitemap on every load and need none of this section; never copy the SP example's `/* === SPA Websites === */` polling block into them [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html). The copy-ready add-on is in [sitemap-templates.md](sitemap-templates.md) §4.
- `reinit(): void` "forces the SDK to reinitialize its state and re-run sitemap evaluation … to match the new virtual page" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
- Documented pattern: inside `init().then()`, poll `window.location.href` and call `reinit()` on change — SP example 500 ms after `initSitemap` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html); Data 360 example 200 ms, set up before `initSitemap` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html). Sitemap Builder `Settings` configures "how the sitemap reacts to URL changes" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_tabs.htm&release=264.0.0&type=5).
- Re-evaluation re-runs `isMatch`; since a matched config's `interaction` is sent automatically, a new page interaction with the new `sourcePageType` follows (inferred).
- `OnInit` is the documented hook for debugging SPAs that "reinitialize without a page load event" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).
- Whether `reinit` re-matches WPM experiences, re-applies flicker defense and re-calls the Decisioning API is undocumented (UNVERIFIED). Console logs show per-page-type experience matching followed by a fetch after navigation (Field-observed, undocumented).
- Virtual-DOM frameworks should render via content zone handlers (§9), not SDK DOM mutation [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html).
- Back/forward cache: no documented handling; `bfcacheAutoReinit` presumably auto-calls `reinit` on bfcache restore (UNVERIFIED; name-based inference).
- Field hardening (DOM-settle ceiling, identity bound before `reinit()`, `locale` as a function for language switchers, re-injection safety): [field-guide-web.md](field-guide-web.md) §3–§4.

## 7. Personalization module

```js
SalesforceInteractions.Personalization.Config.initialize({
  personalizationExperienceConfigs: [/* optional */],
  customFlickerDefenseConfig: { redisplayTimeoutMilliseconds: 2000, renderPersonalizationAfterTimeoutElapsed: false },
  customEngagementConfig: /* optional, see §8 */ undefined,
});
```

- "Initialize it at the beginning of your sitemap"; call it **before** `SalesforceInteractions.init` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html). Guard the call (`if (SalesforceInteractions.Personalization)`) so a build without the module keeps tracking, and end the `init()` chain with `.catch` (Field-observed; [field-guide-web.md](field-guide-web.md) §3.3).
- All three keys optional. The table types all three as `Array`, but examples pass objects for `customFlickerDefenseConfig` and `customEngagementConfig` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html).
- The module publishes WPM-generated experience configurations, flicker defense and extra engagement destinations [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/configure-web-personalization.html).

| `FlickerDefenseConfig` | Type | Default (`DEFAULT_FLICKER_DEFENSE_CONFIG`) | Meaning |
| --- | --- | --- | --- |
| `redisplayTimeoutMilliseconds` | Number | `2000` | Wait before redisplaying hidden elements |
| `renderPersonalizationAfterTimeoutElapsed` | Boolean | `false` | Proceed with (`true`) or block (`false`) rendering after the timeout |

Source: [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/configure-flicker-defense.html)

- The page's "Custom Configuration" snippet (`3000`/`true`, oddly written as an `interface`) is illustrative; defaults "are sufficient for most use cases" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/configure-flicker-defense.html).
- Which elements get hidden isn't documented beyond "hidden elements". Console logs show flicker defense hiding targets of page-type-matched experiences as `{transformerName, tag, path}` (Field-observed, undocumented; mechanism UNVERIFIED).
- `SalesforceInteractions.Personalization.fetch(pointNames: string[])` returns a `Promise` of the Decisioning API response; data space from `init({ personalization: { dataspace } })`; no options argument documented [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html).
- Web response example: `personalizations[]` with `personalizationId`, `requestId`, `individualId`, `dataSpace`, `personalizationPointId` (`9pp…`), `personalizationPointName`, `dmoName` (e.g. `ssot__GoodsProduct__dlm`), `data[]` DMO rows each carrying `personalizationContentId` = `<personalizationId>:<index>` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html). The API reference puts `requestId` at top level (§10).
- WPM experience flow: Personalization Experiences → **New** → **Embedded Content** → personalization point → experience template → **Location** (**Current Page Type** or **Page URL** with wildcards) → **Display Method** → **Content** tab (**Engagement Destination**, template) → **Preview Settings** (Show Overlays, Show All Personalization Experiences) → optional Individual ID → **Save** [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5). Manual mode edits attributes of selected elements [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_manually_personalize_page_elements.htm&release=264.0.0&type=5).

| WPM Display Method | Behavior |
| --- | --- |
| `Replace a Content Zone` | Pick a sitemap content zone; replaced by the template output |
| `Use Content Zone Handler` | Pick a registered handler; offered only if the site uses a frontend framework and a handler is registered |
| `Replace an Element` / `Add Before an Element` / `Add After an Element` | Click the element to target |
| `Add an Overlay` | When to Display: `Immediately`, `Exit Intent` (optional delay), `Element Click`, `Scroll Percentage` |

Source: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5)

- Publish: set the **State** toggle to Enabled, then **Save**; nothing publishes until both happen [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_export_and_publish.htm&release=264.0.0&type=5). (Mobile experiences use State **Active** [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_mobile_publish.htm&release=264.0.0&type=5).)
- Preview: a preconfigured decision (ignores targeting), an experiment cohort, or **Current User Decision** [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_preview_the_experience.htm&release=264.0.0&type=5).
- Building blocks: experience template, content zone, WPM, personalization experience (links a point, a template, a zone) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_web.htm&release=264.0.0&type=5). Since Summer '26 templates are built in the Personalization app; sitemap-held templates migrate automatically [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_build_customize_experience_templates.htm&release=262.0.0&type=5).
- How the SDK loads published experience configs at runtime is undocumented (Gaps).

## 8. Engagement tracking

| Engagement Destination (WPM) | `eventType` | Interaction names | Payload specifics | Recommended DMO |
| --- | --- | --- | --- | --- |
| Product Engagement (recommendation experiences only) | `catalog` | `catalog-object-view-start`, `catalog-object-click` | `id` (item), `type: "Product"`, `personalizationId`, `personalizationContentId` | Product Browse Engagement |
| Website Engagement (manual content) | `userEngagement` | `personalization-view`, `personalization-click` (defaults) | no `id`/`type` | Website Engagement |

Source: [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html)

- You must update the Data Cloud Web Schema so these event types exist. The page's Website Engagement sample payload shows `interactionName: "Button Clicked"`, not the default names [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html).
- Custom destination: `const c = SalesforceInteractions.Personalization.Config.Engagement.get()`; `c.destinations['key'] = { label, description, disableSendingNonItemEngagementEvents, eventModifiers: { type, 'event-type', 'interaction-name' } }` (`'interaction-name'` = string or `(context) => …`, `context.name` ∈ `view`|`click`); pass `customEngagementConfig: c` to `Config.initialize` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html).
- Connector-level tracking: Data Cloud Setup → **Websites and Mobile Apps** → connector → **Personalization** tab → **Personalization Engagement Tracking** → **Add Tracking Event** → **Content Schema**, **Event Type**; Mapping Types `Content Schema Attribute`, `Action`, `Static Value`; **Advanced Settings**: **API Name**, **View Action** (`personalization-view`), **Click Action** (`personalization-click`), **Dismiss Action** (none). Web and mobile; Data 360 engagement events only (not profile, cart, order); once per content schema, applied to every point using it; mobile components must still call the tracking APIs [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_mobile_engagement_tracking.htm&release=264.0.0&type=5).
- Manual tracking (custom rendering or `fetch`): `sendEvent({ interaction: { name: "personalization-click", eventType: "userEngagement", catalogObjectType, catalogObjectId, personalization: { id, contentId } } })`. "Always set `id` and `contentId`": `contentId` = `personalizationContentId` for a specific product, otherwise `personalizationId` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html).
- (Field-observed, undocumented): translated WPM view events `{"eventType":"userEngagement","interactionName":"personalization-view","category":"Engagement","personalizationId":X,"personalizationContentId":X}` match the Website Engagement destination and `contentId` rule; rendered roots get `data-sf-personalization-id` and are observed for visibility; a destination key `Other` appears in logs. The `-view`/`-click` attribute names and any visibility threshold are UNVERIFIED.

## 9. Frontend frameworks: content zone handlers

| Architecture | Slot DOM owner after load | Use | `reinit()` |
| --- | --- | --- | --- |
| Multi-page, server templates (vanilla JS or light enhancements) | HTML, not re-rendered | WPM `Replace an Element` on an `#id` placeholder, or a content zone | No |
| SSR + hydration (Next.js, Nuxt, SvelteKit, Remix, Angular SSR) | Framework | Content Zone Handler in a client component | On client-side navigations |
| SPA | Framework | Content Zone Handler | Yes |
| Islands / partial hydration | HTML or island | Element targeting outside islands; handler inside | Only with client-side routing |
| Server-side render of the decision | Server | Authenticated Decisioning API (§10); you own rendering and view/click events | n/a |

Basis: SDK DOM manipulation "can conflict with the virtual DOM or rendering strategies of modern frameworks" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html). Row assignments are inference. Handler registration timing relative to the decision response is undocumented; test late-mounting components.

```ts
SalesforceInteractions.Personalization.Config.ContentZoneHandler.set(name: string, {
  onReady: (content: string, metadata: ContentZoneHandlerMetadata) => void,  // Required; runtime render
  onRevert?: (metadata: ContentZoneHandlerMetadata) => void,  // design time only (WPM preview cancel); "recommended"
  onHighlight?: (highlight: boolean, metadata?: ContentZoneHandlerMetadata) => void,  // design time; Shadow DOM etc.
  path?: string,   // design time: CSS selector WPM highlights
  label?: string,  // WPM display name; defaults to handler name
});
```

- Rules: don't define both `path` and `onHighlight`; names unique and machine-friendly (e.g. `home_banner`); `onReady` must render, show original children when no content; deregister/reset on unmount (example: `set(name, { onReady: () => {} })`) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html).
- Why: SDK DOM manipulation can conflict with virtual DOM rendering, "causing personalized content to disappear". Troubleshooting: disappearing content → DOM manipulation outside the framework; preview cancel broken → implement `onRevert`; no highlight → fix `path` or add `onHighlight` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html).
- WPM offers `Use Content Zone Handler` only when a handler is registered [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5).

## 10. Decisioning API (server-side and SDK transport)

| Operation | Endpoint (base `https://{tenantSpecificEndpoint}`) | Auth |
| --- | --- | --- |
| Request personalization | `POST /personalization/decisions` (alias `/personalization/v1/decisions`) | None shown; base-URI note targets use "in your Sitemap" |
| Authenticated request | `POST /personalization/authenticated/decisions` (alias `/personalization/v1/authenticated/decisions`) | `Authorization: Bearer <Data Cloud access token>` |

Sources: [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-reference.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-authenticated-request.html)

```json
{ "context": { "individualId": "", "unifiedIndividualId": "", "dataspace": "", "anchorId": "", "anchorType": "",
               "correlationId": "", "messageId": "", "requestUrl": "", "customContextVariable": "" },
  "personalizationPoints": [ { "id": "", "name": "", "decisionId": "" } ],
  "profile": {}, "executionFlags": ["TestMode"] }
```

- `context` and `personalizationPoints` Required; on duplicate keys across `context`/`events`/`profile`, `context` wins. For Accounts replace `individualId` with `profileId` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html).
- `personalizationPoints[]`: `id` or `name`; all points in one request must use the same profile data graph; `decisionId` forces a decision without rule evaluation (testing).
- `profile` (Hot Layer Profile) skips the Data 360 lookup. `executionFlags`: `TestMode` (nothing recorded to the lake), `ContextOnly` (no profile lookup), `EnableDiagnostics`. `requestUrl` enables UTM parsing; `customContextVariable` feeds recommendation filters and isn't recorded; context is logged to the Personalization Record DLO [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html).
- **No profile available (anonymous no-JS pages, edge or server renders):** send `executionFlags: ["ContextOnly"]` ("a call must not look up a profile") and decide on context: `requestUrl` (UTM), `anchorId`/`anchorType`, `customContextVariable`. Profile-based rules and recommender filters then can't match (inference). For experiments without a lookup, `context.unifiedIndividualId` is "only used to enable accurate experimentation partitioning"; `correlationId` attributes one engagement to several requests [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html). On the web, `individualId` is "generated by the SDK" and can't be overridden [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-dynamic-context-variables.html); a server-generated anonymous ID that later joins the web profile is undocumented.
- Response: `{ personalizations: [{ personalizationId, personalizationPointId, personalizationPointName, data: [{ personalizationContentId, … }], attributes: {…}, diagnostics }], diagnostics, requestId }`; `diagnostics` returned only on authenticated requests [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html). Unauthenticated calls log codes to the PersonalizationLog entry; codes resemble but aren't HTTP codes; `decisionId` on an unauthenticated call → `408 SPECIFIED_DECISION_NOT_SUPPORTED` and HTTP `400` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-pipeline-diagnostics.html).
- Mobile SDK response model adds optional `decisionId` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-android.html).
- (Field-observed, undocumented): the Web SDK calls `POST https://<TENANT_ENDPOINT>/personalization/decisions`; responses carry `decisionId` (`9pb…`) and `metadata: {}` per personalization.
- Use cases: server-side/non-SDK channels (authenticated endpoint); Flows via **Get Personalization Decisions** [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/show-personalized-recommendations-in-flows.html); QA with `TestMode` + `decisionId` (authenticated only); standard profile data graphs where the caller supplies the profile.

## 11. Debugging

| `setLoggingLevel(level?: LoggingLevel \| keyof typeof LoggingLevel): void` | Value |
| --- | --- |
| `trace` / `debug` / `info` / `warn` / `error` | `5` / `4` / `3` / `2` / `1` |
| `none` (**default**) | `0` |

- Name or number accepted; a level shows itself and lower. `getLoggingLevel()` returns the number. `SalesforceInteractions.log.{trace,debug,info,warn,error}` prints custom messages gated by the level [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-debugging.html).
- Hooks: `OnPageMatchStatusUpdated` → `matchStatus[]` of `{pageName, status: running|matched|rejected|selected, startTime?, endTime?}`; `OnException` → `{error, context}`; `OnEventSend` → `{actionEvent}`; `OnInitSitemap` → `{currentKey, global, pageTypes, settings}` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).
- Tools: Sitemap Builder `Debug` mode [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_modes.htm&release=264.0.0&type=5); WPM preview with an Individual ID; `EnableDiagnostics` on authenticated calls; PersonalizationLog for unauthenticated calls.
- Console lines at `debug`/`trace`, all undocumented as text (Field-observed, undocumented; meanings inferred):

| Log line | Likely meaning |
| --- | --- |
| `Set Flicker Defense Config to the following` | `customFlickerDefenseConfig` applied |
| `flicker defense currently hiding the following transformations for source matcher type PageType` | Targets (`path`) of page-type-matched experiences hidden until render or timeout |
| `matched enabled personalization experience config names` | Enabled WPM experiences whose Location matches the page |
| `fetching for dataspace [...] points: {...}` | Decisioning call scoped by `personalization.dataspace` |
| `using default value for Substitution Definition of X for Transformer Y` | Template field had no response value; default used |
| `Adding root attribute "data-sf-personalization-id"` / `Observing element for visibility` | Rendered root tagged for attribution; view tracked on visibility |
| `Engagement Tracking: not available (V1) — skipping listener setup` | Possibly no connector-level Personalization Engagement Tracking config |
| `Content Zone … has no Selector` | Zone can't be a DOM target for `Replace a Content Zone`/flicker hiding; harmless for overlay- or handler-only zones |

## Sitemap templates

Copy-ready templates are in [sitemap-templates.md](sitemap-templates.md):
- **§2 Starter sitemap — multi-page / server-rendered site (primary)**: module config → CMP adapter → `init` (`consents` Promise, `cookieDomain`, `personalization.dataspace`) → `initSitemap` with mutually exclusive boolean `isMatch` page types (order confirmation, checkout, cart, item detail, category, home), `ViewCatalogObject` with `anchorId`/`anchorType` context, add-to-cart and sign-out listeners, then separate page-load `ReplaceCart`, `Purchase` (de-duplicated) and `partyIdentification` events. No polling, no `reinit()`.
- **§3 CMP-agnostic consent adapter**; **§4 optional SPA add-on** (client-side routing only); **§5 catalog/cart/order/identity event formats** with landing DMOs.
- The SP example sitemap is "for reference only", hard-codes `OptIn`, and its polling block is labelled "SPA Websites" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html). Content zone syntax: [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-content-zones.html).

## MCP confusion traps

- **Namespace**: MCP uses `window.Evergage`, `Evergage.configure({account, dataset, siteConfigVersion})`, `SalesforceInteractions.mcis.*`; SP uses only `window.SalesforceInteractions` and one `init()` [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_namespace_settings.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_initialization_and_module_settings.htm&release=264.0.0&type=5).
- **Init options**: MCP `trackerUrl` (`https://<accountName>.<instance>.evergage.com`), `dataset` [src](https://developer.salesforce.com/docs/marketing/personalization/guide/sitemapping-getting-started.html); SP `consents`, `cookieDomain`, `personalization.dataspace`, `dataCloud` (§2).
- **Consent default**: MCP proceeds unless opted out, purpose `Personalization`; SP needs explicit opt-in, "if no consent configuration is provided, all users are treated as opted-out", purpose `Tracking` [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5). Authoritative SP basis: §3.
- **Event model**: MCP `action`/`itemAction`, top-level catalog attributes (`catalog.Product._id`); SP `interaction.name` + `interaction.eventType` + `catalogObject {type, id, attributes}`; top-level custom attributes dropped [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_and_data_ingestion.htm&release=264.0.0&type=5).
- **Campaign rendering**: MCP `getCampaignResponses()`, web/server-side campaigns and the SDK Launcher Visual Editor [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_web_campaign_interactions_sdk_launcher.htm&release=264.0.0&type=5); SP has none — it uses WPM + sitemap transformers (handlebars, Shadow DOM, automatic "stat" tracking, element hiding); with `Personalization.fetch()` you own rendering, view/click tracking and flicker defense [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_and_data_ingestion.htm&release=264.0.0&type=5).
- **Content zones**: MCP zones can be strings or objects; `selector` optional for glass-pane popups [src](https://developer.salesforce.com/docs/marketing/personalization/guide/content-zones.html). In SP, zones live only inside page types and `source.contentZones` isn't needed in `sendEvent` [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_content_zone_handling_diffs.htm&release=264.0.0&type=5). **Contradiction**: the migration guide says zones "must have both a name and selector value defined" [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_and_data_ingestion.htm&release=264.0.0&type=5), while the SP dev guide marks `selector` optional and shows selector-less global zones [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-content-zones.html). Give every DOM-rendered zone a selector.
- **Cookies**: MCP `_evga_*`, `_evgn_*`, `_sfid_*` without `sameSite`; SP `_sfid_*` with `secure: true` and `sameSite: "strict"` by default (configurable); the same page also says SP uses "only `_sfic_*`" [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_cookie_id_sdk_diffs.htm&release=264.0.0&type=5).
- **Listeners/events**: MCP `evergage:*`/`mcis:*`, `Evergage.addResponseListener()`/`OnEventResponse`; SP `interactions:*` [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_mod_quicklook.htm&release=264.0.0&type=5). The migration consent page lists `interactions:onConsentGrant`, absent from the SP CustomEvents list [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).
- **Flicker**: MCP flicker protection depends on synchronous beacon loading [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_glossary_defs_a_f.htm&release=264.0.0&type=5); SP uses `customFlickerDefenseConfig` (default `2000` ms). The migration guide's `personalization.flickerDefense {enabled, selector:'body', timeoutMs:3000}` / `personalization.wpm {enabled}` init keys appear in no SP/Data 360 page — treat as unconfirmed [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_initialization_and_module_settings.htm&release=264.0.0&type=5).
- **Chrome tools**: MCP's SDK Launcher is its campaign Visual Editor; SP uses the Launcher only for its Sitemap Editor, or the Data 360 Sitemap Builder; SP authoring happens in WPM.
- **Profiles/server API**: MCP Unified Customer Profile and Event/Channel APIs; SP reads the Data 360 real-time profile data graph and servers call `/personalization/decisions` (§4, §10).
- **Developer docs**: `developer.salesforce.com/docs/marketing/personalization/...` is the MCP guide even though it uses `SalesforceInteractions`; SP is `/docs/marketing/einstein-personalization/...`.
- **Coexistence**: both SDKs share the namespace; enabling coexistence renames the Data 360 side [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_requirements.htm&release=264.0.0&type=5); use `window.getSalesforceInteractions()` outside the sitemap (§2).
- **MCP → Data 360 bundle** maps Consent → `PrivacyConsentLog` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_interaction_studio_bundle_mappings.htm&release=264.0.0&type=5); the SP web connector guide leaves Consent Log unmapped.

## Gaps and uncertainties

- `bfcacheAutoReinit`: undocumented; semantics inferred.
- Tag loading (`async`/`defer`, tag managers, CSP host lists) and content zone handler registration timing: undocumented (§1, §9).
- `init` options: the Data 360 table lists only `consents`, `cookieDomain`; `personalization` appears only in SP pages; `dataCloud.timeTracking` on its own page.
- `reinit` coverage (re-fetch, flicker, WPM re-render) and whether `init()` resolves before a pending `consents` Promise: unstated.
- Web consent pending state: no documented `Pending`/queue; drop-not-queue is observed only. Consent Log `opt-in` vs documented `Opt In`: observed only.
- Engagement internals: `data-sf-personalization-*` attributes, visibility threshold, `Other` destination, "Engagement Tracking … (V1)": undocumented.
- Experience config delivery: how published WPM configs reach the page and the shape of `personalizationExperienceConfigs`: undocumented.
- Doc-vs-doc contradictions: cookie name (`__sfid_${domainHash}_` / `_sfid_*` / `_sfic_*`); `isAnonymous` 0/1 vs `true`; `IDName` vs `IDNameWeb`; `email` vs `emailAddress`; CustomEvent prefix `interactions:` vs `salesforce:`; schema `/250/` vs `/260/`; multi-match merge vs first-`selected`; `global` Required vs omitted; `Array` vs object in `Config.initialize`; zone `selector` optional vs required; standard-graph profile JSON "in the context object" (Help) vs top-level `profile` (API); translation tables map `source.channel` to `sessionId` in several rows (vs `sourceChannel` in the base table — likely doc typo).
- Fetch response shape: web example nests `requestId`/`individualId`/`dataSpace`/`dmoName` per personalization; API reference has top-level `requestId`. `decisionId`/`metadata` in web responses: observed only.
- Unauthenticated endpoint: no auth shown; origin, CORS and rate controls undocumented.
- Identity keying: web `individualId` = `deviceId`/`anonymousId` is inferred from examples.
- CDN script URL format and a formal `sendEvent`/`listener` TypeScript signature: not documented in the pages checked.

## Sources

SP (authoritative) — Help `https://help.salesforce.com/s/articleView?id=mktg.<slug>.htm&release=264.0.0&type=5`:
- `persnl_setup_websdk_ep_module`, `persnl_qs_configure_website_connector`, `persnl_qs_sitemap_building`, `persnl_qs_sitemap_bldr_tabs`, `persnl_qs_sitemap_bldr_modes`
- `persnl_wpm_access_web_personalization_manager`, `persnl_wpm_prerequisites`, `persnl_wpm_use_predefined_templates`, `persnl_wpm_manually_personalize_page_elements`, `persnl_wpm_export_and_publish`, `persnl_wpm_preview_the_experience`, `persnl_experience_web`, `persnl_experience_mobile_publish`, `persnl_experience_mobile_engagement_tracking`
- `persnl_setup_real_time_identity_resolution_for_einstein_personalization`, `persnl_setup_profile_dg_for_max_rev`, `persnl_qs_add_recommended_rules_to_ir_ruleset`, `persnl_setup_data_graphs_using`, `persnl_personalization_point_real_time_profile_data_graphs`, `persnl_personalization_point_standard_profile_data_graphs`

SP developer guide — `https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/<page>.html`:
- `personalize-web-experiences`, `integrate-salesforce-interactions-sdk`, `example-sitemap`, `request-personalization-through-sitemap`, `configure-web-personalization`, `initialize-einstein-personalization-module`, `configure-flicker-defense`, `set-up-content-zones`, `track-personalization-engagement`, `integrate-personalization-modern-frontend-frameworks`
- `decisioning-api-reference`, `decisioning-api-request-personalization`, `decisioning-api-authenticated-request`, `decisioning-api-pipeline-diagnostics`, `show-personalized-recommendations-in-flows`, `batch-personalization-output-dmo`, `personalize-mobile-experiences-android`

Interactions SDK / Data 360 (authoritative) — `https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-<page>.html`:
- `initialization`, `consent`, `consent-data`, `identity`, `api-reference`, `sitemap`, `event-structure`, `user-data`, `translating-sdk-events-to-web-connector-schemas`, `custom-events`, `catalog-interaction`, `cart-interaction`, `order-interaction`, `integration`, `debugging`, `time-tracking`, `salesforce-interactions-web-sdk`, `salesforce-cdp-module-of-the-salesforce-web-sdk`
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-salesforce-web-sdk.html, https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html, https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html, https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-update-mobile-web-datastream.html, https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html
- https://developer.salesforce.com/docs/data/data-cloud-engagement-mobile-sdk/guide/c360a-api-engagement-mobile-sdk-consent-management-v2.html (and `-v3`)
- Data 360 Help `https://help.salesforce.com/s/articleView?id=data.<slug>.htm&release=264.0.0&type=5`: `c360_a_web_mobile_app_connector`, `c360_a_data_stream_schedule`, `c360_a_identity_resolution_real_time`, `c360_a_identity_resolution_configure_real_time_matching`, `c360_a_identity_resolution_unify_partyidentifier`, `c360_a_match_rules_advanced_settings`, `c360_a_ingestion_anonymous_vs_known_profiles`
- Field lessons: [field-guide-web.md](field-guide-web.md), [field-guide-data.md](field-guide-data.md)

Release notes:
- https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_data_360_sitemap_builder.htm&release=260&type=5
- https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_build_customize_experience_templates.htm&release=262.0.0&type=5
- https://help.salesforce.com/s/articleView?id=release-notes.rn_cdp_2026_summer_web_sdk_time_tracking.htm&release=262.0.0&type=5

MCP / MCP-breadcrumb (cited only in MCP ≠ SP statements or contradictions) — Help `mktg.<slug>` at 264.0.0:
- `mc_pers_mcn_for_pers_sitemap_initialization_and_module_settings`, `mc_pers_mcn_for_pers_sitemap_and_data_ingestion`, `mc_pers_mcn_for_pers_sitemap_content_zone_handling_diffs`, `mc_pers_mcn_for_pers_sitemap_consent_mgmt`, `mc_pers_mcn_for_pers_sitemap_cookie_id_sdk_diffs`, `mc_pers_mcn_for_pers_sitemap_mod_quicklook`, `mc_pers_mcn_for_pers_sitemap_namespace_settings`, `mc_pers_mcn_for_pers_requirements`, `mc_pers_web_campaign_interactions_sdk_launcher`, `mc_pers_glossary_defs_a_f`; Data 360 Help `data.c360_a_interaction_studio_bundle_mappings`
- MCP (contrast only): https://developer.salesforce.com/docs/marketing/personalization/guide/sitemapping-getting-started.html, `.../content-zones.html`

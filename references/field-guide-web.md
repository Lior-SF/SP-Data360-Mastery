# Field Guide: Web Implementation Lessons

## Scope

- Lessons verified in real Salesforce Personalization (SP) web implementations that the official docs don't state: consent wiring, identity capture in the browser, sitemap engineering, SPA hardening, WPM placement, and testing the sitemap offline. Data 360 modelling, identity resolution, measurement, credits and rollout: [field-guide-data.md](field-guide-data.md).
- Every lesson is generic. It applies to any site type, industry, consent manager (CMP) or login provider unless it starts with "If the site…". Numbers (timeouts, poll intervals) are examples to measure against, never rules.
- Labels:
  - "(Field-observed, undocumented)": seen in practice and absent from the docs. Re-test after every SDK upgrade and seasonal release. Lessons without another label in §1–§7 carry this label.
  - "(inference)": a design choice built on documented behavior. "(UNVERIFIED)": plausible, confirmed by neither a doc nor a field test.
  - Documented building blocks carry `[src](url)`. CMP behavior is third-party: check it in the vendor's docs.
- Format: **Lesson.** Why it matters. **Do:** the fix. API reference: [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md). Copy-ready code: [sitemap-templates.md](sitemap-templates.md). Symptoms: [troubleshooting.md](troubleshooting.md).
- Placeholders: `<CMP_NAME>`, `<POINT_API_NAME>`, `<CONSENT_WAIT_MS>`, `<NS>` (a prefix for the sitemap's own globals and storage keys).

## 1. Consent wiring

Documented contract: `consents` is required and may be a Promise; "the SDK waits for the `Promise` to resolve before tracking", and `[]` means no tracking until `updateConsents()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html). The SDK stores and sends nothing before an explicit `Opt In` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html). Everything below is about feeding that contract reliably.

### 1.1 Reading the consent manager

- **Read the fastest trustworthy source first.** Many CMPs persist the decision in a first-party cookie that is readable on the sitemap's first line, seconds before their script publishes its JavaScript global. Cold-load gaps of several seconds were observed. Reading only the global keeps returning visitors waiting and out of step with the SDK. **Do:** implement the adapter's `read()` from the live global, with the persisted cookie as fallback, so returning visitors settle `consents` synchronously.
- **Live state outranks the cookie.** On a change, the CMP rewrites its cookie and fires its event in no guaranteed order. A cookie that wins can keep reporting a consent the visitor just withdrew. **Do:** a populated live value always wins. Use the cookie only when the live value is absent or empty.
- **Anchor cookie-name parsing.** Sibling cookies with look-alike names (the target name plus a prefix or suffix) are common, and an unanchored search picks the wrong one. **Do:** match the name at the start of `document.cookie` or right after `; `, and end the value at the next `;`.
- **Locate parameters before decoding.** URL-encoded CMP cookie bodies keep `&` and `=` literal and percent-encode values. Decoding first can turn an encoded `%26key%3D` inside another parameter (a stored landing URL, say) into a forged parameter. **Do:** match `(^|&)key=([^&]*)` on the raw value, then `decodeURIComponent` only the capture.
- **Normalize both sources to one shape.** Cookies often list every category with a verdict (`cat:1`, `cat:0`), while the live global lists only granted ones. Taking the cookie whole reports rejected categories as granted. **Do:** reduce each source to its list of granted categories before comparing or storing.
- **Tokenize category matching.** A substring check lets `CAT10` satisfy `CAT1`. **Do:** split on the delimiter, trim, and compare exact tokens (`list.includes(id)`), never `string.includes(id)`.
- **Parse failure means "unknown", never opt-out, never a throw.** Undocumented CMP formats change without notice, and `document.cookie` itself can throw (sandboxed iframes, privacy extensions). **Do:** wrap every CMP read in `try/catch` and return `null` ("no decision yet"). A format change must cost latency, never consent.
- **An empty answer means "not loaded yet".** If the mapped category is always present once the CMP has loaded, an empty or undefined global means the CMP hasn't answered. Settling on it opts the page load out, and the ceiling timer can't repair that because settling disarms it. **Do:** settle only on a real answer.
- **Keep the change listener attached.** CMPs can fire their change event once before categories are populated, then again with the answer, so a `{ once: true }` listener is spent on the empty event. Some CMPs also expose a single-owner global callback that another script can overwrite. **Do:** subscribe through the CMP's multi-listener event, ignore empty notifications, and never detach after the first answer.
- **Size the consent ceiling from measurements.** Nothing transmits while the `consents` Promise is pending, so overshooting costs little. A short ceiling that settles to "no consent" before a cold-load CMP answers opts out every first visit. `init()` resolves anyway; a pending Promise only delays tracking. **Do:** clear cookies, throttle the network, measure the slowest CMP arrival, and set `<CONSENT_WAIT_MS>` well above it (for example twice).
- **Probe whether the CMP reloads the page on save.** In the console, add a listener for the CMP's change event, set `window.__probe = Date.now()`, then change a preference. If the listener fires and `__probe` survives, the page didn't reload, so the `updateConsents()` handler is mandatory. Without it a withdrawal keeps tracking until the next navigation. (Field-observed technique.)
- **CMP script blocking can remove the SDK.** If the CMP auto-blocks third-party scripts by domain, it can block the SDK itself, and the sitemap's consent gate and mid-session opt-in never run. **Do:** give the CMP owner the connector's CDN host (connector **Integration Guide**), get written confirmation that it's allowed, and gate inside the sitemap instead (inference; vendor behavior).
- **One SDK cookie, one category.** The SDK's first-party cookie serves tracking, rendering and profile stitching, and `Tracking` is the only documented purpose [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html). **Do:** map it to exactly one privacy-approved category, the most restrictive that any of those uses requires. If privacy insists on several, require all of them (inference; privacy decision).

### 1.2 The change handler, replay and memos

- **Call `updateConsents()` synchronously at the top of the change handler, every time.** On a cold load, the init Promise and the handler answer the same CMP event. The Promise's value is applied a microtask later, so a handler that skips the "redundant" update asks a still-closed SDK, declines the replay, and loses the entry page view and the identity bind. **Do:** never optimize that call away.
- **Handler order.**
  1. `updateConsents()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html).
  2. Retry any identity bind attempted while the gate was closed.
  3. Send consent-dependent profile attributes (§1.3).
  4. `reinit()` once, only if the initial view was suppressed and `getConsents()` now reports `Opt In`.

  A closed gate then also suppresses the profile send, so the profile keeps the last permitted state.
- **Decide replay from the SDK, never from the CMP.** Returning visitors can transmit before the CMP publishes, because the SDK restores consent at load. A CMP-based guard then replays a view that already landed and double-counts it. **Do:** read `getConsents()` only, and re-test after upgrades.
- **Fail the replay guard towards "already sent".** If `getConsents()` throws, assume the view transmitted. A lost view is bounded; a false replay is silent double counting.
- **Capture suppression at dispatch time.** Set `initialViewSuppressed = !optedIn()` immediately before `initSitemap()`, after any locale or DOM wait. Declare the variable above the handler that reads it. Captured earlier, consent arriving mid-wait double-counts. A `let` read before its declaration throws inside the listener and kills the consent path.
- **Identical verdicts aren't re-sent.** Repeating `updateConsents()` with an unchanged status produced one `consentLog` row, not two, on current builds. `getConsents()` exposes `lastSentTime` per consent [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html).
- **What's documented about Consent Log rows.** Consent values are attached to "the first event captured after a customer consents to tracking or when a customer revokes consent" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html). Whether an init-time `Opt Out` with no prior opt-in (a fail-closed ceiling) writes a row is undocumented. Confirm it in the `consentLog` DLO before reporting on it.
- **Memoize only what actually transmitted.** Events handed to the SDK before `Opt In` are dropped, not queued, so a persisted "already sent" memo written for a dropped send blocks its own retry for the session. **Do:** check `getConsents()` before writing any memo, and keep "never sent" (`null`) distinct from "sent empty" (`""`).
- **Test opt-out on sites whose banner can't produce it.** Force it from the console with `window.getSalesforceInteractions().updateConsents({ provider: '<CMP_NAME>', purpose: 'Tracking', status: 'Opt Out' })`. Listen for `OnConsentRevoke` and `OnShutDown` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html), and confirm the network stays quiet for events and `/personalization/decisions`. Whether decisions are still fetched after opt-out is UNVERIFIED.

### 1.3 Consent categories as a profile attribute

- **The SDK carries one status; targeting needs a profile field.** Web consent is a single `Tracking` status, so CMP category detail never reaches Data 360. Targeting rules read the profile data graph plus the built-in context resources `Scheduling`, `Source`, `UTM Parameters` and `Visit Context` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_targeting_rules_create.htm&release=264.0.0&type=5), not custom sitemap attributes. Pattern:
  1. Add one optional text field to the `identity` event in the schema: **Update Schema**, then **Sync Schema** ([field-guide-data.md](field-guide-data.md) §2).
  2. Upsert the granted categories on every change. `identity` rows upsert per device. Never put consent on an engagement event: engagement rows append, so "count > 0" would mean "ever consented".
  3. Serialize the list sorted and wrapped in delimiters (`,A,C,`). A text `contains ",A,"` condition then matches exactly one token, and one state can't fragment into permutations. Targeting operators are unpublished, so confirm `contains` exists for text in the decision wizard.
  4. Omit the field when the value is unknown. In partial mode only fields in the update change [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html), so an `""` overwrites the stored value (inference).
  5. Map it to an Individual field. A new field mapping on a ruleset DMO triggers a full ruleset run [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5), so batch it with other identity changes. On a Unified Individual–rooted graph the rule reads the reconciled value, so set a field-level reconciliation rule [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5) that lets the latest device win.
  6. Add the field to the data graph. A published graph accepts additions but not removals [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5).
  7. Re-send the value after every `resetAnonymousId()` (§2.4).

  The value lags the CMP by at least one upsert, so the SDK consent gate stays the compliance boundary. Get privacy sign-off.
- **Rendering-only differences** (hide an embed when a category is declined): set a `data-consent-<category>` attribute on `<html>` from the adapter and hide the element with CSS. No page type, decision or schema change is needed (inference).
- Never branch page types on consent (§3.1).

## 2. Identity capture in the browser

### 2.1 Signals and identifiers

- **Auth signals are observations, not contracts.** Probe each candidate (data-layer flags, DOM text, storage keys, network calls, analytics events) in four states: signed out, signed in, after in-place sign-out, and after a hard reload while signed in. Traps seen:
  - a server-rendered "signed in" flag that never flips on client-side sign-out
  - a logout API call fired when the sign-in panel opens
  - an analytics "success" event fired on panel open
  - site storage keys that keep the user ID after sign-out

  **Do:** bind only on a real identifier. Unbind only on user intent (§2.3).
- **The browser identifier must equal the CRM value.** A party identifier match is an exact match of Identification Number, Identification Name and Party Identification Type [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5). A digest, a variant with or without a check digit, leading zeros, or whitespace drift never match, and nothing reports an error. Letter case matches only while `Case Sensitive` is off: `Exact` ignores case unless that setting is on [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5). Case-significant identifiers need it on ([data-360-foundations.md](data-360-foundations.md)). **Do:** before UAT, read one real signed-in value in the console and find the same string in Party Identification from the CRM source (compare `LENGTH` and case). Normalize with `String(v ?? '').trim()` only. Don't case-fold or strip characters unless the CRM feed does the same.
- **Hashing isn't anonymization.** An unsalted hash of a short numeric ID is reversible. A hashed identifier also needs identical hashing on the CRM side.
- **Send only the signed-in person's own identifiers.** Forms that collect details for other people (companions, recipients, dependants) are not identity sources.
- **Make the identity push a written contract.** If one data-layer push is the only identity source, a missing push produces no error: people stay anonymous and Party Identification stops growing. **Do:** document which pages, load types (including hard reloads while signed in) and subdomains carry it. Monitor sign-ins that produce no `partyIdentification`, and regression-test sign-in and sign-out after every header or tag-manager release.

### 2.2 Reading append-only data layers

- **Scan newest-first.** Tag-manager data layers are arrays that append: a signed-out object on load, a signed-in one later. **Do:** read the identifier from the newest entry that carries the key, not the first.
- **Suppress positionally after logout.** Nothing removes the departing user's entry, so after logout it stays the newest value, possibly for ever. A timed "don't re-bind for N seconds" window only delays re-binding the departing user onto the fresh anonymous ID. **Do:** on logout, store `ignoreBefore = dataLayer.length` and accept only entries pushed after it. Reset the mark if the array shrinks (a tag-manager reload replaced it). Don't clear it on a login-success event that precedes the identity push.
- **Run a login burst.** The site's "login success" signal often lands before the identifier is pushed. **Do:** on that signal, run a short burst of checks (for example every 250 ms for 2 s), each returning at once when bound. Don't shorten the steady-state poll instead.
- **Poll for in-place sign-in.** Overlay or modal sign-in has no navigation, so the identifier appearing is the only signal. **Do:** poll cheaply (for example every 2 s, a no-op while unchanged) and start after `initSitemap`, or the bind lands on an event with no page type.
- **Key auth events on the action**, not on a category that names the credential method. That category changes when a new login method is added.

### 2.3 Sign-out and user switches

- **Arm network logout signals with user intent.** A sign-out click and the app's own logout event are intent, and reset at once. A 2xx from the logout endpoint is only confirmation: accept it only when intent occurred in the last few seconds (for example 10 s), because sites also call that endpoint when the sign-in panel opens. **Do:** make the reset a no-op when nothing is bound, so duplicate signals rotate once. `resetAnonymousId()` deletes the cookie and mints a new ID [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html).
- **Patched site functions must never break the site.** Any hook on `dataLayer.push`, `fetch` or XHR wraps its own logic in `try/catch` and always calls the original. Inspect before forwarding, so a logout reset runs ahead of tag-manager handlers.
- **Persist "who this browser is bound to" in `localStorage`.** Closure state is empty on every load, so a different user signing in looks like a first sign-in and binds onto the old device ID. `sessionStorage` dies with the tab, while the anonymous-ID cookie is reused across sessions [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html). **Do:** on a mismatch, call `resetAnonymousId()` first and bind on the next check. Storage is per origin, while the cookie can span subdomains through `cookieDomain`.
- **Version the storage key when the identifier source or format changes.** Otherwise every browser holding an old-format value looks like a user switch and rotates on release day.
- **Web Storage can throw** (private modes, enterprise policy). Wrap it in `try/catch` and fall back to memory. The cost is extra events, never a lost bind.
- **Drop stale cross-tab memos.** `sessionStorage` is per tab and `localStorage` is shared, so another tab's logout clears the persisted binding but not this tab's session memo. **Do:** on load, drop a session memo that disagrees with the persisted binding.
- **Choose the unbind policy explicitly.** Rotating when a browser merely arrives signed out, or only on explicit sign-out, is a privacy and credit trade-off: [field-guide-data.md](field-guide-data.md) §7.

### 2.4 Profile sends, memos and device rotation

- **Session-scoped "sent" memos are deliberate.** Re-sending profile upserts on every page multiplies Streaming Pipeline rows [src](https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5) for records that upsert on `deviceId` anyway. `localStorage` memos would block the only repair for a bind lost in flight: `sendEvent` gives no delivery confirmation, and `OnEventSend` fires when a request is made [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html). `sessionStorage` allows one repair per session.
- **Key memos to the anonymous ID.** A rotation the sitemap didn't cause (a privacy tool clearing cookies mid-session) otherwise leaves the new device unbound for the session. **Do:** store `getAnonymousId()` with the memos. On load, and on `OnSetAnonymousId` or `OnResetAnonymousId` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html), clear them when the ID changed or can't be read. Don't parse the cookie body; its name differs across doc pages.
- **Re-send profile attributes after `resetAnonymousId()`.** The new ID is a new Individual with none of your custom attributes (consent categories, flags). **Do:** clear the "unchanged value" memos and upsert as anonymous. An `eventType` on that first event also replaces the SDK's automatic minimal identity event [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html).
- **Retry a pre-consent bind from the consent handler**, right after `updateConsents()` (§1.2), not on the next poll.
- **Send `isAnonymous` on every `identity` payload**, consent-only upserts included. The translation table marks it Required [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). **Do:**
  - Derive it from the persisted binding. A per-session flag writes "anonymous" onto a returning known browser before it signs in.
  - Send it as a string when the schema field is Text.
  - Use `1` = anonymous and `0` = known. Ingestion treats `0`, `No`, `N`, `F`, `False` or empty as known [src](https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5); the translation table's example states the reverse.
- **Call SDK methods on the SDK object** (`SI.sendEvent(...)`). Destructured methods can lose their `this` binding. Destructuring constants and `resolvers` is fine.

## 3. Sitemap engineering

### 3.1 Page types

- **Page types classify pages; decisions target people.** The page type name is written on every event as `sourcePageType` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). A page type split by consent or audience duplicates the eligibility rule, splits reporting, and makes a WPM `Current Page Type` binding flip between names. One such split was reverted in practice. **Do:** keep eligibility in targeting rules or profile attributes (§1.3).
- **Match paths on segment boundaries.** `path.startsWith("/section")` also claims `/sectionplus`. **Do:** strip trailing `/`, then accept `path === p || path.startsWith(p + "/")`.
- **Check the hostname** in matchers whose paths recur on other hosts, especially when one sitemap serves several subdomains through a shared `cookieDomain`.
- **Split a page type by locale only when content differs by language.** `Current Page Type` shows an experience "on all website pages of the type you're currently on" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5). A locale-split type keeps one language's content off the other, and reports can filter each audience by page type. The costs: one experience per locale, and events sent before the split keep the old name, so filters count only from the cutover date. Otherwise keep one type and let decisions use context.

### 3.2 Locale

- **Locale is its own dimension.** `locale` is an ISO 639 language code plus an ISO 3166 country code, such as `en_US` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html). **Do:** derive it from the data layer, then from `document.documentElement.lang` normalized (`de-de` → `de_DE`). Don't reuse URL language prefixes (often 3-letter or custom codes), and don't fuse locale into page-type names.
- **If the site is an SPA with a language switcher,** passing `locale` as a function was re-evaluated on `reinit()`. The sitemap reference types `locale` as a string [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html), so re-test after SDK upgrades.
- **Bound the locale wait.** If client code writes locale sources after the sitemap runs, poll briefly before `initSitemap` (for example every 50 ms, capped at 1 s), clear the interval, and proceed without locale at the cap: an empty field beats a missing row. Speeding up init elsewhere (a synchronous consent read) can expose this race.

### 3.3 Robust initialization

- **Guard the Personalization module call.** `if (SI.Personalization && SI.Personalization.Config) { SI.Personalization.Config.initialize({...}); }`, still before `init()` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html). A build without the module then keeps tracking (the failure mode itself is undocumented).
- **Catch the init chain.** `init()` returns a Promise [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html). A throw inside `.then()` (a bad selector, an undefined data layer) is swallowed, and nothing logs even at `debug`. **Do:** end the chain with `.catch((err) => console.error("SP sitemap: initialization failed", err))`.
- **Print a version banner during UAT.** Put `console.info("[SITEMAP] v<N> <date>")` on the first line. A missing or old banner proves a stale upload through **Upload | Replace Sitemap** [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_configure_website_connector.htm&release=264.0.0&type=5), or a cached CDN copy, before any other check.
- **Remove UAT-only lines before go-live:** `setLoggingLevel('debug')`, the banner, and custom traces. Logging defaults to `none` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-debugging.html); debug from the console instead.

### 3.4 Re-injection safety

- The same file often runs twice in one page: the Sitemap Builder `Inject` mode tests a sitemap locally [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_modes.htm&release=264.0.0&type=5), and console pastes and extensions inject too.
- **Use top-level `var` or an IIFE, not `const`/`let`.** A second injection of a top-level `const`/`let` throws `Identifier has already been declared` and kills the whole sitemap. **Do:** test by injecting twice.
- **Guard one-time patches; swap listeners.**
  - Give History API, `fetch`, XHR and `dataLayer.push` patches a marker flag, and route them through `window.__<NS>_HANDLER__` so they reach the latest closure.
  - Swap listeners and intervals: store each reference on `window`, remove or clear the previous one, then register the new one.
  - Skipping them behind a flag leaves the old closure running, so edits appear to do nothing.
- **Test stateful flows by reloading.** Re-injection resets in-memory state (logout suppression, for example).

## 4. SPA routing hardening

If the site changes routes without a full page load. Baseline and add-on: [sitemap-templates.md](sitemap-templates.md) §4. `reinit()` re-runs sitemap evaluation [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html), and `OnInit` is the documented debugging hook for SPAs [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html); expect one per route change.

- **The DOM-settle observer may restart only the debounce, never the ceiling.** If it restarts both, a page that keeps mutating (carousels, live prices) postpones `reinit()` indefinitely: no personalization, no page view, nothing logged.
- **Bind identity before the route's `reinit()`**, after the DOM settles, so the new route's decision can use it. Whether that decision already sees the new match is UNVERIFIED.
- **Test impressions with real navigation.** Automation that calls `history.pushState` doesn't tear down the framework's previous view, so a view event can fire under the new URL. Re-test with in-app navigation before filing a defect.

## 5. WPM placement and anchors

- **State-dependent anchors are a silent partial audience.** If the target element exists only for some users (signed in, a tier, a cookie state), the decision still returns but nothing renders and no view event fires. Reporting then drops that segment without any visible gap. **Do:** test placement with one user in each state that changes the DOM, and ask the site team for a stable, empty, dedicated wrapper that is present for everyone.
- **Avoid selector chains through parent component or tag names** (`<parent-component> .child`). A renamed or misspelled parent matches nothing, with no error. **Do:** prefer a unique `id` (targeted as `#id`), a `data-*` attribute or a unique child tag. The element display methods target the element you click [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5), so check what WPM saved.
- **A returned decision proves nothing about rendering.** Verify decisioning and placement separately. The dependable render check is a `[data-sf-personalization-id]` element inside the target (the attribute itself is undocumented). An empty "flicker defense currently hiding … []" debug line isn't a reliable sign of a missing anchor.
- **If a framework owns the slot's DOM,** register a Content Zone Handler, because SDK DOM manipulation "can conflict with the virtual DOM" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html). Never combine a handler and element replacement on one slot.
- **Retire test experiences.** An experience left `Enabled` on a broad page type or wildcard URL requests a decision on every matching view ([field-guide-data.md](field-guide-data.md) §5).

## 6. Templates and back/forward cache

- The field fixes are in [troubleshooting.md](troubleshooting.md) (rendering symptoms):
  - placeholders in flex columns that measure 0 px wide
  - creative images inside layout templates
  - duplicated renders on back/forward cache restore (`bfcacheAutoReinit: false`, Field-observed)
- Keep template CSS scoped to the template, size it from its container, and make custom rendering idempotent: remove the previous render before inserting.

## 7. Testing the sitemap offline

If the sitemap carries consent, identity or SPA logic, unit-test it. Live UAT alone can't enumerate the timing combinations. (Field-observed practice.)

- **Scenario harness.** Load the real sitemap file into a Node `vm` context with:
  - stubbed browser globals: cookie jar, both storages, data layer, History, `MutationObserver`, `fetch`/XHR
  - a recording SDK stub (`sendEvent`, `reinit`, `updateConsents`, `resetAnonymousId`)
  - a virtual clock, so polls, bursts, ceilings and waits run deterministically

  Cover cold load, returning visit, late or absent CMP, sign-in, sign-out, user switch, SPA navigation and re-injection. Model a reload (both storages kept) separately from a new session (only `localStorage` kept). Read tunables such as timeouts from the source, so retuning can't leave a test checking an old deadline.
- **Stub fidelity.** Model observed SDK behavior: `init()` resolves while `consents` is pending, events transmit only after an explicit `Opt In` (unknown means dropped), and constants use the documented values `Opt In` / `Opt Out` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html). A stub that awaited consent let a build ship that lost the entry view on every cold load. Keep a live cold-load check (cleared cookies, throttled CMP) for races no stub reproduces.
- **Adversarial fixtures.** Surround the real cookie with look-alike names and values containing `=`, `&` or `%26key%3D`, plus malformed CMP values, so naive parsers fail in tests rather than in production.
- **Schema conformance.** Assert each recorded payload against the uploaded schema JSON. No undeclared attributes are allowed, and no required field may be missing other than the beacon-injected `category`, `dateTime`, `deviceId`, `eventId`, `eventType` and `sessionId` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html).
- **Mutation self-test.** Keep a list of `{ from, to }` source patches that reintroduce past bugs. Each must make at least one scenario fail; a surviving mutant marks a blind spot.
- **Mutant hygiene.** Run mutants only against a green baseline, and credit a mutant only with failures that are new against that baseline. Anchor patches on code, not comments, and treat "anchor not found" as an error.
- **Version tests with the sitemap.** Confirm the build banner (§3.3) before each run. Change UAT cases, harness assertions and mutants in the same change as any placement, page-type or consent change. A red suite "fixed" by restoring an old placement can re-create a second placement path.
- **Capture wire payloads.** With debug logging on, the "Events translated for Data Cloud" lines show the wire format, which differs from API values (consent status casing, for example). Wrap `console.debug` to collect them into an array. Pair it with a console probe that returns the device ID, bound identifier, consent categories, locale and path, and call it at each UAT step. The log text is undocumented.
- **User-switch test.** While bound, push a fabricated identifier into the data layer. Expect exactly one rotation, then a bind on the new device, and no device shared by two users. Reuse one fabricated ID (each one creates an orphan profile), and record device-to-user pairs to check in the DMOs after ingestion.
- **Baseline the test environment.** Record backend errors and pre-existing console errors with each run. A failing profile or order service changes what the page renders and can masquerade as an anchor or targeting defect.

## Gaps and uncertainties

- Every CMP behavior in §1.1 (cookie timing, formats, empty first events, reloads, script blocking) is vendor-specific; confirm it per vendor and per vendor release.
- SDK behaviors in this guide are observed, not documented: `init()` resolving while consent is pending, restored consent before the CMP publishes, no second Consent Log row for an unchanged verdict, `locale` as a function, and `data-sf-personalization-id`. Events before `Opt In` are dropped because the SDK doesn't store or transmit until then (documented).
- Undocumented outright: whether an init-time `Opt Out` without a prior opt-in writes a Consent Log row, whether decisions are fetched after opt-out, and whether a route's decision after `reinit()` sees an identity bound just before it.
- Targeting-rule operators (`contains` on text) are unpublished; confirm them in the decision wizard.
- Consent categories stored as a profile attribute lag the CMP by an undocumented delay and need privacy sign-off.

## Sources

Interactions SDK (Data 360 module) — `https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-<page>.html`:
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-debugging.html

Data 360 integration guide and Help:
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5

SP developer guide and SP Help:
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_targeting_rules_create.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_configure_website_connector.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_sitemap_bldr_modes.htm&release=264.0.0&type=5

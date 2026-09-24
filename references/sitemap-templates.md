# Sitemap Templates and Event Formats

## Scope

- Copy-ready Salesforce Personalization (SP) sitemap templates for the Salesforce Interactions SDK (Web SDK): a **multi-page / server-rendered starter** (the primary, default case), a consent-manager (CMP) adapter, an **optional** SPA add-on, and the documented catalog, cart, order and identity event formats with their Data 360 landing objects.
- API detail (`init` options, consent constants, identity methods, sitemap keys, Personalization module, engagement tracking, Decisioning API) lives in [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md); WPM display methods in [wpm-experiences-campaigns.md](wpm-experiences-campaigns.md); failures in [troubleshooting.md](troubleshooting.md).
- Authoritative: SP developer guide (`developer/einstein-personalization`), Interactions SDK Data 360 docs (`developer/data-cloud`), SP Help (`persnl_*`), Data 360 Help. Release 264.0.0 unless stated. Marketing Cloud Personalization (MCP) sitemaps behave differently and are not covered.
- Tags: (inference) = design choice built on documented behavior; (UNVERIFIED) = not confirmed in docs; (Field-observed, undocumented) = seen in real SDK behavior, absent from docs. Third-party (CMP) behavior is marked as such and must be checked in the vendor's own documentation.
- Placeholders: `<PLACEHOLDER>` values, `example.com`. Nothing here is specific to an industry, platform or customer; the item type can be a product, article, offer, service or any catalog object.

## 1. Pick the template

| How pages change | Template | `reinit()` | Slot placement |
| --- | --- | --- | --- |
| Every navigation is a full page load (server templates, most commerce platforms, CMS sites) | §2 starter only | **No** | WPM `Replace an Element` on stable `#id` placeholders, or a sitemap content zone |
| Routes change without a full page load (SPA, or SSR framework with client-side navigation) | §2 starter **plus** §4 add-on | Yes, once per navigation | Content Zone Handler for framework-owned DOM |
| No browser SDK (headless, server-rendered decision, app) | None | n/a | Decisioning API or Engagement Mobile SDK ([mobile-and-channels.md](mobile-and-channels.md)) |

- Why no `reinit()` on multi-page sites: `reinit()` exists for SPAs "where the content and URL change without a full page reload" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html), and the SP example sitemap labels its URL-polling block `/* === SPA Websites === */` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html). A full page load runs the tag, `init` and the sitemap again.
- The SP example is "for reference only" and hard-codes `ConsentStatus.OptIn`; never ship it [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html).
- Framework-owned DOM: SDK DOM manipulation "can conflict with the virtual DOM or rendering strategies of modern frameworks, causing personalized content to disappear"; register a Content Zone Handler instead [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-personalization-modern-frontend-frameworks.html). Architecture → method table: [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §9.

## 2. Starter sitemap — multi-page / server-rendered site (primary)

Documented APIs only; comments marked (inference) are design choices. Replace every `<PLACEHOLDER>`. No polling and no `reinit()`. Remove page types and events the site doesn't have.

```js
/* Re-injection (Sitemap Builder Inject, console paste) re-runs this file: wrap it in an IIFE or use
   top-level var instead of const/let, or the second run throws (field-guide-web.md §3.4). */
/* ===== 1) Personalization module FIRST (must precede init) ===== */
SalesforceInteractions.Personalization.Config.initialize({   // guard with if (SalesforceInteractions.Personalization) if a build may lack the module
  customFlickerDefenseConfig: { redisplayTimeoutMilliseconds: 2000, renderPersonalizationAfterTimeoutElapsed: false }, // documented defaults
});

const SI = SalesforceInteractions;

/* ===== 2) Consent adapter (see §3). CMP calls are PLACEHOLDERS for your vendor's documented API ===== */
const CMP = {
  provider: "<CMP_NAME>",                 // recorded as consent.provider
  read: () => null,                       // PLACEHOLDER: return true | false | null (no decision yet) for the ONE approved category/purpose
  subscribe: (callback) => {},            // PLACEHOLDER: call callback(true | false) on the first decision and on every later change
};
const CONSENT_WAIT_MS = 5000;             // <CONSENT_WAIT_MS>: ceiling so the consents Promise always settles (inference); size it well above measured cold-load CMP arrival
const toConsent = (granted) => ({
  provider: CMP.provider,
  purpose: SI.ConsentPurpose.Tracking,
  status: granted ? SI.ConsentStatus.OptIn : SI.ConsentStatus.OptOut,
});
let settled = false, resolveConsents;
const initialConsents = new Promise((resolve) => { resolveConsents = resolve; });
const settleOnce = (value) => { if (!settled) { settled = true; resolveConsents(value); } };
const stored = CMP.read();
if (stored !== null) settleOnce([toConsent(stored)]);
setTimeout(() => settleOnce([]), CONSENT_WAIT_MS);    // [] = no tracking until updateConsents()
CMP.subscribe((granted) => {
  SI.updateConsents(toConsent(granted));          // every time, first: the Promise applies a microtask later (field-guide-web §1.2)
  if (!settled) settleOnce([toConsent(granted)]);
});
const isOptedIn = () => SI.getConsents().some(({ consent }) =>
  consent.purpose === SI.ConsentPurpose.Tracking && consent.status === SI.ConsentStatus.OptIn);

/* ===== 3) Page matchers: mutually exclusive, return a BOOLEAN (never a Promise) ===== */
const path = () => window.location.pathname;
const is = {
  orderConfirmation: () => /<ORDER_CONFIRMATION_PATH_REGEX>/.test(path()),
  checkout:          () => /<CHECKOUT_PATH_REGEX>/.test(path()),
  cart:              () => /<CART_PATH_REGEX>/.test(path()),
  itemDetail:        () => /<ITEM_DETAIL_PATH_REGEX>/.test(path()),
  category:          () => /<CATEGORY_PATH_REGEX>/.test(path()),
  home:              () => path() === "/",
};
const onDomReady = (fn) => (document.readyState === "loading"
  ? document.addEventListener("DOMContentLoaded", fn, { once: true }) : fn());   // the tag runs in <head> (inference)

/* ===== 4) Site data readers: prefer a server-rendered data layer or JSON-LD over DOM scraping ===== */
const readItemId = () => /* id of the item on this detail page */ null;
const readCartLines = () => /* [{ catalogObjectType: "<ITEM_TYPE>", catalogObjectId, quantity, price, currency }] */ [];
const readAddedLine = () => /* the line just added: { catalogObjectType, catalogObjectId, quantity, price?, currency? } */ null;
const readOrder = () => /* { id, totalValue, currency: "<CURRENCY>", lineItems: [...] } on the confirmation page, else null */ null;
const readKnownUserId = () => /* signed-in ID (newest data-layer entry carrying it), trimmed, else null; never "NA", "null", "0" */ null;

/* ===== 5) Page-load commerce and identity events: separate calls, after the page interaction (inference) ===== */
const sendPageLoadEvents = () => {
  if (!isOptedIn()) return;                                   // nothing is transmitted before Opt In
  if (is.cart()) {                                            // cart snapshot; [] = empty cart
    SI.sendEvent({ interaction: { name: SI.CartInteractionName.ReplaceCart, lineItems: readCartLines() } });
  }
  const order = is.orderConfirmation() && readOrder();
  if (order && sessionStorage.getItem("sp_order_sent") !== order.id) {       // no duplicate purchase on reload (inference)
    SI.sendEvent({ interaction: { name: SI.OrderInteractionName.Purchase, order } });
    sessionStorage.setItem("sp_order_sent", order.id);
  }
  const userId = readKnownUserId();
  let anonId = "";
  try { anonId = SI.getAnonymousId() || ""; } catch (e) { anonId = ""; }
  const partyMemo = anonId + ":" + userId;                    // key to the anonymous ID (field-guide-web §2.4)
  if (userId && anonId && sessionStorage.getItem("sp_party_sent") !== partyMemo) {
    SI.sendEvent({ user: { attributes: {                      // separate event: never on the first action event
      eventType: "partyIdentification",
      IDNameWeb: "<ID_NAME>",                                  // SDK translation name; SP mapping DLO column may be IDName — match the uploaded schema
      IDType: "<ID_TYPE>",
      userId,
    } } });
    sessionStorage.setItem("sp_party_sent", partyMemo);       // write only after Opt In (guard above)
  }
};

/* ===== 6) init + sitemap ===== */
SI.init({
  consents: initialConsents,                                  // required
  cookieDomain: "<REGISTRABLE_DOMAIN>",                       // e.g. "example.com" to share identity across subdomains; omit for one host
  personalization: { dataspace: "<DATA_SPACE>" },             // data space of your points ("default" if you have only one)
}).then(() => {
  const { listener, resolvers, CatalogObjectInteractionName, CartInteractionName } = SI;
  // Run page-load events after the first event of this page is sent (the page interaction) (inference):
  document.addEventListener(SI.CustomEvents.OnEventSend, () => onDomReady(sendPageLoadEvents), { once: true });
  const clearPartyMemo = () => { try { sessionStorage.removeItem("sp_party_sent"); } catch (e) {} };
  document.addEventListener(SI.CustomEvents.OnResetAnonymousId, clearPartyMemo);
  document.addEventListener(SI.CustomEvents.OnSetAnonymousId, clearPartyMemo);

  SI.initSitemap({
    global: {
      locale: "<LOCALE>",                                     // e.g. "en_US": from the data layer or <html lang>, normalized to ll_CC
      listeners: [
        listener("click", "<ADD_TO_CART_SELECTOR>", () => {   // or call sendEvent from the site's own add-to-cart code
          const lineItem = readAddedLine();
          if (lineItem) SI.sendEvent({ interaction: { name: CartInteractionName.AddToCart, lineItem } });
        }),
        listener("click", "<SIGN_OUT_SELECTOR>", () => SI.resetAnonymousId()),   // shared devices: new anonymous ID after sign-out
      ],
      onActionEvent: (event) => event,                        // must return the event
    },
    pageTypeDefault: { name: "default", interaction: { name: "Default Page View", eventType: "userEngagement" } },
    pageTypes: [                                              // first match is selected: most specific first
      { name: "order_confirmation", isMatch: is.orderConfirmation,
        interaction: { name: "Order Confirmation View", eventType: "userEngagement" } },
      { name: "checkout", isMatch: is.checkout,
        interaction: { name: "Checkout View", eventType: "userEngagement" } },
      { name: "cart", isMatch: is.cart,
        interaction: { name: "Cart View", eventType: "userEngagement" } },
      { name: "item_detail", isMatch: is.itemDetail,
        interaction: { name: CatalogObjectInteractionName.ViewCatalogObject, catalogObject: {
          type: "<ITEM_TYPE>",                                // e.g. Product, Article, Offer
          id: resolvers.fromSelectorAttribute("<ITEM_ROOT_SELECTOR>", "<ITEM_ID_ATTR>"),   // or fromJsonLd(...), fromMeta(...), fromWindow("<DATA_LAYER_PATH>")
        } },
        contextualAttributes: {                               // anchor for "similar / bought together" recommenders
          anchorId: readItemId,
          anchorType: "<ITEM_DMO_API_NAME>",                  // DMO API name, e.g. ssot__GoodsProduct__dlm
        } },
      { name: "category", isMatch: is.category,
        interaction: { name: CatalogObjectInteractionName.ViewCatalogObject, catalogObject: {
          type: "Category",                                   // lands with item views; filter on type downstream (§5)
          id: resolvers.fromSelectorAttribute("<CATEGORY_ROOT_SELECTOR>", "<CATEGORY_ID_ATTR>"),
        } } },
      { name: "home", isMatch: is.home,
        interaction: { name: "Home View", eventType: "userEngagement" } },
    ],
  });
}).catch((err) => console.error("SP sitemap: initialization failed", err));   // a throw in .then() is otherwise silent
```

- API basis: module before `init` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/initialize-einstein-personalization-module.html); `init` → `initSitemap` in `.then()`, `consents` as `Consent[]` or `Promise<Consent[]>`, `[]` = no tracking until `updateConsents()`, `cookieDomain` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html); `personalization.dataspace` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html); sitemap keys, resolvers, `listener`, `onActionEvent` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-sitemap.html); `contextualAttributes` in `global` or `pageTypes`, value = string, function or Promise, `anchorType` = "The Data Model Object name associated with the anchor item" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-dynamic-context-variables.html); `CustomEvents.OnEventSend` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html); `resetAnonymousId()` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-identity.html).
- Contracts:
  - Page type `name` values are the WPM `Current Page Type` binding and the events' `sourcePageType` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). Don't rename them after go-live.
  - `userEngagement` and every custom event or attribute must exist in the uploaded connector schema; **Update Schema** only adds [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html).
  - `<ID_NAME>` / `<ID_TYPE>` must match the real-time identity resolution match rule [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5).
- Placement: the starter declares no content zones. Ask the site team for empty, stable `#id` placeholders and target them in WPM with `Replace an Element`. To use zones instead, add `contentZones: [{ name, selector }]` to a page type and use `Replace a Content Zone` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/set-up-content-zones.html). Never both for the same slot.
- Why identity is a separate call: the SDK's automatic anonymous `identity` event is sent only when the first action event after an anonymous-ID change carries no `user.attributes.eventType` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html). Putting `partyIdentification` on the page interaction (for example via `onActionEvent`) suppresses it on a new device.
- Identity hardening (Field-observed, undocumented): the sign-out listener is the simplest case. Sites also need intent-armed network logout signals and a reset that's a no-op when nothing is bound. Append-only data layers need newest-first reads and positional suppression after logout. The `sessionStorage` memos are deliberately session-scoped (one repair per session), but key them to `getAnonymousId()` and write them only after `Opt In`. Patterns: [field-guide-web.md](field-guide-web.md) §2.
- In-page changes without navigation (quick view, variant switch, filters, tabs): send a catalog event such as `QuickViewCatalogObject` with `sendEvent` from a listener [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-catalog-interaction.html). Don't call `reinit()`.
- Add to cart: the cart docs send `AddToCart` either from a sitemap listener or "from within your site's custom 'addToCart' function" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-cart-interaction.html). Sitemap and cart examples pass a callback argument `(event)`; the shape of that object isn't documented, so read the line from the site's data layer; outside the sitemap use `window.getSalesforceInteractions()`.
- Timing: whether `initSitemap` waits for DOM ready before running resolvers is undocumented (UNVERIFIED). Prefer values available in `<head>` (a data layer on `window` set before the tag, `fromMeta`, `fromJsonLd`), or test on slow pages.
- First page before a first-time consent decision: if the decision arrives after the page interaction, that page view isn't sent. The SDK doesn't store or transmit before `Opt In`, so those events are dropped, not queued [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html). `init()` resolving while the consents Promise is still pending is Field-observed, undocumented. On a multi-page site the next full load tracks normally. Replaying that one view is optional; see [troubleshooting.md](troubleshooting.md) (consent symptoms).
- `OnEventSend` "is dispatched after an event has been successfully processed, and a request is made" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html); using its first occurrence as the "page interaction sent" signal is inference. If consent arrives mid-page, the page-load events run after the next sent event; the `isOptedIn()` guard blocks them before opt-in.

## 3. Consent manager adapter (CMP-agnostic)

- Documented contract:
  - `consents` is **Required** in `init`; the SDK "waits for the `Promise` to resolve before tracking" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
  - Use a Promise "when waiting for a user action … or for a third-party Consent Management Platform (CMP) to load"; pass `[]` when the user hasn't decided [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
  - `updateConsents(Consent | Consent[])` handles later changes; the docs show calling it "directly from your OneTrust or custom consent management provider's code" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html).
  - The only documented purpose is `Tracking`; statuses `Opt In` / `Opt Out`; `provider` is the CMP name [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html).
- Third-party (verify in the CMP vendor's own docs): most CMPs expose (1) a read of the stored decision per category or purpose, (2) a callback or DOM event on the first decision and on later changes, and (3) sometimes a "loaded / ready" signal; some implement the IAB TCF API. The adapter's `read()` and `subscribe()` are placeholders for exactly those calls; keep all vendor code inside them.
- Rules (inference):
  - Map exactly **one** privacy-approved CMP category or purpose to SP `Tracking`. Never map an always-granted category (for example "strictly necessary"): it opts in everyone. Compliance stays with the site owner [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html).
  - Always let the Promise settle: on the stored decision, on the first decision, or with `[]` after a ceiling. A Promise resolving `[]` isn't a documented shape; test it, or resolve with an explicit `Opt Out` after privacy sign-off. Whether that init-time `Opt Out` writes a Consent Log row is undocumented ([web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §3).
  - Field hardening (Field-observed, undocumented):
    - Implement `read()` from the CMP's live state, with its persisted cookie as fallback, so returning visitors settle at once.
    - Parse cookies anchored on the name, and match categories as exact tokens.
    - Treat empty or unparseable answers as `null`.
    - Keep `subscribe()` attached (no `{ once: true }`), and call `updateConsents()` synchronously at the top of the change handler.
    - Probe whether the CMP reloads the page on save.

    Details: [field-guide-web.md](field-guide-web.md) §1.
  - After settling, route every change through `updateConsents()`; on `Opt Out` the SDK "immediately stops emitting events" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-salesforce-interactions-web-sdk.html).

## 4. Optional SPA add-on (client-side routing only)

Add this **only** if routes change without a full page load (SPA, or an SSR framework with client-side navigation). Paste it inside `init().then(...)`, after `SI.initSitemap(...)`. A multi-page site never needs it.

```js
  /* ===== OPTIONAL SPA ADD-ON: only for client-side routing ===== */
  // Documented baseline: poll the URL and reinit on change (SP example 500 ms; SDK example 200 ms).
  let currentUrl = window.location.href;
  setInterval(() => {
    if (currentUrl !== window.location.href) { currentUrl = window.location.href; SI.reinit(); }
  }, 500);
  // Page-load events run once per full load; re-arm them for each virtual page (inference):
  document.addEventListener(SI.CustomEvents.OnInit, () =>
    document.addEventListener(SI.CustomEvents.OnEventSend, () => onDomReady(sendPageLoadEvents), { once: true }));
```

- Basis: polling and `reinit()` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/example-sitemap.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-initialization.html); `OnInit` is the documented hook for SPAs that "reinitialize without a page load event" [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-integration.html).
- Hardening (Field-observed, undocumented): prefer the router's "navigation complete" hook to polling; debounce until the new route's DOM settles, with a hard ceiling that the MutationObserver never restarts; one `reinit()` per navigation; verify exactly one `OnInit` and one `/personalization/decisions` request per route change. On re-injection, swap listeners and intervals (remove the previous one, then add) and route one-time patches through a `window` pointer to the current closure ([field-guide-web.md](field-guide-web.md) §3.4, §4).
- Scripts that change the URL without navigating (`history.replaceState` for filters or anchors) also trigger the poll and re-send the page interaction; ignore those URL changes or compare only the path (Field-observed, undocumented).
- Render framework-owned slots with Content Zone Handlers ([web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §9), not WPM element replacement.

## 5. Event formats: catalog, cart, order, identity

| Action | `interaction.name` constant → value | Required shape (+ optional) | Web connector `eventType` → starter DMO |
| --- | --- | --- | --- |
| View any catalog item (product, category, article…) | `CatalogObjectInteractionName.ViewCatalogObject` → `View Catalog Object`; also `ViewCatalogObjectDetail`, `QuickViewCatalogObject`, `FavoriteCatalogObject`, `ShareCatalogObject`, `ReviewCatalogObject`, `CommentCatalogObject` (values are the spaced words) | `catalogObject: { type, id }` (+ `attributes`, `relatedCatalogObjects`) | `catalog` → Product Browse Engagement |
| Add / remove one line | `CartInteractionName.AddToCart` → `Add To Cart`; `.RemoveFromCart` → `Remove From Cart` | `lineItem: { catalogObjectType, catalogObjectId, quantity }` (+ `price`, `currency`, `attributes`) | `cart` + child `cartItem` (`cartEventId`) → Shopping Cart Engagement + Shopping Cart Product Engagement |
| Replace the whole cart (login merge, snapshot; `[]` = empty) | `CartInteractionName.ReplaceCart` → `Replace Cart` | `lineItems: [...]` | same |
| Order lifecycle | `OrderInteractionName.Purchase` → `Purchase`; also `Return`, `Cancel`, `Preorder`, `Exchange`, `Ship`, `Deliver` | `order: { id, totalValue }` (+ `currency`, `lineItems`, `attributes`) | `order` (`orderId`, `orderTotalValue`, `orderCurrency`) + line rows (`orderEventId`) → Product Order Engagement + Sales Order Product Engagement |
| Known-user key | `user.attributes.eventType: "partyIdentification"` | `IDNameWeb` (SP mapping guide DLO: `IDName`), `IDType`, `userId` | `partyIdentification` (Profile) → Party Identification |
| Name / anonymous flag | `eventType: "identity"` | `firstName`, `lastName`, `isAnonymous` | `identity` → Individual |
| Email / phone | `eventType: "contactPointEmail"` / `"contactPointPhone"` | `email` / `phoneNumber` | same → Contact Point Email / Phone |

Sources: [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-catalog-interaction.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-cart-interaction.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-order-interaction.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-line-item-data.html) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html)

- Catalog items are "any trackable item from your catalog, such as products, categories, articles"; `catalogObject.type` examples are `Product`, `Blog` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-catalog-interaction.html). Line-item `catalogObjectType` examples are `Product`, `Service` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-line-item-data.html).
- Non-product types land in the same `catalog` DLO and Product Browse Engagement (the starter mapping sends `type` to Product Category and `id` to Product [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html)). Filter on `type` in calculated insights and recommender filters, or send non-item views as a custom event (inference).
- The SP web mapping guide leaves `Order Item` "Not mapped" [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html), but the starter mapping sends Order Event Items to Sales Order Product Engagement (`orderEventId` → Product Order Engagement) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html). Map it when using Maximize Revenue or order-line insights.
- Maximize Revenue needs `SalesOrderProductEngagement.ProductOrderEngagementId` mapped and an active N:1 relationship from Sales Order Product Engagement to Product Order Engagement; Shopping Cart Product Engagement → Shopping Cart Engagement N:1 is optional [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_profile_dg_for_max_rev.htm&release=264.0.0&type=5).
- Custom `attributes` on catalog objects, line items and orders become `attributeCustomFieldN` and "aren't automatically defined in the recommended schema"; add them by hand (the docs' `giftWrapping` example needs this too) [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html).
- Doc quirks: the translation page labels order line rows `eventType = "order"` (the starter mapping calls the DLO Order Item); the Line Item page's example uses a `View Cart` name with `lineItems`, which isn't a `CartInteractionName` constant. Use the names in your uploaded schema [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-line-item-data.html).
- Personalization view/click events (`personalization-view` / `personalization-click`, or `catalog-object-view-start` / `catalog-object-click` for recommendations) are covered in [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §8.

## 6. Test before go-live (multi-page)

- Per full page load: exactly one `OnInit`, one `selected` page type, one page interaction, and one `/personalization/decisions` request per page with experiences (debug snippet in [troubleshooting.md](troubleshooting.md)).
- First visit, consent not yet given: nothing is sent; after opt-in, the next event is sent and the Consent Log receives the change.
- Order confirmation reload: one `Purchase` only. Sign-in: one `partyIdentification` per user per session, never on the first event of a new device.
- Data lands in the expected DMOs (Product Browse, Shopping Cart, Product Order engagement) before building insights or recommenders.

## Gaps and uncertainties

- Tag loading: `async`/`defer`, tag-manager deployment and CSP host lists are undocumented for SP (see [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §1).
- Whether `initSitemap` waits for DOM ready before resolving selectors; whether the page interaction is always the first `OnEventSend` of a page or virtual page; whether `init()` resolves before a pending `consents` Promise (observed: yes).
- `sitemap` listener handler arguments; handler registration timing relative to the decision response for late-mounting components.
- Doc-vs-doc: `IDName` vs `IDNameWeb`; `isAnonymous` `0`/`1` vs `true`; order line `eventType` label; `Order Item` "Not mapped" (SP guide) vs mapped (starter mapping).
- Targeting-rule operators remain unpublished ([decisioning.md](decisioning.md) §6.3).

## Sources

SP developer guide — `https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/<page>.html`:
- `example-sitemap`, `initialize-einstein-personalization-module`, `integrate-salesforce-interactions-sdk`, `request-personalization-through-sitemap`, `set-up-dynamic-context-variables`, `set-up-content-zones`, `integrate-personalization-modern-frontend-frameworks`

Interactions SDK / Data 360 — `https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-<page>.html`:
- `initialization`, `consent`, `consent-data`, `identity`, `user-data`, `sitemap`, `integration`, `catalog-interaction`, `cart-interaction`, `order-interaction`, `line-item-data`, `translating-sdk-events-to-web-connector-schemas`, `salesforce-interactions-web-sdk`
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-sdk-mappings-for-engagement-events.html

SP Help — `https://help.salesforce.com/s/articleView?id=mktg.<slug>.htm&release=264.0.0&type=5`:
- `persnl_setup_profile_dg_for_max_rev`, `persnl_setup_real_time_identity_resolution_for_einstein_personalization`

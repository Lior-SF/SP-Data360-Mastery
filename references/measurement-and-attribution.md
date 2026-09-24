# Measurement: Engagement Signals, Attribution, Analytics and Reporting

## Scope
- How Salesforce Personalization (SP) measures personalization: engagement signals, engagement signal metrics and compound metrics, attribution models (predefined and custom), Attribution Intelligence, Pipeline Intelligence, Tableau, Intelligence SQL, and Data 360 reports, dashboards and calculated insights (CIs).
- Release 264.0.0 unless stated. Authoritative: SP Help (`persnl_*`, `mc_persnl_*`), `developer/einstein-personalization`, Data 360 Help and DMO guide, Reports and Dashboards Help, release notes. Marketing Cloud Personalization (MCP) pages appear only in "MCP confusion traps".
- Tags: `(UNVERIFIED)` = not confirmed in docs; `(Field-observed, undocumented)` = seen in a live SP org, not documented; `(inference)` = reasoned from documented rules.

## 1. Engagement signals and metrics

### 1.1 Where web engagement events come from
- SDK out-of-the-box destinations: `Product Engagement` → event type `catalog` → Product Browse Engagement DMO, interaction names `catalog-object-view-start` / `catalog-object-click`; `Website Engagement` → event type `userEngagement` → Website Engagement DMO, interaction names `personalization-view` / `personalization-click`, for Dynamic Content, formerly Manual Content (no `id`/`type` in payload). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html)
- Custom destinations can override `interaction-name` (function receives `context.name` = `view` | `click`). Manually sent events must carry `personalizationId` and `personalizationContentId`; "For a specific product, set `contentId` to the `personalizationContentId` value from the JSON response. Otherwise, set it to the `personalizationId`." [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html)
- Connector-level tracking (Data Cloud Setup → `Websites and Mobile Apps` → connector → `Personalization` tab → `Add Tracking Event`), once per content schema; defaults `View Action` = `personalization-view`, `Click Action` = `personalization-click`, `Dismiss Action` = none; Data 360 engagement events only (no profile, cart, order events); permission `Data Cloud admin`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_mobile_engagement_tracking.htm&release=264.0.0&type=5)
- Web connector mapping: Catalog `personalizationId` → Product Browse Engagement `Personalization`; `personalizationContentId` → `Personalization Content`; `interactionName` → `Engagement Channel Action`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_behavioral_events_data_mapping_ref.htm&release=264.0.0&type=5) Identity DLO `deviceId` → Individual `Individual ID`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html)

### 1.2 Definition, uses, permissions
- An engagement signal is "a set of data that provides information about an engagement action performed by an individual" (web clicks, email open/response, PDF download). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals.htm&release=264.0.0&type=5)
- Used by custom recommender objectives, custom attribution models and personalization experiments; docs recommend defining signals first. Only DMOs of category Engagement; only mapped DMOs and fields. Permission: `Engagement Signals` (also for metrics and compound metrics). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5)
- Standard permission set `Personalization Admin` has full CRUD on `Engagement Signals`, `Engagement Signal Compound Metrics`, `Attribution Models`; `Personalization User` has only `Read` / `View All` on those three (no separate "Engagement Signal Metrics" object row is listed). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5)

### 1.3 Create a signal (App Launcher → `Engagement Signals` → `New`)
1. `Manual Setup` or `Use a Data Kit` (only unmanaged data kits; required DMOs and mappings must already exist).
2. Data space → engagement DMO (menu lists only mapped DMOs of category Engagement).
3. Optional checkbox to make the signal available in flows (SP plus Marketing Cloud Next automation-event-triggered flows). "Related object fields are unsupported in flows"; selecting it excludes related objects.
4. Identifier fields from the DMO or from one related DMO (mapped fields only), see 1.4.
5. Counting: `Count each event as a discrete engagement signal` (default) or `Define added fields to group repeat events, and count them as one signal` (pick fields that make an occurrence unique, e.g. individual ID + message ID + click).
6. Optional filters: `Add Condition`; `Condition Requirements` = `All Conditions Are Met` (AND) or `Any Conditions Is Met` (OR); filter resource = field of the primary or the related DMO. No filters = all engagements.
7. Name (API name auto-generated) → save.
- All steps: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5)
- Trap (inference): a flow-enabled signal cannot use a related DMO, so it cannot filter on Personalization Log fields such as the personalization point.

### 1.4 Identifier fields
| Field | Docs meaning | Documented example (`Product View`) |
| --- | --- | --- |
| `User Identifier` | general user identifier (email, phone, other ID) | `Product Browse Engagement > Individual` |
| `Timestamp Identifier` | date/time captured for the engagement | `Product Browse Engagement > Engagement Date Time` |
| `Item Identifier` | isolates the item; required if the signal is used in custom objective-based recommenders | `Product Browse Engagement > Product SKU` |
| `Event Identifier` (examples label it `Unique Engagement Identifier`) | unique event ID; groups identical engagements, removes duplicates | `Product Browse Engagement > Product Browse Engagement Id` |

- Sources: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_examples_prod_view_engmt.htm&release=264.0.0&type=5)
- Example filters: `Engagement Channel Action` `Is Equal To` `catalog-object-view-start` (API name `ProductView`) or `catalog-object-click` (API name `ProductClick`); `All Conditions Are Met`; data space `default`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_examples_prod_click_engmt.htm&release=264.0.0&type=5)

### 1.5 Filter operators
| Operator | Supported types |
| --- | --- |
| `Is Equal To`, `Has No Value`, `Has Value` | All |
| `Is Less Than`, `Is Less than Or Equal To`, `Is Greater Than`, `Is Greater Than Or Equal To` | Number, Percent, Currency |
| `Is Not Equal To` | String, Number, Percent, Currency |

- [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5). Added in Spring '26 (260) for custom objectives, attribution models and experiments (e.g., exclude `Is Test Send` = True). [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_added_es_filter_operators.htm&release=260&type=5)

### 1.6 Related DMOs and the Personalization Log requirement
- Signal fields can come from the primary DMO and related DMOs with one-to-one or many-to-one cardinality, but from only one related DMO (limit `1`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5)
- Attribution eligibility, verbatim: "For an engagement signal to be eligible for use in a funnel stage, it must have an active relationship with the Personalization Log DMO." [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5)
- Website Engagement → Personalization Log is a standard N:1 relationship (related field `Personalization Log Id`). [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html) In the Data 360 standard model the foreign key is `PersonalizationContentId` → Personalization Log `Id`. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-websiteengagementdmo-dmo.html)
- Other standard engagement DMOs with the same `PersonalizationContentId` → Personalization Log `Id` foreign key (attribution-eligible once the stream maps that field): Website Item [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-websiteitemengagementdmo-dmo.html), Product Browse [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-productbrowseengagementdmo-dmo.html), Shopping Wishlist [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-shoppingwishlistengagementdmo-dmo.html), Shopping Wishlist Item [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-shoppingwishlistitemengagementdmo-dmo.html), Shopping Cart Product [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-shoppingcartproductengagementdmo-dmo.html), Sales Order Product [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-salesorderproductengagementdmo-dmo.html), Media (also FKs to Digital Content and Electronic Media) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-mediaengagementdmo-dmo.html), Lead [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-leadengagementdmo-dmo.html), Social Message [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-socialmessageengagementdmo-dmo.html), Promotion Engagement [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-promotionengagementdmo-dmo.html). An Email Engagement FK was not confirmed; check the org's Data Model tab → DMO → Relationships.
- Non-web pattern (inference from the fields above; not a doc recipe): store the response's `personalizationContentId` (item) or `personalizationId` with the outcome event (app, contact center, kiosk, email landing), ingest it into one of these DMOs with `PersonalizationContentId` mapped (server-side: the Data 360 Ingestion API streaming pattern [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-ingestion-api.html)), then build the signal on that DMO. Request fields `correlationId` ("attribution involving multiple personalization requests") and `messageId` ("an individual outbound message") exist for such flows [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-authenticated-request.html). `TestMode` records no outputs to the data lake, so test-mode responses have no log rows to join (inference).
- Personalization Log `Id`: "Primary Key Personalization Content Id must store the same value". [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html)
- Website Engagement has no personalization point field; `PersonalizationPointId` and `PersonalizationDecisionId` live on Personalization Log, so point-level filtering of a web signal goes through the related Personalization Log. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html)

### 1.7 Engagement signal metrics
- "By default, a count-based engagement signal metric is created for each engagement signal"; it can be used like any other metric. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_configure.htm&release=264.0.0&type=5) Documented default names: `Count ProductView`, `Count ProductClick`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_examples.htm&release=264.0.0&type=5) Auto-created API names follow `Count_<SignalApiName>` (Field-observed, undocumented).
- Create: open signal → `Related` tab → `Engagement Signal Metrics` → `New` → name, optional description → `Aggregate` menu → DMO field → save. Ingesting the same event from multiple data streams can duplicate rows and inflate `COUNT`; docs recommend `DISTINCT`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_configure.htm&release=264.0.0&type=5)

| Aggregation | Meaning | Supported in |
| --- | --- | --- |
| `COUNT` | counts all entries (rows) | Custom Objectives, Custom Attribution Configurations, Experimentation |
| `SUM` | adds values | Custom Attribution Configurations, Experimentation |
| `AVG` | averages values | Custom Attribution Configurations, Experimentation |
| `DISTINCT` | counts unique values | Custom Attribution Configurations, Experimentation |
| `SELECT` | lets models use an attribute's value, not just its count | Custom Objectives, Custom Attribution Configurations (API only) |

- [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_configure.htm&release=264.0.0&type=5). Examples: `Revenue` = `Sum` of `Product Order Engagement > Adjusted Total Product Order Amount`; `Add to Cart Count`; `Click Count`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_examples.htm&release=264.0.0&type=5)

### 1.8 Compound metrics
- Rate metrics: numerator metric, operator `Divide By`, denominator metric. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_compound_metrics_configure.htm&release=264.0.0&type=5) "This release supports using only count metrics with a divide by operator" (e.g., clicks per views, email opens per deliveries). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_compound_metrics_examples.htm&release=264.0.0&type=5)
- Prerequisite: "at least two single metrics configured for the engagement signal that you're creating the compound metric on"; the pair must logically form a ratio (recommender clicks / recommender views). Create: signal → `Related` → `Engagement Signal Compound Metrics` → `New` → name (API name auto-generated) → numerator → `Divide By` → denominator → save. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_compound_metrics_configure.htm&release=264.0.0&type=5)
- Implication (inference): both metrics sit on one signal, so a views→clicks CTR needs a signal whose rows include both actions (no action filter), with metrics that separate them; whether metric definitions support that split is UNVERIFIED.

### 1.9 Limits
| Item | Limit |
| --- | --- |
| Engagement signals per org / per data space | 100 / 100 |
| Filters per signal; related DMOs per signal | 10; 1 |
| Signals used for training per objective-based recommender | 25 |
| Metrics per org / per data space / per signal | 100 / 100 / 10 |
| Compound metrics per org / per data space | 100 / 100 |
| Referenced field levels for a signal in a data graph | 3 |
| Attribution models per org (active + inactive, all data spaces) / per data space | 20 / 10 |
| Stages per attribution configuration; signals per stage; metrics per configuration | 4; 1; 5 |

- [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5)

### 1.10 Where metric values surface
- Custom objectives, custom attribution configurations and experiments, per the aggregation table. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_es_metrics_configure.htm&release=264.0.0&type=5)
- Experiments: the primary metric decides the winner; results show `Lift`, `Credible Interval`, `Chance to beat control`, `Chance to beat all`; secondary metrics don't decide the winner. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_analytics_primary_metric_results.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_analytics_secondary_metric_results.htm&release=264.0.0&type=5)
- No standalone metrics dashboard is documented; values surface through attribution and experiment analytics (UNVERIFIED that no other view exists).

## 2. Attribution

### 2.1 Model semantics and attribution DMOs
- `First Touch`: of multiple qualifying engagements for a conversion, the first gets 100% of the value; `Last Touch`: the last gets 100%. The docs' example engagement is a "view or impression". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5)
- Four attribution DMOs: Personalization Point / Personalization Content × First Touch / Last Touch View-Based Attribution. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_dmos.htm&release=264.0.0&type=5)

| DMO | Object API name (developer ref) | Date field | Point field | Clicks field |
| --- | --- | --- | --- | --- |
| Point First Touch | `PersnlPointFirstTouchViewAttr__dlm` | `AttributionDate__c` | `RootPersonalizationPoint__c` | `AttributedClickCount__c` |
| Point Last Touch | `PersnlPointLastTouchViewAttr__dmo` (sic) | `AttributionDate__c` | `PersonalizationPoint__c` | `AttributedClicksCount__c` |
| Content First Touch | `PersnlContentFirstTouchViewAttr__dlm` | `AttributionDate__c` | `PersonalizationPoint__c` | `AttributedClickCount__c` |
| Content Last Touch | `PersnlContentLastTouchViewAttr__dlm` | `PersonalizationAttrDate__c` | `RootPersonalizationPoint__c` | `AttributedClickCount__c` |

- Sources: [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-view-attribution-dmo.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-click-attribution-dmo.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-content-view-attribution-dmo.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-content-click-attribution.html)
- Shared fields: primary key `PersonalizationAttrPk__c`; `PersonalizationDecision__c`, `Personalizer__c`, `DataSpace__c`, `UniqueProfileCount__c` ("Total number of unique Personalization profiles (visitors)"), `PersonalizationRequestCount__c`, `AttributedCartsCount__c`, `AttributedRevenue__c`, `AttributedOrdersPlaced__c`. `AttributedViewsCount__c` only on the two First Touch DMOs; content DMOs add `ContentObjectRecordId`. Same sources.
- Doc inconsistencies: the developer overview describes these DMOs as eligibility/view vs engagement/click based, and the Last Touch pages have `-click-attribution` URL slugs (legacy view/click model). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/data-model-object-reference.html) The Help deploy article names all four with `__dlm` plus `{dataspacePrefix}_{irSuffix}_` prefixes. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5) Check real names in Data Explorer before writing SQL.

### 2.2 Predefined attribution configurations
- Two predefined configurations are installed through Personalization setup; data is viewed from the `Attributions` tab. They need Product Browse Engagement, Shopping Cart Engagement and Product Order Engagement; if you don't use those objects the predefined setup is optional. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_settings.htm&release=264.0.0&type=5)
- Parameters: model types `First Touch` and `Last Touch`; `Attribution Window` = `7 days` ("the maximum allowed time between two engagements for a conversion to occur"; orders outside the window aren't counted). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_settings.htm&release=264.0.0&type=5)
- KPIs: Engagement `Impressions` ("Revenue is considered attributed if the individual has seen the content. Direct engagement with the content isn't required."), `Clicks`; Business Metrics `Add to Carts`, `Orders`, `Revenue`. The intro lists KPIs as "Views, Clicks, Add to carts, and Orders" (Views = Impressions; Revenue omitted). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_settings.htm&release=264.0.0&type=5)

### 2.3 Deploy predefined attribution data
- Setup → `Personalization Setup` → `Foundational Setup` tab → Personalization Attribution Intelligence Setup → `Select Data Space and IR Ruleset` → data space (must already have SP foundational data) → optional identity resolution ruleset → `Deploy`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Creates DLOs `{dataspacePrefix}_{irSuffix}_PersnlPointFirstTouchViewAttr`, `..._PersnlPointLastTouchViewAttr`, `..._PersnlContentFirstTouchViewAttr`, `..._PersnlContentLastTouchViewAttr`, the same names with `__dlm` as DMOs, models `{dataspacePrefix}_{irSuffix}_DefaultAttribution_FT` / `..._DefaultAttribution_LT`, one Salesforce CRM data stream per attribution DMO, full mappings, and no CIs (example CI SQL is separate). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Each default model "combine[s] and display[s] both the personalization point and content first touch and last touch DMO attribution data". Example CI SQL: `persnl_references_sample_calculated_insight_refs`. Same source.
- Naming: default data space adds no prefix; no ruleset adds no `{irSuffix}`; a ruleset with an empty suffix yields `e_s_`; a ruleset starting with a number in the default data space yields prefix `n_s_{irSuffix}`. Deployment checks whether the data space already has attribution data. Same source.

### 2.4 Custom attribution configuration (App Launcher → `Attributions` → `New`)
Permission `Personalization Intelligence User`. Purpose: a two- to four-stage funnel "from initial impression to conversion" built from your own signals and metrics.
1. Data space.
2. Identity resolution ruleset, or `No IR Ruleset` "For data model objects that don't require the use of an identity resolution ruleset, like the Individual object".
3. Name → `Next` (API-name behavior undocumented).
4. Model type `First Touch` or `Last Touch`; attribution window (options not listed in docs, see 2.6) → `Next`.
5. Funnel stages: "at least 2", "up to 4"; one engagement signal per stage; each signal needs an active Personalization Log relationship.
6. Stages 2–4: `Content Match`. Enabled: attribution only if the item in this stage is the same item engaged with in the previous stage. Disabled: any item counts, even if not engaged with before.
7. Move metrics from `Available Metrics` to `Selected Metrics` (max 5 per configuration, per limits page).
8. `Save Draft` (saved, not enabled; enable any time) or `Save & Enable`.
9. Create the two output DMOs, named differently: `Personalization Point Output DMO` (point-level data) and `Personalization Point Content Output DMO` (content-level data).
- Steps: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5); limits: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5)
- Ruleset vs `No IR Ruleset` counting is not defined in docs. Inference: with a ruleset, source Individuals linked to one unified profile likely count once; with `No IR Ruleset`, each source Individual counts, and each anonymous web `deviceId` is its own Individual (UNVERIFIED).

### 2.5 Enable, disable, delete
- Enable a draft: `Attributions` → open draft → `Enable` → create the two output DMOs → `Enable`. Permission `Personalization Intelligence User`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_enable_draft.htm&release=264.0.0&type=5)
- Status `Active` (enabled) or `Inactive` (disabled); row menu `Disable` / `Delete`. Deleting a predefined configuration removes it from the tab but keeps its objects and data; redeploying attribution intelligence recreates it without overwriting data. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_disable_delete.htm&release=264.0.0&type=5)
- Inactive models still count toward the 20-per-org limit. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5)

### 2.6 Windows and processing cadence
- Only documented window value: `7 days` (predefined). The custom wizard offers `24 Hrs`, `7 Days`, `30 Days` (Field-observed, undocumented).
- Processing cadence, latency and any "last run" indicator are not documented (UNVERIFIED). Treat attribution output as batch, not real time.

### 2.7 Analytics tab (Attribution Intelligence dashboard)
- Open: `Attributions` → open an **active** model → `Analytics` tab; covers all personalization points and associated content. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_view.htm&release=264.0.0&type=5)
- Section 1, global filters: `Personalization Point`, `Recommender`, timeframe; changing any changes every metric.
- Section 2, Funnel Stage Conversion: stage labels come from the model's signals; left (entrance) to right (exit); the entrance shows "the total number of individuals who have started the conversion journey", later stages show "the total number of conversions at each stage"; each rate is relative to the previous stage. Predefined: Views = total individuals, Clicks = clicks/views, Carts = carts/clicks, Orders = orders/carts.
- Sections 3 and 4: `Attribution by Decision` (default columns Personalization Point, Decision, Recommender) and `Attribution by Content` (adds Content ID); other columns are the model's stages.
- Dashboard sections: [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_attrib_intelligence_using.htm&release=264.0.0&type=5)
- Whether later stages count distinct individuals or events is not stated (UNVERIFIED); the docs imply individuals.
- Pattern (inference): for a no-code per-decision view/click table across all points, build a custom two-stage model with **unfiltered** view and click signals and read `Attribution by Decision`. Values follow attribution and individual semantics, not raw events; use SQL (§8) for event CTR.

## 3. Dependencies: CRM Analytics and permissions
- **Pipeline Intelligence requires CRM Analytics**, verbatim: "In the Personalization Pipeline Intelligence Dashboard Setup section, make sure that CRM Analytics is enabled." If not, `Enable` → `Enable CRM Analytics`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5)
- **Attribution Intelligence: no CRM Analytics dependency is documented, and none is excluded.** None of the SP attribution articles (overview, predefined, deploy, custom create, enable, disable/delete, view, dashboard, Tableau) mention CRM Analytics; their only permission is `Personalization Intelligence User`, and the dashboard opens from the `Attributions` record's `Analytics` tab. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_intelligence.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_view.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_attrib_intelligence_using.htm&release=264.0.0&type=5)
- Ambiguity: the analytics-types page says "The Salesforce Personalization Intelligence app provides two types of analytics — Personalization pipeline intelligence and Personalization attribution intelligence", grouping both under one app, yet the CRM Analytics prerequisite is stated only for the Pipeline dashboard. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_types.htm&release=264.0.0&type=5)
- Structural hint (not proof): the Pipeline dashboard is installed per data space from Personalization Setup, whereas attribution deployment creates DLOs, DMOs, streams and models, and the dashboard is the `Analytics` tab of an active model, with no dashboard install step. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5) CRM-Analytics-free alternatives: Tableau (§5) or Query Editor on the attribution DMOs (§6).
- Both standard SP permission sets include system permissions `Use CRM Analytics Templated Apps`, `Personalization Intelligence User`, `Attribution Model User`, `Access Personalization Platform`. That hints at CRM Analytics templated assets but does not establish a dependency for the `Analytics` tab (UNVERIFIED). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5)

| Task | Permission (verbatim) |
| --- | --- |
| Configure signals, metrics, compound metrics | `Engagement Signals` |
| Create custom attribution; enable a draft | `Personalization Intelligence User` |
| Install Pipeline Intelligence dashboard | `Personalization Intelligence User permission set` |
| View Pipeline Intelligence dashboard | `Personalization Intelligence User` (usage page says "license") |
| Create calculated insights | `Data Cloud Architect` |
| Data 360 reports (private / public folders) | `Create and Customize Reports` / `Report Builder (Lightning Experience)` |
| CRM Analytics Direct Data for Data 360 | `CRM Analytics Plus User` or `CRM Analytics Growth User` |

- Sources: signals [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_engagement_signals_configure.htm&release=264.0.0&type=5), pipeline install [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5), pipeline view [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_pipeline_intelligence_using.htm&release=264.0.0&type=5), CIs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5), reports [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_create_standard_reports.htm&release=264.0.0&type=5), CRM Analytics [src](https://help.salesforce.com/s/articleView?id=analytics.bi_direct_data_cdp_prerequisites.htm&release=264.0.0&type=5)

## 4. Pipeline Intelligence dashboard
- Purpose: operational metrics, "the number of decision requests, number of personalization points, number of personalization decisions, and number of unique individuals targeted". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_types.htm&release=264.0.0&type=5) Its metric list contains no view or click engagement (inference from the metric list, not a doc quote). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_pipeline_intelligence_using.htm&release=264.0.0&type=5)
- Prerequisites: data space contains CIs `Daily Personalization Requests` and `Daily Personalization Uniques` ("billable events within Data 360", including associated queries); one dashboard per data space; data space has SP foundational data; CRM Analytics enabled. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5) Foundational data installs both CIs, but they "must be manually scheduled". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_deploy_foundational_data.htm&release=264.0.0&type=5) Required API names: `DailyPersonalizationUniques__cio`, `DailyPersonalizationRequests__cio`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5)
- Install: Setup → `Personalization Setup` → `Foundational Setup` → enable CRM Analytics → Install the Personalization Pipeline Intelligence Dashboard → `Select Data Space` → `Install`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5)
- Open: App Launcher → `Personalization` → `Personalization Intelligence` tab → data space. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_intelligence_app_open.htm&release=264.0.0&type=5)
- Content: global `Date Range` filter; `Total Personalization Requests`, `Total Personalization Points` (filter by personalization type or point); `Avg. Number of Unique Individuals / Day`; All Data table `Personalization Point`, `Personalization Point ID`, `Personalization Decision`, `Personalization Decision ID`, `Personalization Requests`. Copy errors on that page: `Avg. Number of Unique Individuals / Day` is described as "unique personalization points", and `Personalization Decision` as the point's name. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_pipeline_intelligence_using.htm&release=264.0.0&type=5)

## 5. Tableau
- Use Tableau to "view and analyze attribution metrics for predefined attribution DMOs" through the built-in Salesforce Data Cloud Connector, "in near real time". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_intelligence_using_tableau.htm&release=264.0.0&type=5) Any personalization analytics DMO can be visualized with Tableau or a JDBC client. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics.htm&release=264.0.0&type=5)
- Connector minimums: Tableau Desktop 2023.2+, Tableau Server 2023.3, Tableau Cloud since Oct 2023; the old Customer Data Platform connector was deprecated in Oct 2023. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_set_up_tableau_connected_app.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_dc_for_tableau.htm&release=264.0.0&type=5)

## 6. Intelligence SQL samples (verbatim)
- Run from any JDBC-compatible client connected to Data 360 (Query Editor, Tableau, DBeaver). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_intelligence_sql_queries.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/guide/int-apps-data-cloud.html)

Get Information About Personalization Pipeline Requests. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_pipeline_request_results.htm&release=264.0.0&type=5)
```sql
SELECT
substr(to_iso8601(RequestDateTime__c),1,19) as DateTime,
PersonalizationRequestId__c as PersonalizationRequestId,
IndividualId__c as IndividualId,
PersonalizationPointId__c as PersonalizationPoint,
ResponseTimeMillisecond__c as ResponseTime,
TargetObjectLabelText__c as TargetObjectLabel,
TargetObjectRecordId__c as TargetObjectRecordId
FROM
PersonalizationLog__dlm
WHERE
PersonalizationRequestId__c ='fcf77347-44c2-4e84-952f-10391a5a9df9'
```

Aggregate the Requests Served to Individuals per Day. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_aggregate_requests_individuals_per_day.htm&release=264.0.0&type=5)
```sql
SELECT
DATE_TRUNC('day',RequestDateTime__c) as Day,
COUNT(DISTINCT PersonalizationRequestId__c) as NumRequests,
COUNT(DISTINCT IndividualId__c) as UniqueIndividuals
FROM
PersonalizationLog__dlm
GROUP BY
1
ORDER BY
1
```

View Personalization Pipeline Metrics by Date. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_view_pipeline_metrics_by_date.htm&release=264.0.0&type=5)
```sql
SELECT
CAST(PersonalizationLog__dlm.RequestStartDateTime__c AS DATE) as RequestDate,PersonalizationPoint__dlm.Name__c as PersonalizationPoint,
PersonalizationDecision__dlm.Name__c as PersonalizationDecision,
approx_distinct(PersonalizationLog__dlm.PersonalizationId__c) as NumRequests,approx_distinct(PersonalizationLog__dlm.IndividualId__c) as UniqueIndividuals, SUM(PersonalizationLog__dlm.ResponseTimeMillis__c/COALESCE(NULLIF(PersonalizationLog__dlm.NumContentItems__c,0),1)) as TotalResponseTime,
SUM(PersonalizationLog__dlm.NumContentItems__c/COALESCE(NULLIF(PersonalizationLog__dlm.NumContentItems__c,0),1)) as NumContentItems
FROM PersonalizationLog__dlm
 LEFT JOIN PersonalizationPoint__dlm
 ON(PersonalizationLog__dlm.PersonalizationPointId__c =
 PersonalizationPoint__dlm.Id__c)
 LEFT JOIN PersonalizationDecision__dlm
 ON(PersonalizationLog__dlm.PersonalizationDecisionId__c =
 PersonalizationDecision__dlm.Id__c)

GROUP BY 1,2,3
ORDER BY 1 DESC
```

Query Personalization Attribution by Personalization Point. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_personalization_attribution_by_personalization_point.htm&release=264.0.0&type=5)
```sql
SELECT
AttributionDate__c,
PersonalizationDecision__c,
PersonalizationPoint__c,
Personalizer__c,
SUM(PersonalizationRequestCount__c) as personalization_requests,
SUM (UniqueProfileCount__c) as unique_individuals,
SUM (AttributedViewsCount__c) as views,
SUM (AttributedClicksCount__c) as clicks,
SUM (AttributedCartsCount__c) as carts,
SUM (AttributedOrdersCount__c) as orders,
SUM(AttributedOrdersCount__c) / NULLIF(SUM(AttributedViewsCount__c), 0)*100 as orderConversionRate,
SUM (AttributedRevenue__c) as revenue
FROM scm_PersonalizationPointViewAttribution__dlm
WHERE  AttributionDate__c >= date('2024-01-01') AND AttributionDate__c <= date('2024-04-01')
GROUP BY 1,2,3,4
ORDER BY AttributionDate__c ASC;
```

Inconsistencies (adapt before use):
- The pipeline-metrics page promises results "over the selected date range" and "personalized responses provided to each individual", but its SQL has no date filter and no per-individual metric.
- Two Personalization Log field generations: `RequestDateTime__c` / `ResponseTimeMillisecond__c` (Data 360 standard model) vs `RequestStartDateTime__c` / `ResponseTimeMillis__c` / `NumContentItems__c` (SP developer reference). The pipeline-metrics sample counts `PersonalizationId__c` as `NumRequests`, the per-day sample counts `PersonalizationRequestId__c`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html)
- The attribution sample uses a legacy DMO name (`scm_` = data space prefix, `PersonalizationPointViewAttribution`) and `AttributedOrdersCount__c`, which no current attribution DMO page lists (`AttributedOrdersPlaced__c`). Point it at `{prefix}_{irSuffix}_PersnlPoint...ViewAttr__dlm`.
- Samples omit `ssot__`; default data space SP docs use `ssot__` names (`ssot__PersonalizationLog__dlm.ssot__RequestDateTime__c`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_dmo_name_field_reqs.htm&release=264.0.0&type=5)
- `approx_distinct`, `to_iso8601`, `date()` are Trino-style; confirm the dialect in your client (UNVERIFIED).
- Summing `UniqueProfileCount__c` across dates over-counts people active on several days (inference).

## 7. Data 360 reports and dashboards
- Create a report on a CI, semantic model or DMO: record page `Create Report`; list view Action menu `Create Report`; or Reports tab → `Create Report` → category `Data 360` → CI or DMO as record type → `Start Report`. Editions: Developer, Enterprise, Performance, Unlimited. [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_create_standard_reports.htm&release=264.0.0&type=5)
- Reports can cover single or multiple related DMOs or CIs; custom report types can be built on DMOs; users with Data 360 access can use Data 360 reports by default. [src](https://help.salesforce.com/s/articleView?id=data.datacloud_reports_dashboards_overview.htm&release=264.0.0&type=5)
- Limits: 2,000 rows in run mode (subtotals count); export 50,000 rows / 100 MB (`.csv`, `.xls`, `.xlsx`); 5 row-level formulas per report. [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_limits.htm&release=264.0.0&type=5)
- Not available (selected): custom report types on CIs; stacked summaries; changing grouped-date granularity; standard filters, cross filters, filter by scope; historical trending; formula functions such as `ISNULL`, `NOT`, `OR`, `PARENTGROUPVAL`, `PREGROUPVAL`, `PRIORVALUE`; date/time functions in formulas. Salesforce Identity license users have no access; in a companion org the `Data 360` category appears only after at least one of its DMOs is mapped. [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_limits.htm&release=264.0.0&type=5)
- Contradiction on joined reports: the limits page lists "Joined reports" under "Report Features Not Available" [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_limits.htm&release=264.0.0&type=5); separate articles document joined Data 360 reports for DMOs only ("Calculated Insight Objects and Semantic Data Models aren't supported"), Lightning only, each block sharing at least one common field with the base block [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_joined_reports_considerations.htm&release=264.0.0&type=5). Either way, CI reports can't be joined.
- Semantic data models that contain a calculated insight can't be reported on. [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_limits.htm&release=264.0.0&type=5)
- CI reports: measures are aggregates, dimensions are groupings; a report needs at least one aggregate measure with a non-text data type and at least one dimension; non-aggregatable measures require all CI dimensions in the report and show no subtotals. Output is a summary report without details, grand totals or row count; no row-level or summary formulas; you can't re-aggregate (sum, min, max, average) a measure; no `Details Only` export; with more than 5 dimensions at least one aggregatable measure is required, and with mixed measures a report holds up to five dimensions (remove one to add another). [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_calculated_insights_limits.htm&release=264.0.0&type=5)
- Trending over time: reports on CI history snapshots (Beta) need history tracking on the CI and the setting `Enable reporting on CIO History in Data Cloud Reports (Beta)`; only aggregatable measures, summed by `Snapshot Date`. [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_dashboards_cio_history_reporting.htm&release=264.0.0&type=5)
- CI charts and dashboards: tabular, metric and gauge components are unavailable. `Funnel` and `Donut` are unavailable when the report has 2 dimensions, the chart has 1, and all measures are non-aggregatable. With 3+ dimensions and only non-aggregatable measures, no chart can be added. Same source.
- Consequence: compute CTR inside the CI or outside reports (Query Editor, Tableau, CRM Analytics); a CI report can't derive it with a formula.
- CRM Analytics alternative: CI record page → `Explore in Analytics` → chart gallery `Funnel`; requires CRM Analytics Direct Data permissions (section 3). [src](https://help.salesforce.com/s/articleView?id=analytics.bi_direct_data_cdp_one_clickexplore.htm&release=264.0.0&type=5)

## 8. Calculated insights for personalization reporting

### 8.1 Authoring rules
- Create: Data Cloud → `Calculated Insights` tab → `New` → data space → `Calculated Insight` → `Use SQL Authoring` → `Next` → name (API name auto-filled) → SQL (max 131,021 characters) → `Check Syntax` → `Activate` → schedule, start date/time → `Enable`. DMO names are case-sensitive. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5)
- Structure: `SELECT <attributes>, <aggregation(measures)> FROM <dmo> [JOIN ...] [WHERE ...] GROUP BY <dimensions>`. A measure is a field inside an aggregation function (at least one required); every other `SELECT` field is a dimension and must be in `GROUP BY`. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5)
- Clause rules: no aggregate within an aggregate; no top-level `DISTINCT` or `ORDER BY`; `/* */` comments allowed; a dimension alias can't equal the source field name; nested subqueries allowed in `WHERE` / `JOIN`. `WHERE` can't hold aggregates or reference aliases; `GROUP BY` can't hold measure aliases or aggregates and can reference a dimension alias but not inside an expression; `CASE` or `RANK` wrapping aggregates yields non-aggregatable measures. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5)
- Functions: aggregatable `SUM`, `COUNT` ("COUNT(*) isn't supported"), `AVG`, `MIN`, `MAX`, `MEAN`, `FIRST`, `LAST`. Non-aggregatable `APPROX_COUNT_DISTINCT` (documented unique-count function), `PERCENTILE`, `STDDEV`, all datetime functions (`DATE_ADD`, `DATE_SUB`, `CURRENT_DATE`, `NOW`, `DATE_TRUNC`, ...), analytical functions, `CASE`, `IFNULL`, `NULLIF`, `LIKE`. Streaming and real-time insights support only `SUM` and `COUNT`. "Aggregatable" means the output can be rolled up across fewer dimensions when queried in segments or activations; `RANK`, `NTILE`, `CASE` are the page's examples of non-aggregatable functions. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5)
- Operators: `* + - /`; `TRY_CONVERT_CURRENCY`; `=`, `!=`/`<>`, `<`, `<=`, `>`, `>=`; `and`; `LIKE` (`%`); `RLIKE`; `Is_True`, `Is_False`, `Has_Boolean_Value`, `Has_No_Boolean_Value`. `OR` / `IN` are not listed, so the samples below avoid them. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_operators.htm&release=264.0.0&type=5)
- Naming: default data space → prefix DMOs and fields with `ssot__`; other data spaces → `{prefix}__`. The page's own non-default sample shows `{prefix}_PersonalizationLog__dlm.RequestDateTime__c` (single underscore, unprefixed field), which is inconsistent. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_dmo_name_field_reqs.htm&release=264.0.0&type=5)
- CI objects end in `__cio`. Every documented measure and dimension alias ends in `__c`; no explicit rule found (UNVERIFIED as a hard rule). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_uniques_ci_ref.htm&release=264.0.0&type=5)

### 8.2 Scheduling and limits
- Schedule every 1, 6, 12 or 24 hours, or `Not Scheduled`. A run still in progress causes the next one to be skipped; 15-minute start times round to the next 30 minutes; the user's time zone applies. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_schedule_a_calculated_insight_in_data_cloud.htm&release=264.0.0&type=5)
- Limits: 10 dimensions, 50 measures, 300 CIs per tenant (active, inactive and draft), 4 nested CIs, 2-hour execution (longer runs may be terminated), 30 manual runs per CI per 24 h, 20 real-time insights. A CI doesn't run if source data, mappings and configuration are unchanged. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5) Validate results in Data Explorer (object type `Calculated Insights`). [src](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5)

### 8.3 Source Individual to Unified Individual
- Unified link objects "are required for creating calculated insights for unified profiles". [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_terms.htm&release=264.0.0&type=5)
- Unified Link Individual = `IndividualIdentityLink__dlm`: `SourceRecordId__c` (Individual Id), `UnifiedRecordId__c` (Unified Individual Id). A ruleset ID is appended to object names, e.g., `UnifiedLinkIndividualTest__dlm` / `UnifiedssotIndividualTest__dlm` for ruleset `Test`. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5)
- Documented join, verbatim: `JOIN IndividualIdentityLink__dlm ON ssot__SalesOrder__dlm.ssot__SoldToCustomerId__c = IndividualIdentityLink__dlm.SourceRecordId__c JOIN UnifiedIndividual__dlm ON IndividualIdentityLink__dlm.UnifiedRecordId__c = UnifiedIndividual__dlm.ssot__Id__c`. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5)

### 8.4 Field reference for SP web engagement reporting (default data space)
- `ssot__WebsiteEngagement__dlm`: `ssot__Id__c` (PK), `ssot__IndividualId__c`, `ssot__EngagementChannelActionId__c`, `ssot__EngagementDateTm__c`, `ssot__WebpageType__c`, `ssot__PersonalizationContentId__c`, `ssot__PersonalizationId__c`, `ssot__PersonalizationRequestId__c`, `ssot__PageURL__c`. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html)
- `ssot__PersonalizationLog__dlm`: `ssot__RequestDateTime__c`, `ssot__IndividualId__c`, `ssot__PersonalizationPointId__c`, `ssot__PersonalizationDecisionId__c`, `ssot__PersonalizerId__c`, `ssot__PersonalizationType__c`, `ssot__PersonalizationRequestId__c`, `ssot__PersonalizationId__c`, `ssot__ResponseTimeMillisecond__c`, `ssot__ContentItemsQuantity__c`. Names via `ssot__PersonalizationPoint__dlm.ssot__Name__c`, `ssot__PersonalizationDecision__dlm.ssot__Name__c`, `ssot__Personalizer__dlm.ssot__Name__c`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5)
- Join `ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c` follows the documented FK (1.6) and `ssot__` naming rule. The same `PersonalizationContentId` → Personalization Log FK exists on Website Item, Shopping Wishlist and Shopping Wishlist Item Engagement. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-websiteitemengagementdmo-dmo.html)
- The newer standard-model page lists Personalization Log as `std__PersonalizationLogDmo__dlm` (254+, category Unassigned), a third naming generation next to `ssot__` and unprefixed names. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html)
- `ssot__WebpageType__c` holds the sitemap page type name (Field-observed, undocumented).

### 8.5 SP-provided CI SQL (verbatim)
Daily Personalization Uniques (`DailyPersonalizationUniques__cio`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_uniques_ci_ref.htm&release=264.0.0&type=5)
```sql
SELECT
   DATE_ADD(ssot__PersonalizationLog__dlm.ssot__RequestDateTime__c,0) as RequestDate__c,
   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__IndividualId__c) as NumUniqueIndividuals__c,    APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__PersonalizationRequestId__c) as NumRequests__c,
   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__PersonalizationId__c) as NumPersonalizationRequests__c,
   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__ContentObjectAPIName__c) as NumUniqueRecordTypes__c,
   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__ContentObjectRecordId__c) as NumUniqueRecords__c
FROM
   ssot__PersonalizationLog__dlm
GROUP BY
   RequestDate__c
```
Daily Personalization Requests (`DailyPersonalizationRequests__cio`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5)
```sql
SELECT
   DATE_ADD(ssot__PersonalizationLog__dlm.ssot__RequestDateTime__c, 0) as RequestDate__c,
   ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c as PersonalizationPointId__c,
   ssot__PersonalizationPoint__dlm.ssot__Name__c as PersonalizationPointName__c,
   ssot__PersonalizationLog__dlm.ssot__PersonalizationType__c as PersonalizationType__c,
   ssot__PersonalizationLog__dlm.ssot__PersonalizationDecisionId__c as PersonalizationDecisionId__c,
   ssot__PersonalizationDecision__dlm.ssot__Name__c as PersonalizationDecisionName__c,
   ssot__PersonalizationLog__dlm.ssot__PersonalizerId__c as PersonalizerId__c,
   ssot__Personalizer__dlm.ssot__Name__c as PersonalizerName__c,
   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__PersonalizationRequestId__c) as NumRequests__c,   APPROX_COUNT_DISTINCT(ssot__PersonalizationLog__dlm.ssot__PersonalizationId__c) as NumPersonalizationRequests__c,
   SUM(ssot__PersonalizationLog__dlm.ssot__ResponseTimeMillisecond__c / IFNULL(NULLIF(ssot__PersonalizationLog__dlm.ssot__ContentItemsQuantity__c, 0), 1)) as TotalResponseTimeMilliseconds__c,
   SUM(ssot__PersonalizationLog__dlm.ssot__ContentItemsQuantity__c / IFNULL(NULLIF(ssot__PersonalizationLog__dlm.ssot__ContentItemsQuantity__c, 0), 1)) as NumContentItems__c,
   SUM(ssot__PersonalizationLog__dlm.ssot__ContentLengthBytesNumber__c) as TotalContentLength__c
FROM
   ssot__PersonalizationLog__dlm
LEFT JOIN
   ssot__PersonalizationPoint__dlm ON (ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c = ssot__PersonalizationPoint__dlm.ssot__Id__c)
LEFT JOIN
   ssot__PersonalizationDecision__dlm ON (ssot__PersonalizationLog__dlm.ssot__PersonalizationDecisionId__c = ssot__PersonalizationDecision__dlm.ssot__Id__c)
LEFT JOIN
   ssot__Personalizer__dlm ON (ssot__PersonalizationLog__dlm.ssot__PersonalizerId__c = ssot__Personalizer__dlm.ssot__Id__c)
GROUP BY
   RequestDate__c,
   PersonalizationPointId__c,
   PersonalizationPointName__c,
   PersonalizationType__c,
   PersonalizationDecisionId__c,
   PersonalizationDecisionName__c,
   PersonalizerId__c,
   PersonalizerName__c
```
- These CIs count served requests from Personalization Log, not rendered views or clicks.

### 8.6 Constructed CI SQL for views, clicks and uniques (not executed)
- Built only from documented field names, functions and clause rules (8.1–8.4). The `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` pattern appears in a documented CI template. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/cdp_crm_dk2__FieldService.html) Runtime behavior is UNVERIFIED.

CI A: daily views and clicks per point and decision. `CASE` is listed as non-aggregatable, so whether `SUM(CASE ...)` measures roll up across fewer dimensions is UNVERIFIED; plan reports with all three dimensions until checked in the CI's object home.
```sql
SELECT
  DATE_ADD(ssot__WebsiteEngagement__dlm.ssot__EngagementDateTm__c, 0) AS engagement_date__c,
  ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c AS point_id__c,
  ssot__PersonalizationLog__dlm.ssot__PersonalizationDecisionId__c AS decision_id__c,
  SUM(CASE WHEN ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END) AS views__c,
  SUM(CASE WHEN ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END) AS clicks__c
FROM ssot__WebsiteEngagement__dlm
JOIN ssot__PersonalizationLog__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c
WHERE ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c LIKE 'personalization-%'
GROUP BY engagement_date__c, point_id__c, decision_id__c
```
- CTR option: add `SUM(<click CASE>) / NULLIF(SUM(<view CASE>), 0) AS ctr__c`. Whether a ratio of aggregates is aggregatable is undocumented (UNVERIFIED); if not, reports need all three dimensions.

CI B: unique viewers and clickers (non-aggregatable; report with all dimensions; daily uniques are not additive across days).
```sql
SELECT
  DATE_ADD(ssot__WebsiteEngagement__dlm.ssot__EngagementDateTm__c, 0) AS engagement_date__c,
  ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c AS point_id__c,
  ssot__PersonalizationLog__dlm.ssot__PersonalizationDecisionId__c AS decision_id__c,
  ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c AS engagement_action__c,
  APPROX_COUNT_DISTINCT(ssot__WebsiteEngagement__dlm.ssot__IndividualId__c) AS unique_individuals__c
FROM ssot__WebsiteEngagement__dlm
JOIN ssot__PersonalizationLog__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c
WHERE ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c LIKE 'personalization-%'
GROUP BY engagement_date__c, point_id__c, decision_id__c, engagement_action__c
```

CI C: unified-profile uniques over a rolling 30 days (use `UnifiedLinkIndividual<RulesetId>__dlm` if the ruleset has an ID).
```sql
SELECT
  ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c AS point_id__c,
  ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c AS engagement_action__c,
  APPROX_COUNT_DISTINCT(IndividualIdentityLink__dlm.UnifiedRecordId__c) AS unique_unified_individuals__c
FROM ssot__WebsiteEngagement__dlm
JOIN ssot__PersonalizationLog__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c
JOIN IndividualIdentityLink__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__IndividualId__c = IndividualIdentityLink__dlm.SourceRecordId__c
WHERE ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c LIKE 'personalization-%'
  and ssot__WebsiteEngagement__dlm.ssot__EngagementDateTm__c >= DATE_SUB(CURRENT_DATE(), 30)
GROUP BY point_id__c, engagement_action__c
```

### 8.7 Query Editor ad-hoc funnel (exact distinct counts, names, CTR)
- Query Editor runs Data 360 SQL on DLOs, DMOs, CIOs and data graphs inside a workspace; it needs data space access to the object. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor_create_queries.htm&release=264.0.0&type=5) ANSI SQL below; not executed (UNVERIFIED).
```sql
SELECT
  pp.ssot__Name__c AS personalization_point,
  pd.ssot__Name__c AS decision,
  SUM(CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END) AS views,
  SUM(CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END) AS clicks,
  COUNT(DISTINCT CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-view' THEN we.ssot__IndividualId__c END) AS unique_viewers,
  COUNT(DISTINCT CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-click' THEN we.ssot__IndividualId__c END) AS unique_clickers,
  100.0 * SUM(CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END)
    / NULLIF(SUM(CASE WHEN we.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END), 0) AS ctr_pct
FROM ssot__WebsiteEngagement__dlm we
JOIN ssot__PersonalizationLog__dlm pl ON we.ssot__PersonalizationContentId__c = pl.ssot__Id__c
LEFT JOIN ssot__PersonalizationPoint__dlm pp ON pl.ssot__PersonalizationPointId__c = pp.ssot__Id__c
LEFT JOIN ssot__PersonalizationDecision__dlm pd ON pl.ssot__PersonalizationDecisionId__c = pd.ssot__Id__c
WHERE we.ssot__EngagementChannelActionId__c IN ('personalization-view', 'personalization-click')
  AND we.ssot__EngagementDateTm__c >= CAST('<START_DATE>' AS DATE)
GROUP BY 1, 2
ORDER BY views DESC
```

## 9. Decision guide
| Question | Use | What you get | Watch out for |
| --- | --- | --- | --- |
| View → click funnel for one placement, as people and stage conversion % | Custom attribution, 2 stages | `Analytics` tab funnel, Attribution by Decision / Content | batch; cadence undocumented; 20 models/org incl. inactive |
| Revenue/orders attributable to recommendations | Predefined attribution, or custom with `SUM` metric | attributed carts, orders, revenue | predefined needs Product Browse, Shopping Cart, Product Order Engagement |
| Which variant wins | Experiment with a primary signal metric | Lift, credible interval, chance to beat control | only the primary metric decides |
| Daily views, clicks, CTR, uniques by point/decision on a dashboard | CI (8.6) + Data 360 report/dashboard | summary reports, charts | no formulas in CI reports; uniques need all dimensions; no tabular/metric/gauge components |
| Exact numbers, validation, join debugging | Query Editor (8.7) | ad-hoc grid | not scheduled |
| Pipeline health (requests, points, uniques/day) | Pipeline Intelligence or pipeline SQL | CRM Analytics dashboard | needs CRM Analytics + 2 scheduled CIs; no view/click data |
| Rich BI on attribution DMOs | Tableau via Salesforce Data Cloud Connector | workbooks | documented for predefined attribution DMOs |
| Row grain: who saw which decision when, per unified person | Batch data transform to a DLO ([field-guide-data.md](field-guide-data.md) §4) | one row per view or click with point, decision and unified ID | CIs need an aggregate measure; pattern is field practice |

Recipe (generic): view → click funnel for one placement when several points share Website Engagement (for another channel, use its engagement DMO and action values, §1.6).
1. Signal `<VIEW_SIGNAL_NAME>`: DMO Website Engagement; `User Identifier` `Website Engagement > Individual`; `Timestamp Identifier` `Engagement Date Time`; `Event Identifier` `Website Engagement Id`; filter `Engagement Channel Action` `Is Equal To` `personalization-view`, plus related `Personalization Log > Personalization Point Id` `Is Equal To` `<POINT_ID>`, `All Conditions Are Met`. Leave the flows checkbox cleared. The auto metric is `<SIGNAL_METRIC_NAME>` (`Count_<SignalApiName>`).
2. Signal `<CLICK_SIGNAL_NAME>`: same, with `personalization-click`.
3. Attribution: data space, ruleset or `No IR Ruleset`, `First Touch` or `Last Touch`, window, stage 1 = view signal, stage 2 = click signal (optionally `Content Match`), metrics, `Save & Enable`, name the two output DMOs.
4. Read the `Analytics` tab with the `Personalization Point` filter; pair with CI A/B for event counts and CTR.
- Each step is documented (2–4 stages, Personalization Log relationship, related-DMO filters: 1.3–1.6, 2.4); the combined recipe is not a doc example (Field-observed, undocumented).
- Why filter by point (inference): without it, a click on point B inside the window could be credited to an earlier view of point A. `Content Match` may do the same job; its behavior for Dynamic Content (formerly Manual Content) is UNVERIFIED.
- Web Individuals may have no linked master profile, so `Website Engagement > Individual` is the practical `User Identifier` (Field-observed, undocumented); doc examples use `<Engagement DMO> > Individual` too.

## MCP confusion traps
- Paths: `mc_pers_*` = MCP; `mc_persnl_*` / `persnl_*` = SP. `developer/personalization` = MCP; SP developer docs = `developer/einstein-personalization`.
- MCP Help pages carry `products: Marketing|Salesforce Personalization` metadata with breadcrumb "Marketing Cloud Personalization". Filter by breadcrumb or path, not `products`. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_glossary_defs_a_f.htm&release=264.0.0&type=5)
- Attribution windows differ. MCP: "four attribution windows: 30 minutes (default), 1 hour, 24 hours, and 1 week". [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_glossary_defs_a_f.htm&release=264.0.0&type=5) SP predefined uses `7 days`; SP custom offers `24 Hrs` / `7 Days` / `30 Days` (Field-observed, undocumented).
- Reporting differs. MCP Campaign Statistics split "attribution statistics" from "activity statistics", use a `Results Filter`, and require the Impressed Visit (IV) and goal inside the time frame. SP has no campaign statistics, goals or IV; it uses engagement signals, attribution configurations and the `Analytics` tab. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_campaign_statistics_results_filter_att_stats.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_campaign_statistics_attribution_time_frame.htm&release=264.0.0&type=5)
- CRM Analytics differs. MCP integrates CRM Analytics with MCP's Data Warehouse [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_salesforce_crma.htm&release=264.0.0&type=5); unrelated to the SP Pipeline Intelligence prerequisite.
- Other "attribution" products that are not SP: Marketing Intelligence "Funnel-Based Attribution" (Data Management → `Touch-Based Attribution`, also First/Last Touch) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_mc_mi_data_management.htm&release=262.0.0&type=5); Account Engagement `Einstein Attribution` (Data-Driven Model, B2B Marketing Analytics Multi-Touch Attribution dashboard) [src](https://help.salesforce.com/s/articleView?id=mktg.pardot_einstein_attribution_setup.htm&release=264.0.0&type=5).
- The "Salesforce Personalization" release-notes page covers both SP and MCP; check each note's product. [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=264.0.0&type=5)

## Gaps and uncertainties
- Undocumented, field-observed: custom window options `24 Hrs` / `7 Days` / `30 Days`; auto metric API name `Count_<SignalApiName>`; `ssot__WebpageType__c` value source; the two-stage point-filtered funnel recipe; web Individuals lacking a master profile.
- Not documented at all: attribution processing cadence and latency; custom attribution API name; custom output DMO schema (assumed to match the predefined attribution DMOs); ruleset vs `No IR Ruleset` counting; whether funnel stages after the entrance count individuals or events; `Content Match` for Dynamic Content (formerly Manual Content, non-catalog); where compound metric values are displayed.
- CRM Analytics for the Attribution `Analytics` tab: neither stated nor excluded (section 3).
- CI SQL: aggregatability of `SUM(CASE ...)` and ratio measures; hard `__c` alias rule; `OR` / `IN` in `WHERE`; SQL dialect of the Intelligence samples.
- Doc-vs-doc inconsistencies: attribution DMO names and fields (`__dmo` suffix, `AttributedClickCount__c` vs `AttributedClicksCount__c`, `AttributedOrdersCount__c` vs `AttributedOrdersPlaced__c`); Personalization Log field generations; non-default data space prefix format; predefined KPI list (intro vs table); Pipeline dashboard metric descriptions; pipeline-by-date SQL vs its description; joined-report availability.
- Only 264.0.0 versions of these SP pages were available; no release comparison.

## Sources
All inline links are the sources. Core SP pages (release 264.0.0, breadcrumb "Salesforce Help|Docs|Salesforce Personalization"):
- Signals: `persnl_engagement_signals`, `persnl_engagement_signals_configure`, `persnl_es_examples_prod_view_engmt`, `persnl_es_examples_prod_click_engmt`, `persnl_es_metrics_configure`, `persnl_es_metrics_examples`, `persnl_es_compound_metrics_configure`, `persnl_es_compound_metrics_examples`, `persnl_basics_limits`.
- Attribution: `persnl_analytics_attribution_intelligence`, `persnl_analytics_attribution_settings`, `persnl_setup_pers_attribution_intel_data_deploy`, `persnl_analytics_attrib_config_custom_create`, `persnl_analytics_attrib_config_enable_draft`, `persnl_analytics_attrib_config_disable_delete`, `persnl_analytics_attrib_config_view`, `persnl_analytics_pers_attrib_intelligence_using`, `persnl_analytics_attrib_intelligence_using_tableau`, `persnl_basics_dmos`.
- Pipeline and SQL: `persnl_analytics_types`, `persnl_setup_install_pers_pipeline_dashboard`, `persnl_analytics_pers_intelligence_app_open`, `persnl_analytics_pers_pipeline_intelligence_using`, `persnl_setup_deploy_foundational_data`, `persnl_intelligence_sql_queries` (+4 query pages), `persnl_references_daily_personalization_*_ci_ref`, `persnl_setup_insights_dmo_name_field_reqs`, `persnl_setup_assign_standard_permission_sets_to_users`.
- SP developer (`developer/einstein-personalization`): track-personalization-engagement, integrate-salesforce-interactions-sdk, data-model-object-reference, personalization-log-dmo, four attribution DMO pages.
- Data 360 / Reports / CRM Analytics: DMO mapping guide (Website Engagement, Personalization Log, and the engagement DMOs listed in §1.6); `data.c360_a_*` calculated insight, identity resolution, Query Editor, Tableau pages; `analytics.rd_dc_reports_*`; `analytics.bi_direct_data_cdp_*`.
- Release notes: `rn_persnl_added_es_filter_operators` (260), `rn_personalization` (264).
- MCP and other products (warnings only): `mc_pers_glossary_defs_a_f`, `mc_pers_campaign_statistics_*`, `mc_pers_salesforce_crma`, `pardot_einstein_attribution_setup`, `rn_mc_mi_data_management`.

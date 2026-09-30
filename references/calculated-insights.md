# Insights and Personalization: Calculated, Streaming and Real-Time Insights with Data Graphs

## Scope
- How Data 360 insights (calculated, streaming, real-time) feed Salesforce Personalization (SP): choosing a type, authoring rules, adding an insight to a data graph, using it in targeting rules, merge fields and recommenders, freshness, limits, cost and troubleshooting.
- Baseline: Data 360 and SP Help at release 264.0.0 (262 release notes for history). Reporting insights (views, clicks, CTR) are in [measurement-and-attribution.md](measurement-and-attribution.md) §8; insight SQL for reports is in [sql-cookbook.md](sql-cookbook.md); graph mechanics are in [decisioning.md](decisioning.md) §1 and [data-360-foundations.md](data-360-foundations.md).
- Labels: `(UNVERIFIED)` = not confirmed in docs; `(inference)` = reasoned from the cited docs. No statement here is field-observed; §8 lists what to test in the target org.

## 1. Which insight type

| | Calculated insight (CI) | Streaming insight | Real-time insight |
|---|---|---|---|
| Processing | Scheduled runs over large history (SP calls it "near real time") | Continuous micro-batches, windows as short as 1 minute | Per event, results in milliseconds |
| Source | Mapped DMOs and other insights (nesting, §2) | Engagement DMOs from streaming connectors (Web SDK, Mobile SDK, Marketing Cloud Personalization, Ingestion API, Kinesis, Kafka, CRM Streaming); joins only to Engagement and unified Individual objects | A real-time data graph |
| Authoring | SQL or Visual Builder | SQL or Visual Builder | Visual Builder only |
| Aggregates | See §2 | `SUM`, `COUNT` | `Sum`, `Count` on the 264 create page; `Min`, `Max` added by a 262 release note (next list) |
| Segments and activation | Yes | No | Yes, as part of a real-time graph |
| Typical SP use | Item rankings, lifetime or periodic profile metrics | Orchestration and data actions | In-session thresholds: cart value, recent clicks, frequency caps |

[src](https://help.salesforce.com/s/articleView?id=data.c360_a_insights.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_real_time_insight.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_streaming_insight.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5)

- **SP's own guidance:** a CI is "near real time and best used when creating metrics associated with items or products, not for real-time Personalization applications". Use a real-time insight for events that need real-time consideration [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_using.htm&release=264.0.0&type=5).
- **Real-time aggregate functions: the docs disagree.** The 264 create page says "Only Sum and Count are supported for real-time insights" [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_real_time_insight.htm&release=264.0.0&type=5). A 262 release note says the Visual Builder Aggregate node gained `Min` and `Max` ("available June 2026"), plus the Case and Transform nodes [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_cdp_2026_summer_realtime_insights_advanced_functions.htm&release=262.0.0&type=5). Read the function list in the builder before designing around either (`UNVERIFIED` for which an org offers).
- **Streaming insights can go in a graph.** SP says "You can use any Data 360 insight type with Salesforce Personalization" and add it to the data graphs it uses [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_using.htm&release=264.0.0&type=5). The data graph page says calculated and streaming insights can be included "if they're based on a DMO that's also included in the data graph" [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_graph_data_structures.htm&release=264.0.0&type=5). How a decision evaluates a streaming insight, and how fresh its value is, isn't documented (`UNVERIFIED`; §8). A streaming insight's last-run status always reads `Processing` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_streaming_insight.htm&release=264.0.0&type=5), it shows no data until events keep arriving [src](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5), and it isn't available in segmentation or activation.
- **Don't build an insight to expose a value that already exists.** If the source DMO already carries the field (a tier, a flag, a points balance), map it and select it as a direct attribute. A CI adds a run schedule, a numeric-measure shape and the 5-measure cap (§4). Build an insight only for aggregation (inference).

## 2. Authoring a calculated insight

- **Shape:** `SELECT <dimensions>, <aggregate measures> FROM <DMO> [JOIN …] [WHERE …] GROUP BY <dimensions>`. At least one measure is required; every non-aggregated field in `SELECT` is a dimension and must be in `GROUP BY` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5).
- **Clause rules:** DMO names are case-sensitive; no aggregate inside an aggregate; no top-level `DISTINCT` or `ORDER BY`; a dimension alias can't equal the source field name (`Id__c as Id__c` fails); `WHERE` can't hold aggregates or aliases; use `CASE WHEN SUM(x) > 100 THEN …` to compare aggregates; currency fields need `TRY_CONVERT_CURRENCY`; for an empty date use null, not `''` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5). Aggregatable versus non-aggregatable functions are in [sql-cookbook.md](sql-cookbook.md).
- **Names depend on the data space.** In the default data space prefix every DMO and field with `ssot__`; in another data space use `{prefix}__` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_dmo_name_field_reqs.htm&release=264.0.0&type=5). A CI copied between data spaces probably fails on names first (inference).
- **Relative windows:** `NOW`, `SECOND_ADD` and `SECOND_SUB` build rolling windows, from seconds to years (365+ days) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_insight_relative_time_metrics.htm&release=264.0.0&type=5); the statement limit is 131,021 characters [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_create_ci_for_targeting.htm&release=264.0.0&type=5).
- **Nesting ("metrics on metrics"):** a CI can read another CI by naming its `…__cio` object in `FROM` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_metrics_on_metrics.htm&release=264.0.0&type=5); the limit is 4 nested calculated insights [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5). Use it to split scoring into steps.
- **Key on the unified profile.** For a Unified Individual–rooted graph, unified link objects are required [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_terms.htm&release=264.0.0&type=5). Documented insights join `IndividualIdentityLink__dlm.UnifiedRecordId__c` to `UnifiedIndividual__dlm.ssot__Id__c` and the source record through `SourceRecordId__c` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ci_outlier_unified_profiles.htm&release=264.0.0&type=5). Constructed from that pattern (not executed). The cited example leaves the identity DMOs unprefixed while the default-data-space rule above prefixes standard DMOs, so confirm every API name on the Data Model tab (inference):

```sql
SELECT
  UnifiedIndividual__dlm.ssot__Id__c AS unified_id__c,
  COUNT(<ENGAGEMENT_DMO>.ssot__Id__c) AS event_count__c
FROM UnifiedIndividual__dlm
JOIN IndividualIdentityLink__dlm
  ON IndividualIdentityLink__dlm.UnifiedRecordId__c = UnifiedIndividual__dlm.ssot__Id__c
JOIN <ENGAGEMENT_DMO>
  ON <ENGAGEMENT_DMO>.ssot__IndividualId__c = IndividualIdentityLink__dlm.SourceRecordId__c
GROUP BY unified_id__c
```

- **Schedule:** every 1, 6, 12 or 24 hours, or `Not Scheduled` and run it manually (30 manual runs per CI per 24 hours, per the limits page below). If a run isn't finished when the next one is due, the next run is skipped; a 15-minute start time rounds up to the next 30 minutes; the user's time zone sets the schedule [src](https://help.salesforce.com/s/articleView?id=data.c360_a_schedule_a_calculated_insight_in_data_cloud.htm&release=264.0.0&type=5). A CI doesn't run when source data, mappings and configuration are unchanged, and it can be terminated after 2 hours [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
- **Validate before use:** Data Explorer → Object `Calculated Insights` → the insight. Wait until the run finishes first [src](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5).
- **Design the schema before the first run; editing is narrow.** For measures you can't change the API name, data type or rollup behavior, and can add only aggregatable measures to an aggregatable insight. For dimensions you can't change the name or data type, and can add one only if it's a key qualifier dimension. You can't remove measures or dimensions [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_calculated_insight_in_customer_data_platform.htm&release=264.0.0&type=5). To change a shape, create a new insight. A graph that already includes the old one accepts additions only (§4), so plan the swap.

## 3. Authoring a real-time insight

- **Prerequisites:** a real-time data graph, and every dimension and measure you plan to use already added to that graph; `Data Cloud Architect` permission [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_real_time_insight.htm&release=264.0.0&type=5).
- **Builder steps:** Calculated Insights tab → `New` → data space → `Real-Time Insights` → `Use Visual Builder` → pick the real-time graph → optional relative time filter (`DateTime` → `Relative DateTime` → `Interval`) → `Aggregate` with a metric function (`Sum` or `Count` on the 264 page; `Min` and `Max` per §1) and dimensions → `Save and Enable`. Toggle `Show related fields` to use a related DMO as a dimension.
- **The graph's primary key is added automatically** as a dimension and can't be removed; it counts toward the 15-field cap.
- **Evaluated at graph query time.** With no events in the window the metric is 0. Real-time graph clients must process the insight data client-side to get the true value at query time [src](https://help.salesforce.com/s/articleView?id=data.c360_a_insight_relative_time_metrics.htm&release=264.0.0&type=5). Whether SP applies the window exactly when it decides is undocumented (`UNVERIFIED`; test it, §8).
- **Windows can be approximate.** To save storage, recent events sit in small buckets and older ones in larger buckets, so a count can be approximate rather than exact; `window_start__c` and `window_end__c` dimensions are created automatically [src](https://help.salesforce.com/s/articleView?id=data.c360_a_insight_relative_time_metrics.htm&release=264.0.0&type=5). Don't set a threshold that needs an exact count near the boundary (inference).
- **Privacy lag:** real-time insights skip data subject rights checks per event. A companion batch CI applies them at the next real-time graph refresh, so an individual with a fresh request can still appear until then [src](https://help.salesforce.com/s/articleView?id=data.c360_a_insights_data_subject_rights.htm&release=264.0.0&type=5).
- **Frequency-cap pattern:** [decisioning.md](decisioning.md) §8.1 and [implementation-playbook.md](implementation-playbook.md) §12.

## 4. Adding an insight to a data graph

1. Create and run the CI so its object exists. It must be based on a DMO that is also in the graph, and that DMO's primary key must be a CI dimension.
2. In the graph editor, click `+` next to the root DMO and pick the CIO (marked with the data graph icon), then select its dimensions and measures on the `Fields` tab. Permission: `Data Cloud Architect`.
3. **Root only.** A CIO can't be a child node under another object [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_calculated_insights_to_a_data_graph.htm&release=264.0.0&type=5). Every documented example keys the CI on the root's primary key (a Unified Individual id for a profile graph, a Goods Product id for an item graph); a CI keyed on another id is the first thing to check when it isn't offered (inference).
4. **Shape in the record:** the graph JSON carries the CI as an array with one element per dimension combination, each repeating the root key [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_calculated_insights_to_a_data_graph.htm&release=264.0.0&type=5). A CI whose only dimension is the root key yields one row per person; extra dimensions multiply rows in every record (inference: they also grow the record toward the 200 KB guidance in [decisioning.md](decisioning.md) §1.6).
5. **Caps:** 5 measures per CI in a graph (50 in the CI itself), 25 objects per graph, and recommender filters consider the top 100 CI values ([decisioning.md](decisioning.md) §1.6, §7.6).
6. **Edits:** in a published graph you can add fields but not remove them, so add only what rules, merge fields and filters read ([decisioning.md](decisioning.md) §1.6).
7. **Freshness is two clocks (inference):** the CI's own run, then the graph's refresh. A standard graph refreshes on its schedule (every 30 minutes, 1 hour, 4 hours, daily, weekly, monthly, or streaming) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_refresh_a_data_graph.htm&release=264.0.0&type=5). A CI in a real-time graph probably follows that batch path rather than per-event updates, since the CI itself only runs on its schedule (inference); session extension can also delay lakehouse updates [src](https://help.salesforce.com/s/articleView?id=data.c360_a_sess_ext_data_graphs.htm&release=264.0.0&type=5). Budget the sum of both schedules when you promise "updated within N hours".

## 5. Using an insight in Personalization

| Where | How | Notes |
|---|---|---|
| Targeting rule | Resource `Calculated Insights`: CIs defined at the graph root | Create the insight and add it to the point's graph first; rules see everything reachable from that graph; up to 50 conditions per decision [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_targeting_rules_create.htm&release=264.0.0&type=5). Operator labels aren't published; confirm in the wizard ([decisioning.md](decisioning.md) §6.3) |
| Merge field | CI on the profile graph, with sort criteria | Multi-value attributes need a sort criterion to pick which value returns (262) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_decisions_with_rltd_attrib_and_calc_insgt.htm&release=262.0.0&type=5) |
| Rule-based recommender | CI on the **item** graph; choose the CI, `Sort Measure`, `Sort Order` | Top sellers and co-bought below; the `Maximize Revenue` objective needs the Product Sales (Top Sellers) insight configured first ([decisioning.md](decisioning.md) §2) |
| Recommender filter | Item graph CI, or a `Profile Data Graph` CI | Filter details and limits: [decisioning.md](decisioning.md) §7.6 |
| Predictive model input | Dimensionless numeric CI | [mobile-and-channels.md](mobile-and-channels.md) |
| Segments | CI joins the Profile-type segmented table with its primary key as a dimension | [sql-cookbook.md](sql-cookbook.md) |

- **Which graph:** point-level targeting reads the **profile** graph; recommenders sort on CIs in the **item** graph. SP's insight setup pages call the item graph "near real-time" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_product_sales_standard_ci_ref.htm&release=264.0.0&type=5). "Using Data Graphs With Personalization" says the profile graph "must be a real-time data graph", but point-level articles support standard profile graphs, so treat that wording as stale ([decisioning.md](decisioning.md) §1.2) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5).
- **Multi-row CIs in rules:** which row a targeting condition evaluates when the CI has several rows per person isn't documented (`UNVERIFIED`). Prefer a CI keyed only on the person for eligibility rules, and use extra dimensions only where sort criteria choose the value (inference).
- **Top Sellers (SP-provided, verbatim):** rows per product with the units sold. Add it to the item graph and sort by `TotalSoldUnits__c` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_product_sales_standard_ci_ref.htm&release=264.0.0&type=5).

```sql
SELECT
   ssot__GoodsProduct__dlm.ssot__Id__c as ProductId__c, SUM(ssot__SalesOrderProductEngagement__dlm.ssot__OrderedQuantity__c) as TotalSoldUnits__c from ssot__SalesOrderProductEngagement__dlm
JOIN
   ssot__GoodsProduct__dlm
ON
   ssot__SalesOrderProductEngagement__dlm.ssot__ProductId__c = ssot__GoodsProduct__dlm.ssot__Id__c group by ssot__GoodsProduct__dlm.ssot__Id__c
```

- **Co-bought:** SP provides a longer insight with two product dimensions (`p1__c`, `p2__c`) and a count measure (`countP2__c`). In the recommender choose the count as the `Sort Measure` and filter with `Decision Context` on the product being viewed [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_co_bought_standard_ci_ref.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_recommender_filters_configure_multiple_dimension_example.htm&release=264.0.0&type=5).
- **Real-time insights:** Data 360 stores them in the real-time graph. The frequency-cap pattern in [decisioning.md](decisioning.md) §8.1 selects one under the `Calculated Insights` resource with a "below N" condition (inference; operator labels are unpublished).

## 6. Choosing an approach

| Need | Use | Why |
|---|---|---|
| Field already on a DMO (tier, flag, points) | Direct attribute, not an insight | No schedule, no measure cap |
| Person-level aggregate that changes daily (lifetime spend, orders in 90 days, engagement rank) | Batch CI on the profile graph | Accepts staleness up to CI run plus graph refresh |
| Threshold on this session's behavior (cart value, clicks in 10 minutes, capped views) | Real-time insight | Query-time evaluation; `Sum` and `Count` on the 264 page, `Min` and `Max` per §1 |
| Top sellers, most viewed, co-bought, brand or category rankings | Batch CI on the item graph | SP's documented rule-based recommender input |
| Consent categories for targeting | A profile attribute on the `identity` event, not an insight | [field-guide-web.md](field-guide-web.md) §1.3; a CI's measures are aggregates and it runs on a schedule, so it lags the browser (inference) |
| Views, clicks, CTR reporting | CI plus a Data 360 report or Query Editor | [measurement-and-attribution.md](measurement-and-attribution.md) §8 |
| Affinity scores | Calculated affinity (creates one CI per field) | [decisioning.md](decisioning.md) §8 |

## 7. Limits, cost and governance

| Item | Value |
|---|---|
| Dimensions per CI / measures per CI | 10 / 50 |
| CIs per tenant | 300, counting active, inactive and draft |
| Existing insights one new insight can use ("nested") | 4 |
| Execution time | 2 hours |
| Manual runs per CI per 24 hours | 30 |
| Real-time insights / fields (incl. graph key) / related DMOs | 20 / 15 / 10 |

- Real-time insight related DMOs must have a many-to-one relationship, directly, with an engagement DMO in the real-time graph; the 10 cap covers all active real-time insights across data spaces [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
- Each real-time insight has a companion batch CI. Whether it counts against the 300 isn't stated (`UNVERIFIED`); check before planning near the cap.
- **Cost:** a batch CI bills on the records in all underlying objects each run and nothing when the objects haven't changed. Real-time insights bill under the real-time pipeline or sub-second real-time events; streaming insights under streaming pipeline usage. To lower cost: run less often, set an end date, and turn off history tracking [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_insights.htm&release=264.0.0&type=5).
- **History tracking** creates a `…History` insight with `history_capture_ts`; use it for trend analysis; using it in targeting is untested [src](https://help.salesforce.com/s/articleView?id=data.c360_a_insight_apply_history_tracking.htm&release=264.0.0&type=5).
- **Permissions:** `Data Cloud Architect` to create real-time insights and to add insights to graphs.

## 8. Test before you promise (not yet field-verified)

Build a small CI keyed on the person, add it to a scratch copy of the profile graph, then confirm each point in the org:

1. **The CI appears as an array in the graph record.** Read the record with the in-org Flow lookup ([troubleshooting.md](troubleshooting.md)) and count the rows.
2. **Real freshness.** Change source data, note the CI run, the graph refresh and the moment the value changes in the record. Record both clocks.
3. **Multi-row evaluation.** With two rows per person, check which row a targeting condition matches.
4. **Streaming insight in a graph.** The docs say it can be added (§1). Add one, then check the record shape, how often the value changes and whether a targeting rule can read it.
5. **Real-time window at decision time.** Trigger the event, then compare the decision with the record.

## 9. Troubleshooting

| Symptom | Check in order |
|---|---|
| CI isn't offered when adding to the graph | Run finished? Based on a DMO in the graph? Root's primary key is a dimension? Same data space? Adding at the root, not under a child? Permission `Data Cloud Architect`? |
| CI isn't offered in the targeting rule | On the point's graph? Graph saved and refreshed after adding? Point built on that graph? |
| Value is stale or empty | CI status and last run; skipped run (previous still running); source unchanged so no run; graph refresh time; unified key (dimension is the source-level id, not the unified id) |
| CI SQL fails | Alias equals field name; DMO name casing or missing `ssot__` or `{prefix}__`; missing measure; dimension not in `GROUP BY`; aggregate in `WHERE`; currency without `TRY_CONVERT_CURRENCY` |
| Merge field returns the wrong value | No sort criteria on a multi-value CI; extra dimensions producing several rows |
| Real-time insight won't save | Field not on the real-time graph yet; a function the builder doesn't offer (§1); over 15 fields or 20 insights |
| Numbers differ from a report | Non-aggregatable measure queried on fewer dimensions; approximate real-time buckets; window not exact ([measurement-and-attribution.md](measurement-and-attribution.md) §8) |

Sources: [Data 360 insights](https://help.salesforce.com/s/articleView?id=data.c360_a_insights.htm&release=264.0.0&type=5) · [Insights with SP](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_using.htm&release=264.0.0&type=5) · [Add CIs to a data graph](https://help.salesforce.com/s/articleView?id=data.c360_a_add_calculated_insights_to_a_data_graph.htm&release=264.0.0&type=5) · [Real-time insights](https://help.salesforce.com/s/articleView?id=data.c360_a_create_real_time_insight.htm&release=264.0.0&type=5) · [Limits](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5)

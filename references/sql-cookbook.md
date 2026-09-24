# Data 360 SQL Cookbook for Personalization

## Scope
- SQL for Salesforce Personalization (SP) reporting and debugging on Data 360: views and clicks per point, decision breakdowns, daily trends, unified-individual counts, calculated insights (CIs), SP's own attribution sample, decision latency, orphan engagement events, and identity checks.
- Run ad-hoc SQL in Query Editor, which queries DLOs, DMOs, calculated insight objects (CIOs), and data graphs; you need data space access to each object, and creating queries needs the `Data Cloud Activation Specialist` permission set [src](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor_create_queries.htm&release=264.0.0&type=5). Tableau and DBeaver are the other integrated apps [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/guide/int-apps-data-cloud.html). Save recurring metrics as CIs, which need `Data Cloud Architect` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5).
- Status tags: `field-verified (Query Editor)` ran successfully in a live SP org; `doc-derived (untested)` uses only documented object, field, and function names but hasn't been run; `doc sample (verbatim)` is copied from SP Help.
- Every query assumes the default data space (`ssot__` names) and the Website Engagement destination used by Dynamic Content (formerly Manual Content), except Q4b (Product Browse Engagement); see "Joins and values" to switch channels. Placeholders: `<POINT_ID>`, `<PAGE_TYPE>`, `<RULESET_ID>`, `<START_DATE>`, `<END_DATE>`, `<CI_API_NAME>`. Q4b also uses `<PRODUCT_BROWSE_ENGAGEMENT_DMO>`, `<ACTION_FIELD>`, `<PERSONALIZATION_CONTENT_ID_FIELD>` and `<DATETIME_FIELD>`.

## Rules

### Query Editor SQL vs calculated insight SQL
| Topic | Query Editor, Query API, JDBC | Calculated insight SQL |
| --- | --- | --- |
| Dialect | Data 360 SQL, shared with the Query API and Tableau Hyper API [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/data-cloud-sql-context.html) | `SELECT dims, agg(measures) FROM dmo [JOIN] [WHERE] GROUP BY dims` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5) |
| `COUNT(*)` | Works (Q1) | "COUNT(*) isn't supported"; count a key field [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5) |
| Unique counts | `COUNT(DISTINCT x)` (Q1) or `approx_count_distinct(x [, error])` [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/approx-count-distinct.html); multi-column `COUNT(DISTINCT a, b)` isn't supported in Query API V3 [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/query-api-migration.html) | `APPROX_COUNT_DISTINCT` (non-aggregatable); no top-level `DISTINCT` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5) |
| `ORDER BY`, `LIMIT` | Allowed; `LIMIT` and `OFFSET` are supported [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/select.html) | No top-level `ORDER BY` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5) |
| Dates | `date_trunc('day', ts)`, `CURRENT_DATE`, `DATE_ADD(unit, value, date)`, `ts - INTERVAL '7 days'` [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/datetime-func.html); `DATE_SUB` isn't supported in V3 [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/query-api-migration.html) | `DATE_ADD(date, n)`, `DATE_SUB`, `DATE_TRUNC`, `CURRENT_DATE`, `NOW` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5) |
| Filters | Standard SQL, including `IN` and `OR` | Documented operators: `=`, `!=`/`<>`, `<`, `<=`, `>`, `>=`, `and`, `LIKE`, `RLIKE` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_operators.htm&release=264.0.0&type=5); the function list adds `NOTLIKE`, `NOTRLIKE`, `BETWEEN`, `REGEXP` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5). `IN` and `OR` aren't listed |
| Subqueries | Standard SQL | Nested subqueries allowed in `WHERE` or `JOIN` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5) |
| Aliases | Any | A dimension alias can't equal the source field name [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5); every documented CI alias ends in `__c` (no explicit rule found, so follow the convention) |

- Don't paste SQL between the two engines unchanged: the CI function list and Data 360 SQL differ, as the `DATE_ADD` signatures and `DATE_SUB` support show.

### Calculated insight rules that cause most failures
- Every CI needs at least one measure, and every non-aggregated `SELECT` field is a dimension that must appear in `GROUP BY` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5).
- No aggregate inside an aggregate; `WHERE` can't contain aggregates or aliases; `GROUP BY` may reference dimension aliases (not inside expressions) but never measure aliases; currency fields require `TRY_CONVERT_CURRENCY` in `SELECT` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5).
- Rollups: aggregatable measures (`SUM`, `COUNT`, `AVG`, `MIN`, `MAX`) can be queried on any subset of dimensions. Non-aggregatable ones (`APPROX_COUNT_DISTINCT`, `CASE` wrapping an aggregate, `RANK`, `NTILE`) need all dimensions whenever they're queried [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5); reports show them only after you add every dimension [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_calculated_insights_limits.htm&release=264.0.0&type=5).
- An aggregatable insight accepts only aggregatable measures [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_calculated_insight_in_customer_data_platform.htm&release=264.0.0&type=5), so keep counts and uniques in separate CIs (Q6a, Q6b). `SUM(CASE WHEN … THEN 1 ELSE 0 END)` is a `CASE` inside `SUM`, not an aggregate inside `CASE`, so it should stay aggregatable (inference).
- DMO names are case-sensitive; copy them from the Object API Name column on the Data Model tab [src](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5).
- Limits: 10 dimensions, 50 measures, 300 CIs per tenant, 4 nested CIs, a 2-hour runtime, and 30 manual runs per 24 hours [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5); SQL up to 131,021 characters [src](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5).
- Schedules: every 1, 6, 12, or 24 hours, or `Not Scheduled`. A run still in progress makes the next one skip, start times round to 30-minute increments, and the user's time zone applies [src](https://help.salesforce.com/s/articleView?id=data.c360_a_schedule_a_calculated_insight_in_data_cloud.htm&release=264.0.0&type=5). A CI doesn't run when source data, mappings, and configuration are unchanged [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
- After creation you can't change a measure's API name, data type, or rollup behavior, remove measures or dimensions, or add a dimension unless it's a key qualifier dimension [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_calculated_insight_in_customer_data_platform.htm&release=264.0.0&type=5). Get the design right before you activate.
- Streaming and real-time insights support only `SUM` and `COUNT` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5).
- Segments: the Segment On DMO must be Profile type, the CI must join the segmented table and include its primary key as a dimension, and a non-aggregatable measure is hidden in the segment builder if the CI has a date dimension [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_in_segments.htm&release=264.0.0&type=5). Validate a CI in Data Explorer before using it in a segment [src](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5).

### Names: data spaces and the two documented naming sets
- Default data space: prefix DMO names and fields with `ssot__`; other data spaces: `{prefix}__`. The same page's non-default sample writes `{prefix}_PersonalizationLog__dlm.RequestDateTime__c` (one underscore, unprefixed field), so confirm real names in Data Explorer [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_dmo_name_field_reqs.htm&release=264.0.0&type=5).
- Set 1, `ssot__` (legacy DMOs): `ssot__PersonalizationLog__dlm`, `ssot__PersonalizationPoint__dlm`, `ssot__PersonalizationDecision__dlm`, `ssot__Personalizer__dlm`, `ssot__WebsiteEngagement__dlm`, `ssot__PartyIdentification__dlm`. SP's own CI definitions use this set [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5), and every query below is written against it. The SP developer guide shows the log without a namespace (`PersonalizationLog__dlm`) and with other field names (`RequestStartDateTime__c`, `ResponseTimeMillis__c`) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html).
- Set 2, `std__` (standard DMOs, "Available in 254 and later"): `std__PersonalizationLogDmo__dlm`, `std__PersonalizationPointDmo__dlm`, `std__PersonalizationDecisionDmo__dlm`, `std__PersonalizerDmo__dlm`, `std__WebsiteEngagementDmo__dlm`. Personalization Log fields include `std__RequestDateTime__c`, `std__ResponseTimeMillisecond__c` and `std__ContentItemsQuantity__c` [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html). Website Engagement's `std__` fields include `std__Id__c`, `std__EngagementChannelActionId__c`, `std__EngagementDateTm__c`, `std__PersonalizationContentId__c` and `std__WebpageType__c`, not those request, response or item-count fields [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-websiteengagementdmo-dmo.html).
- Which set an org has isn't documented; check the Data Model tab. Porting isn't purely mechanical because casing drifts between pages: `ssot__ContentObjectAPIName__c` (SP CI) vs `std__ContentObjectApiname__c` (standard DMO), and `ssot__IdentificationNumber__c` (identity resolution troubleshooting) vs `ssot__Identificationnumber__c` (Party Identification DMO) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_uniques_ci_ref.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ir_errors.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-party-identification-dmo.html).
- If an unquoted identifier doesn't bind, double-quote it (`"ssot__Id__c"`): the Semantic Layer docs say Data 360 identifiers are case-sensitive and unquoted ones are case-folded [src](https://developer.salesforce.com/docs/data/semantic-layer/guide/query-api-in-depth-logical-views.html). (UNVERIFIED for Query Editor, where Q1 and Q2 ran unquoted.)

### Joins and values used below
- Website Engagement → Personalization Log is a documented many-to-one relationship, and the log's `Id` must store the Personalization Content Id [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html). Join on `w.ssot__PersonalizationContentId__c = p.ssot__Id__c` (field-verified). Website Engagement has no point field of its own.
- Log → point, decision, personalizer: `ssot__PersonalizationPointId__c`, `ssot__PersonalizationDecisionId__c`, `ssot__PersonalizerId__c` equal each object's `ssot__Id__c`; display names are in `ssot__Name__c` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5).
- `ssot__EngagementChannelActionId__c` holds `personalization-view` / `personalization-click` for the Website Engagement destination (field-verified). Recommendation experiences using Product Engagement land in Product Browse Engagement as `catalog-object-view-start` / `catalog-object-click`, and custom destinations can rename interactions [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html).
- On web events, `ssot__IndividualId__c` is the source Individual keyed by the device ID, not a person (the web mapping sends `deviceId` → Individual ID [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html)); use Q5 for people.
- Other channels: substitute `<ENGAGEMENT_DMO>` (for example `ssot__ProductBrowseEngagement__dlm`, or the `std__…Dmo__dlm` / `{prefix}__` form your org exposes) and `<VIEW_ACTION>` / `<CLICK_ACTION>` (for example `catalog-object-view-start` / `catalog-object-click`), keeping the join `<ENGAGEMENT_DMO>.…PersonalizationContentId__c = <PERSONALIZATION_LOG_DMO>.…Id__c`. The FK is documented on the DMOs listed in measurement-and-attribution.md §1.6, for example Product Browse Engagement [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-productbrowseengagementdmo-dmo.html). Field-verified results come from one org; re-verify names in the target org's Data Model tab.
- Take point IDs from the log (Q2). Setup-UI URL IDs (`0Wl…`) don't match log IDs (`9pp…`) (Field-observed, undocumented).

## Queries

### Q1. Views vs clicks for one point — `field-verified (Query Editor)`
Purpose: events and unique source individuals per action for one personalization point.
```sql
SELECT w.ssot__EngagementChannelActionId__c AS action,
       COUNT(*) AS events,
       COUNT(DISTINCT w.ssot__IndividualId__c) AS unique_individuals
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
WHERE w.ssot__EngagementChannelActionId__c IN ('personalization-view', 'personalization-click')
  AND p.ssot__PersonalizationPointId__c = '<POINT_ID>'
GROUP BY w.ssot__EngagementChannelActionId__c
```
- Unique individuals are per action row; don't add them across rows. Q6 is the CI version.

### Q2. Point IDs present in the log for a page type — `field-verified (Query Editor)`
Purpose: find the real point IDs to use in Q1, engagement signal filters, and attribution.
```sql
SELECT p.ssot__PersonalizationPointId__c AS point_id,
       COUNT(*) AS events
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
WHERE w.ssot__WebpageType__c = '<PAGE_TYPE>'
GROUP BY p.ssot__PersonalizationPointId__c
```
- `ssot__WebpageType__c` is documented [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html); that it holds the sitemap page type name is Field-observed, undocumented.
- Variant with point names and a page type inventory, `doc-derived (untested)`; a renamed page type shows up here as two names:
```sql
SELECT w.ssot__WebpageType__c AS page_type,
       p.ssot__PersonalizationPointId__c AS point_id,
       pp.ssot__Name__c AS point_name,
       COUNT(*) AS events
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
LEFT JOIN ssot__PersonalizationPoint__dlm pp
  ON p.ssot__PersonalizationPointId__c = pp.ssot__Id__c
GROUP BY 1, 2, 3
ORDER BY events DESC
```

### Q3. Breakdown by decision — `doc-derived (untested)`
Purpose: which decision each viewer received, and how each performed. `ssot__PersonalizationDecisionId__c` on the log and `ssot__PersonalizationDecision__dlm.ssot__Name__c` come from SP's Daily Personalization Requests CI [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5).
```sql
SELECT p.ssot__PersonalizationDecisionId__c AS decision_id,
       d.ssot__Name__c AS decision_name,
       SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END) AS views,
       SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END) AS clicks,
       COUNT(DISTINCT w.ssot__IndividualId__c) AS unique_individuals
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
LEFT JOIN ssot__PersonalizationDecision__dlm d
  ON p.ssot__PersonalizationDecisionId__c = d.ssot__Id__c
WHERE p.ssot__PersonalizationPointId__c = '<POINT_ID>'
  AND w.ssot__EngagementChannelActionId__c IN ('personalization-view', 'personalization-click')
GROUP BY p.ssot__PersonalizationDecisionId__c, d.ssot__Name__c
ORDER BY views DESC
```
- A visitor whose profile changes can receive different decisions over time, so per-decision uniques don't sum to Q1's total.

### Q4. Daily trend of views, clicks, and CTR — `doc-derived (untested)`
Purpose: spot drops after a release, a sitemap change, or a consent change.
```sql
SELECT date_trunc('day', w.ssot__EngagementDateTm__c) AS day,
       SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END) AS views,
       SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END) AS clicks,
       100.0 * SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-click' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN w.ssot__EngagementChannelActionId__c = 'personalization-view' THEN 1 ELSE 0 END), 0) AS ctr_pct
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
WHERE p.ssot__PersonalizationPointId__c = '<POINT_ID>'
  AND w.ssot__EngagementDateTm__c >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1
```
- `date_trunc` on a `timestamp with time zone` truncates in the current time zone by default [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/datetime-func.html), and the event `dateTime` comes from the visitor's clock, which can be skewed [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html).
- This is event CTR. Attribution funnels count individuals per stage, so their conversion rates differ by design [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_attrib_intelligence_using.htm&release=264.0.0&type=5).

### Q4b. Views and clicks per point and decision for Recommendations points — `doc-derived (untested)`
Purpose: the Product Engagement destination (`eventType` `catalog`, `catalog-object-view-start` / `catalog-object-click`, recommended DMO Product Browse Engagement; payload carries `personalizationId` and `personalizationContentId`) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html). Field names vary by mapping; confirm them in the Data Model tab.
```sql
SELECT pl.ssot__PersonalizationPointId__c AS point_id,
       pl.ssot__PersonalizationDecisionId__c AS decision_id,
       SUM(CASE WHEN pbe.<ACTION_FIELD> = 'catalog-object-view-start' THEN 1 ELSE 0 END) AS views,
       SUM(CASE WHEN pbe.<ACTION_FIELD> = 'catalog-object-click' THEN 1 ELSE 0 END) AS clicks
FROM <PRODUCT_BROWSE_ENGAGEMENT_DMO> pbe
JOIN ssot__PersonalizationLog__dlm pl ON pbe.<PERSONALIZATION_CONTENT_ID_FIELD> = pl.ssot__Id__c
WHERE pbe.<DATETIME_FIELD> >= CAST('<START_DATE>' AS DATE)
GROUP BY 1, 2
```
- Combine with a Website Engagement query (Q3) through `UNION ALL` for a mixed Dynamic Content + Recommendations report.

### Q5. Unified individuals for an identity resolution ruleset — `doc-derived (untested)`
Purpose: count people instead of devices.
```sql
SELECT w.ssot__EngagementChannelActionId__c AS action,
       COUNT(DISTINCT w.ssot__IndividualId__c) AS source_individuals,
       COUNT(DISTINCT l.UnifiedRecordId__c) AS unified_individuals,
       COUNT(DISTINCT COALESCE(l.UnifiedRecordId__c, w.ssot__IndividualId__c)) AS people_estimate
FROM ssot__WebsiteEngagement__dlm w
JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
LEFT JOIN UnifiedLinkIndividual<RULESET_ID>__dlm l
  ON w.ssot__IndividualId__c = l.SourceRecordId__c
WHERE p.ssot__PersonalizationPointId__c = '<POINT_ID>'
  AND w.ssot__EngagementChannelActionId__c IN ('personalization-view', 'personalization-click')
GROUP BY w.ssot__EngagementChannelActionId__c
```
- Finding the link DMO: a ruleset without a ruleset ID produces `IndividualIdentityLink__dlm`; with a ruleset ID, the ID is appended to the names, for example `UnifiedLinkIndividualTest__dlm` and `UnifiedssotIndividualTest__dlm` for ruleset `Test`. Link fields are `SourceRecordId__c` (Individual Id) and `UnifiedRecordId__c` (Unified Individual Id) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5).
- The ruleset ID is optional, up to four characters, and can't be changed; the creation wizard tells you to note the DMO names it generates [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5). Otherwise open the Identity Resolutions tab for the ruleset ID, or search "Unified Link Individual" on the Data Model tab.
- The documented CI join pattern is Source → `IndividualIdentityLink__dlm.SourceRecordId__c`, then `UnifiedRecordId__c` → `UnifiedIndividual__dlm.ssot__Id__c` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5).
- `people_estimate` counts unlinked devices as one person each (inference); individuals appear in the link DMO only after the ruleset processes them (inference).

### Q6. Calculated insight versions of Q1 — `doc-derived (untested)`
Purpose: schedule Q1 as reusable metrics for reports and dashboards. Q6a holds aggregatable counts; Q6b holds non-aggregatable uniques.
```sql
/* Q6a: events per point, action, and day (aggregatable) */
SELECT
  ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c AS point_id__c,
  ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c AS engagement_action__c,
  DATE_ADD(ssot__WebsiteEngagement__dlm.ssot__EngagementDateTm__c, 0) AS engagement_date__c,
  COUNT(ssot__WebsiteEngagement__dlm.ssot__Id__c) AS events__c
FROM ssot__WebsiteEngagement__dlm
JOIN ssot__PersonalizationLog__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c
WHERE ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c LIKE 'personalization-%'
GROUP BY point_id__c, engagement_action__c, engagement_date__c
```
```sql
/* Q6b: unique individuals per point, action, and day (non-aggregatable) */
SELECT
  ssot__PersonalizationLog__dlm.ssot__PersonalizationPointId__c AS point_id__c,
  ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c AS engagement_action__c,
  DATE_ADD(ssot__WebsiteEngagement__dlm.ssot__EngagementDateTm__c, 0) AS engagement_date__c,
  APPROX_COUNT_DISTINCT(ssot__WebsiteEngagement__dlm.ssot__IndividualId__c) AS unique_individuals__c
FROM ssot__WebsiteEngagement__dlm
JOIN ssot__PersonalizationLog__dlm
  ON ssot__WebsiteEngagement__dlm.ssot__PersonalizationContentId__c = ssot__PersonalizationLog__dlm.ssot__Id__c
WHERE ssot__WebsiteEngagement__dlm.ssot__EngagementChannelActionId__c LIKE 'personalization-%'
GROUP BY point_id__c, engagement_action__c, engagement_date__c
```
- `COUNT(*)` becomes `COUNT` of the Website Engagement primary key `ssot__Id__c` [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html). `COUNT(DISTINCT …)` becomes `APPROX_COUNT_DISTINCT`, a HyperLogLog++ estimate [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5).
- `IN (...)` becomes `LIKE 'personalization-%'`, a documented operator. It also admits any other `personalization-*` action. Web experiences send view, click and dismiss events [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_web.htm&release=264.0.0&type=5). Documented tokens are `personalization-view` and `personalization-click` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html); whether dismiss uses the `personalization-` prefix is not stated, so confirm the connector's Dismiss Action. `engagement_action__c` keeps distinct actions separate.
- The point filter becomes the `point_id__c` dimension, so one CI serves every point. `DATE_ADD(ts, 0)` produces a date dimension exactly as SP's own CIs do, and fully qualified `DMO.field` references match SP's CI definitions [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_uniques_ci_ref.htm&release=264.0.0&type=5).
- Read the output with `SELECT * FROM <CI_API_NAME>__cio WHERE point_id__c = '<POINT_ID>'` in Query Editor, or validate it in Data Explorer [src](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5). In reports, add all three dimensions before Q6b's measure appears [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_calculated_insights_limits.htm&release=264.0.0&type=5); daily uniques aren't additive across days.
- Neither CI is usable in segments: they carry no Profile-type primary key, and Q6b's non-aggregatable measure with a date dimension is hidden in the segment builder [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_in_segments.htm&release=264.0.0&type=5).
- CI reports can't add row-level or summary formulas [src](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_calculated_insights_limits.htm&release=264.0.0&type=5), so compute CTR in SQL (Q4) or in the BI tool.

### Q7. SP's Intelligence SQL for attribution — `doc sample (verbatim)`
Source: "Query Personalization Attribution by Personalization Point" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_personalization_attribution_by_personalization_point.htm&release=264.0.0&type=5).
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
Inconsistencies in the docs:
- `scm_PersonalizationPointViewAttribution__dlm` isn't a deployed name. Attribution Intelligence deploys `{dataspacePrefix}_{irSuffix}_PersnlPointFirstTouchViewAttr__dlm` and `..._PersnlPointLastTouchViewAttr__dlm` (plus `PersnlContent…` equivalents). The default data space adds no prefix; no ruleset adds no suffix; a ruleset with an empty suffix adds `e_s_`; a ruleset starting with a number in the default data space gets an `n_s_{irSuffix}` prefix [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5). `scm_` reads like a data space prefix.
- `AttributedOrdersCount__c` is on neither **point** DMO. Point First Touch has `AttributedOrderCount__c` and `AttributedOrdersPlaced__c`; point Last Touch has only `AttributedOrdersPlaced__c` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-view-attribution-dmo.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-click-attribution-dmo.html). Content Last Touch also has `AttributedOrderCount__c` and `AttributedOrdersPlaced__c` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-content-click-attribution.html).
- The field names split by model. First Touch uses `RootPersonalizationPoint__c`, `AttributedClickCount__c`, and has `AttributedViewsCount__c`; Last Touch uses `PersonalizationPoint__c`, `AttributedClicksCount__c`, and has no views field, so the sample's conversion rate can't run on it. The Last Touch object API name is printed as `PersnlPointLastTouchViewAttr__dmo` and lives at a `-click-attribution` URL (same sources).
- First Touch describes `AttributedViewsCount__c` as "Number of orders attributed to personalization views", which is a copy error [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-view-attribution-dmo.html).
- Top-level `ORDER BY` makes this Query Editor or JDBC SQL; it isn't valid CI SQL [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5). Summing `UniqueProfileCount__c` across dates over-counts people active on several days (inference).
- The sibling pipeline samples mix dialects and field generations: "View Personalization Pipeline Metrics by Date" uses `approx_distinct` with `RequestStartDateTime__c`, `ResponseTimeMillis__c`, and `NumContentItems__c` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_view_pipeline_metrics_by_date.htm&release=264.0.0&type=5); "Get Information About Personalization Pipeline Requests" uses `to_iso8601` with `RequestDateTime__c` and `ResponseTimeMillisecond__c` on the same `PersonalizationLog__dlm` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_pipeline_request_results.htm&release=264.0.0&type=5). The Query API V3 replacements are `approx_count_distinct` and `TO_CHAR` [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/query-api-migration.html), and SP's own CIs use `ssot__RequestDateTime__c` / `ssot__ResponseTimeMillisecond__c`.

Adapted for the deployed First Touch point DMO, `doc-derived (untested)`:
```sql
SELECT AttributionDate__c,
       RootPersonalizationPoint__c AS point_id,
       PersonalizationDecision__c AS decision_id,
       Personalizer__c AS personalizer_id,
       SUM(PersonalizationRequestCount__c) AS personalization_requests,
       SUM(AttributedViewsCount__c) AS views,
       SUM(AttributedClickCount__c) AS clicks,
       SUM(AttributedCartsCount__c) AS carts,
       SUM(AttributedOrdersPlaced__c) AS orders,
       SUM(AttributedRevenue__c) AS revenue,
       100.0 * SUM(AttributedOrdersPlaced__c) / NULLIF(SUM(AttributedViewsCount__c), 0) AS order_conversion_pct
FROM PersnlPointFirstTouchViewAttr__dlm   -- replace with the deployed API name from the Data Model tab
WHERE AttributionDate__c >= DATE '<START_DATE>' AND AttributionDate__c < DATE '<END_DATE>'
GROUP BY 1, 2, 3, 4
ORDER BY 1
```
- For Last Touch, use `PersonalizationPoint__c` and `AttributedClicksCount__c`, and drop views and the conversion rate.
- Predefined attribution requires Product Browse, Shopping Cart, and Product Order Engagement objects [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5); a manual-content-only site may have empty attribution DMOs (inference).

### Q8. Decision latency per point — `doc-derived (untested)`
Purpose: check whether slow decisions explain flicker-defense timeouts (default `redisplayTimeoutMilliseconds` is 2000 [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/configure-flicker-defense.html)).
```sql
SELECT p.ssot__PersonalizationPointId__c AS point_id,
       COUNT(DISTINCT p.ssot__PersonalizationRequestId__c) AS requests,
       AVG(p.ssot__ResponseTimeMillisecond__c) AS avg_ms,
       PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY p.ssot__ResponseTimeMillisecond__c) AS p95_ms,
       MAX(p.ssot__ResponseTimeMillisecond__c) AS max_ms
FROM ssot__PersonalizationLog__dlm p
WHERE p.ssot__RequestDateTime__c >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY p.ssot__PersonalizationPointId__c
ORDER BY p95_ms DESC
```
- Response time covers the augmenting, qualifying, and personalizing stages plus overhead [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html); network and rendering time come on top (inference). `PERCENTILE_CONT(<fraction>) WITHIN GROUP (ORDER BY …)` is the documented syntax [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/percentile-cont.html).
- The log can hold one row per content item (`ContentItemsQuantity` counts items "included in the denormalized Personalization Log"), which is why SP's CI divides response time by the item count [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5). Multi-item recommendation requests therefore weigh more in `AVG` and the percentile.

### Q9. Engagement events without a matching log row — `doc-derived (untested)`
Purpose: catch manual events with a wrong `contentId`, and other joins that silently drop data.
```sql
SELECT w.ssot__EngagementChannelActionId__c AS action,
       COUNT(*) AS events,
       SUM(CASE WHEN p.ssot__Id__c IS NULL THEN 1 ELSE 0 END) AS events_without_log_row
FROM ssot__WebsiteEngagement__dlm w
LEFT JOIN ssot__PersonalizationLog__dlm p
  ON w.ssot__PersonalizationContentId__c = p.ssot__Id__c
WHERE w.ssot__EngagementChannelActionId__c IN ('personalization-view', 'personalization-click')
  AND w.ssot__EngagementDateTm__c >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY w.ssot__EngagementChannelActionId__c
```
- Likely causes: manual events without the response's `personalizationId` / `personalizationContentId` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html), decisions requested with `TestMode`, which records nothing to the data lake [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html), or log rows still ingesting (inference).

### Q10. Identity sanity checks — `doc-derived (untested)`
Purpose: explain unrecognized signed-in visitors and merged strangers. The web mapping sends `IDName` → Identification Name, `IDType` → Party Identification Type, `userId` → Identification Number, and `deviceId` → Party [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html); field API names come from the Party Identification DMO page [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-party-identification-dmo.html).
```sql
/* Q10a: name and type pairs actually ingested; compare with the match rule's values */
SELECT pi.ssot__Name__c AS identification_name,
       pi.ssot__PartyIdentificationTypeId__c AS identification_type,
       COUNT(*) AS party_identification_rows
FROM ssot__PartyIdentification__dlm pi
GROUP BY 1, 2
ORDER BY 3 DESC;

/* Q10b: most shared identification numbers; placeholders such as NA or 0 surface here */
SELECT pi.ssot__Identificationnumber__c AS identification_number,
       COUNT(DISTINCT pi.ssot__PartyId__c) AS individuals
FROM ssot__PartyIdentification__dlm pi
GROUP BY 1
ORDER BY 2 DESC
LIMIT 20;

/* Q10c: largest unified profiles; swap in the ruleset's link DMO from Q5 */
SELECT l.UnifiedRecordId__c AS unified_individual,
       COUNT(*) AS linked_individuals
FROM IndividualIdentityLink__dlm l
GROUP BY 1
ORDER BY 2 DESC
LIMIT 20;
```
- Run each statement separately. Q10b's output contains member identifiers, so don't paste it into tickets or chat.
- Compare Q10a with the match rule's Party Identification Type and Name values [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5). Placeholder values are a documented cause of oversized unified profiles, and identity resolution can't combine more than 50,000 records into one unified profile [src](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ir_errors.htm&release=264.0.0&type=5).
- Next steps when a rule matches nothing: group Party Identification by data source as well as Name and Type, then run the web-to-CRM acceptance query on the link object with a negative control ([field-guide-data.md](field-guide-data.md) §4).
- Q10b uses the DMO page spelling `ssot__Identificationnumber__c`; identity resolution troubleshooting writes `ssot__IdentificationNumber__c`. If one fails, use the other or the Query Editor field picker.

## Gaps and uncertainties
- Only Q1 and Q2 have run in a live org. Interval literals, `PERCENTILE_CONT`, and `DATE` literals in Q4, Q7, Q8, and Q9 follow the Data 360 SQL reference but are untested.
- No rule states that CI aliases must end in `__c`; every documented example does.
- Which naming set (`ssot__` or `std__`) an org exposes isn't documented. Attribution DMO naming is documented for empty prefixes and suffixes (see Q7), but no page shows a fully resolved example.
- Whether Query Editor requires quoted identifiers for mixed-case names is unconfirmed; Q1 and Q2 ran unquoted.
- The SP mapping table doesn't document the Website Engagement mapping for `userEngagement`; the `ssot__EngagementChannelActionId__c` values rely on the field-verified Q1.
- The Personalization Log field that stores diagnostic codes for unauthenticated calls isn't identified. The standard DMO has `StatusCode` "defined by HTTP status codes (200, 500, 501)" [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html); its `ssot__` name is unverified.

## Sources
- Query Editor and Data 360 SQL: [Query Editor](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor.htm&release=264.0.0&type=5), [Create queries](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor_create_queries.htm&release=264.0.0&type=5), [Integrated apps](https://developer.salesforce.com/docs/data/data-cloud-query-guide/guide/int-apps-data-cloud.html), [SQL reference](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/data-cloud-sql-context.html), [SELECT](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/select.html), [Date/time](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/datetime-func.html), [approx_count_distinct](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/approx-count-distinct.html), [percentile_cont](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/dc-sql-reference/percentile-cont.html), [Query API V3 migration](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/query-api-migration.html), [Logical views (quoting)](https://developer.salesforce.com/docs/data/semantic-layer/guide/query-api-in-depth-logical-views.html)
- Calculated insights: [Use SQL](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5), [Create with SQL](https://help.salesforce.com/s/articleView?id=data.c360_a_get_started_with_calculated_insights.htm&release=264.0.0&type=5), [SQL rules](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_general_sql_rules.htm&release=264.0.0&type=5), [Functions](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5), [Operators](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_operators.htm&release=264.0.0&type=5), [Edit](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_calculated_insight_in_customer_data_platform.htm&release=264.0.0&type=5), [Schedule](https://help.salesforce.com/s/articleView?id=data.c360_a_schedule_a_calculated_insight_in_data_cloud.htm&release=264.0.0&type=5), [Limits](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5), [Segments](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_in_segments.htm&release=264.0.0&type=5), [Validate](https://help.salesforce.com/s/articleView?id=data.c360_a_validate_an_insight_in_data_cloud.htm&release=264.0.0&type=5), [Report considerations](https://help.salesforce.com/s/articleView?id=analytics.rd_dc_reports_calculated_insights_limits.htm&release=264.0.0&type=5)
- SP data: [CI naming](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_insights_dmo_name_field_reqs.htm&release=264.0.0&type=5), [Daily Requests CI](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_requests_ci_ref.htm&release=264.0.0&type=5), [Daily Uniques CI](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_daily_personalization_uniques_ci_ref.htm&release=264.0.0&type=5), [Attribution deploy](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5), [Attribution by point](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_personalization_attribution_by_personalization_point.htm&release=264.0.0&type=5), [Pipeline by date](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_view_pipeline_metrics_by_date.htm&release=264.0.0&type=5), [Pipeline requests](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_query_pipeline_request_results.htm&release=264.0.0&type=5), [Attribution dashboard](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_pers_attrib_intelligence_using.htm&release=264.0.0&type=5), [Web experiences](https://help.salesforce.com/s/articleView?id=mktg.persnl_experience_web.htm&release=264.0.0&type=5), [Real-time IR](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5)
- SP developer guide: [Personalization Log DMO](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html), [First Touch DMO](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-view-attribution-dmo.html), [Last Touch DMO](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-click-attribution-dmo.html), [Track engagement](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html), [Integrate SDK](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html), [Request Personalization](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html), [Flicker defense](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/configure-flicker-defense.html)
- DMOs and identity: [Website Engagement](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html), [Std Website Engagement](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-websiteengagementdmo-dmo.html), [Std Personalization Log](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html), [Party Identification](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-party-identification-dmo.html), [Link objects](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5), [Create ruleset](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5), [IR errors](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ir_errors.htm&release=264.0.0&type=5), [Event structure](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-event-structure.html)

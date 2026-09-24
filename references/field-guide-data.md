# Field Guide: Data, Identity Resolution, Measurement and Operations

## Scope

- Lessons verified in real Salesforce Personalization (SP) implementations that the official docs don't state, on the Data 360 side:
  - identity resolution design
  - website connector schema and mapping traps
  - targeting on child records
  - measurement and SQL diagnosis
  - credits, rollout and UAT practice
  - privacy decisions that need sign-off

  Browser-side lessons (consent wiring, identity capture, sitemap engineering, WPM anchors, sitemap tests): [field-guide-web.md](field-guide-web.md).
- Every lesson is generic: any industry, data source or identifier type. Numbers are examples to measure against, never rules.
- Labels:
  - "(Field-observed, undocumented)": seen in practice and absent from the docs. Re-test after every seasonal release.
  - "(inference)": a design choice built on documented behavior. "(UNVERIFIED)": plausible, confirmed by neither a doc nor a field test.
  - Documented building blocks carry `[src](url)`.
- Format: **Lesson.** Why it matters. **Do:** the fix. Setup facts and limits: [platform-and-setup.md](platform-and-setup.md). Graphs and decisions: [decisioning.md](decisioning.md). Queries: [sql-cookbook.md](sql-cookbook.md).
- Placeholders: `<WEB_SOURCE_ID>` (the website connector's data source ID), `<ID_NAME>`, `<ID_TYPE>`.

## 1. Identity resolution design

### 1.1 Party identifiers

- **All three values must match exactly.** A party identifier match is an exact match of Identification Number, Identification Name and Party Identification Type. Party Identification ID, Party (the foreign key to the Individual or Account), Type, Number and Name must be mapped before the object can be used, and Match on Blank isn't allowed [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5). **Do:** set Name and Type on the criterion to exactly the strings the web sends.
- **"Match to" (cross-object matching) can silently break party-identifier matching.**
  - Symptom: web profiles never unify with CRM profiles, and even web devices with the same identifier stay separate.
  - Docs: the match-rule steps mention cross-object matching in one sentence, in advanced criteria: "the object you want to match to must be modeled properly" [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5).
  - Observed: a "Match to" target on the party-identifier criterion replaced the same-field Party Identification comparison. Once set, it couldn't be cleared from its dropdown; the criterion had to be deleted and recreated (Field-observed, undocumented).
  - **Do:** leave "Match to" empty. Land the CRM identifier as Party Identification rows with the Name and Type the web sends, through the source feed (preferred) or a data transform. Open a Support case if you need cross-object behavior.
- **Case sensitivity is opt-in.** Without `Case Sensitive`, uppercase and lowercase letters match [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5). **Do:** tick it for case-significant tokens (mixed-case federated or random IDs), batched with other rule changes (§1.3). Whether real-time runs honor it is UNVERIFIED. The docs disagree on scope: the Apex API allows `caseSensitiveMatch` only on party-identifier criteria, while Help describes it as an advanced setting for match criteria ([data-360-foundations.md](data-360-foundations.md)).
- **Match on Blank over-merges.** On frequently empty fields it links incomplete records into one profile, can cause the "matched 50,000 or more other profiles" error, and is ignored in real time [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5). Keep it off for sparse standard-field criteria.
- **Never match on Party Identification ID for web rows.** The SP mapping writes `deviceId` into both Party and Party Identification ID [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html), so the rule would unify by browser, not by person (inference).
- **Plan one `partyIdentification` row per device × identifier type.** The row's primary key is `deviceId` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html). A second identifier type sent from the same browser overwrites the first, and matching on the first silently stops (observed; mechanism inferred from the key). **Do:** if more than one type will ever be sent, key rows per device × type before the schema locks, and keep `deviceId` → Party. Never key on the identifier value alone: every device of a person would share one row.
- **A second person on the same device doesn't fuse two people.** Their `partyIdentification` upserts the device's row, so the next run re-attributes that device's history to the second person (inference from the key). **Do:** call `resetAnonymousId()` before binding a different user ([field-guide-web.md](field-guide-web.md) §2.3). Never call `setAnonymousId()` to mark a login: it splits one person's behavior before and after login (Field-observed).

### 1.2 Limits and real-time behavior

- **Hard limits that shape the design** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5):
  - 5 rulesets per primary DMO per data space (2 on the legacy Customer Data Platform license [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines_cdp.htm&release=264.0.0&type=5)).
  - 10 match rules per ruleset and 10 criteria per rule.
  - Scheduled at most once a day, and at most 4 ruleset jobs per ruleset per data space in 24 hours. Jobs are skipped when nothing changed.
  - Source records over 15 KB are skipped. Matched values over 500 combined characters are truncated and can mis-match.
  - 50,000 source profiles per unified profile.
  - 75 source profile identifiers per unified profile, of which a real-time graph includes no more than 25 profile records from website and mobile connections and 50 others.
  - 100 engagement events per unified profile.
- **Extra web devices fall out of real time.** Real-time matching prioritizes profiles with recent, frequent and authenticated activity [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_type_compare.htm&release=264.0.0&type=5). A person with more than 25 web or mobile records can get anonymous decisions on the rest (inference). **Do:** monitor web rows per unified profile, especially if devices rotate on logout.
- **Real-time can't rescue a merge the scheduled run doesn't make.**
  - Real-time unification needs an Individual-based ruleset whose output Unified Individual roots a real-time data graph [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_realtime.htm&release=264.0.0&type=5).
  - It compares the input with unified profiles in that graph, which a scheduled run refreshes once a day, and a non-exact input returns no profile [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_type_compare.htm&release=264.0.0&type=5).
  - It isn't available on the legacy Customer Data Platform license [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines_cdp.htm&release=264.0.0&type=5).
  - **Do:** fix the scheduled rule first, and confirm the license early. Whether match-rule objects must also be graph nodes is UNVERIFIED, so test a CRM-only identifier in real time.
- **Batch identity rows unify at the next run.** Rulesets process every 60 minutes to 24 hours depending on the source; streaming connectors after 1 hour or 500 changes, whichever is sooner; Web SDK real-time data immediately [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_processing_frequency.htm&release=264.0.0&type=5). **Do:** run the ruleset manually to test sooner. A manual run counts toward the 4 jobs per 24 hours.

### 1.3 Changes that trigger billable full reruns

- **Full-run triggers** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5):
  - changing a ruleset's match rules or reconciliation rules
  - adding or changing ruleset filter conditions
  - mapping a new DLO to a DMO used in a ruleset
  - mapping any new field to a DMO used in any ruleset, including Is Anonymous
- **Batch identity changes** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5):
  - disable `Run jobs automatically`, make every change, then resume
  - test new rulesets in a sandbox or a small data space first
  - keep one active ruleset per primary DMO per data space
  - **Do:** prefer adding rows to an already-mapped feed over mapping a new DLO (inference).
- **On an existing production ruleset, add a dedicated rule.** Add Party Identification / Identification Number / Exact with the web Name and Type, instead of editing a multi-criteria rule; removing criteria loosens matching for every existing profile. Anonymous web profiles have no names, so rules that require name criteria never match them. Real-time runs every rule as Exact or Exact Normalized [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5), so the single exact rule is the one that works in-session. **Do:** record unified, known and anonymous counts before and after. A second ruleset creates a parallel set of unified profiles, and records processed by all active rulesets are summed for billing [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
- **Pre-run checks for a new identifier feed**, before spending a full run (Field-observed):
  1. In the raw DLO, Name and Type exactly equal the rule's values, and Identification Number lengths cluster as expected.
  2. Key qualifiers are populated on both sides of the Party → Individual relationship, or on neither. One-sided qualifiers orphan rows silently.
  3. A `LEFT JOIN` from Party Identification to Individual returns an Individual for every new row.

  A DMO-level relationship is inherited by newly mapped DLOs.
- **After changing `IDName` or `IDType`,** older rows keep the old pair and fall outside the rule. **Do:** filter every count by Name, clear cookies and re-test instead of reasoning about mixed data, and change the rule and the sitemap constants together.

### 1.4 Anonymous flag and reconciliation

- **Is Anonymous decides known vs anonymous counts.** A source profile without the field mapped is always known; known values are `0`, `No`, `N`, `F`, `False` or empty (not case-sensitive); unified profiles become `0` (known) or `1` (anonymous) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5). **Do:** map it on every Individual stream; the mapping triggers a full run (§1.3). The SDK's automatic event sends `isAnonymous: true` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html) while custom code often sends strings, so check the stored values.
- **Reconciliation decides the value targeting reads** on a unified root [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5):
  - `Last Updated` needs Last Modified Date mapped. The SP web `identity` mapping sends `dateTime` to Created Date [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html).
  - `Most Frequent` and `Source Priority` accept `Ignore Empty Values`.
  - Rules don't apply to contact points.

  **Do:** put the web source lowest in Source Priority, with Ignore Empty Values on for name fields, so anonymous web events can't blank CRM values. For web-owned fields such as a consent string, choose a rule that lets the latest device win. Partial refresh only protects each device's own row [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html); the unified value comes from reconciliation.

## 2. Website connector schema and mapping traps

- **Schema changes reach streams only through Sync Schema.** After **Update Schema**, open each data stream [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-update-mobile-web-datastream.html):
  1. **Sync Schema** adds new fields to events already in the stream.
  2. **Add Events** adds new events; Sync Schema won't.
  3. **Data Mapping** → **Start**: map each new field. Unmapped fields aren't available for segments, calculated insights or activations.
- **Additive and optional only.** New fields must be optional (`isDataRequired: false`), and existing fields can't be updated or renamed [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html). Display labels are part of that. Dead fields can't be removed either: leave them unmapped.
- **Treat required fields as a hard contract.** `isDataRequired: true` means the field "must be sent when the parent event is sent" [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html). The effect of omitting it is undocumented, so treat such events as lost and assert payloads in tests ([field-guide-web.md](field-guide-web.md) §7).
- **One engagement DLO, one primary key.** All engagement events are combined into a single DLO, so give every engagement event the same `primaryIndexOrder: 1` field (`eventId`) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html). Changing the key later needs a new connection, or deleting every data stream [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-update-mobile-web-datastream.html).
- **Refresh mode decides the payload shape.** Incremental blanks the fields an update omits. Partial keeps them, and by default applies only to events with the same device ID [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html). The Ingestion API's partial update changes only the fields in the payload [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-perform-partial-update-on-record.html). **Do:** use Partial for web profile streams and omit unknown values, because an `""` is a value and overwrites (inference). Send complete records under the other modes.
- **Review every auto-mapped row.** Automapping suggests fields from past mappings, exact, standardized and fuzzy name matches, and synonyms [src](https://help.salesforce.com/s/articleView?id=data.c360_a_automapping_dlo_dmo.htm&release=264.0.0&type=5). A schema label such as "Engagement Channel Type" on `interactionName` pre-fills the wrong field. **Do:** map `interactionName` → **Engagement Channel Action** and each event group's `eventType` → **Engagement Type**, as the SP behavioral mapping table does for catalog, cart and order [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_behavioral_events_data_mapping_ref.htm&release=264.0.0&type=5). Leave Engagement Channel Type empty. The same applies to custom engagement events such as `userEngagement` (inference).
- **A DMO field takes one source field.** Mapping a second raises **Replace Mapping** and displaces the first, while the canvas still looks complete. One source feeding several DMO fields is fine. Events that share labels (`consentLog` and `userEngagement` both carry Page URL, Webpage Type…) give auto-mapping two candidates per row. **Do:** confirm each row resolved to the engagement event. (Field-observed.)
- **Map `eventType` inside each event group.** The SP table has no All Event Data `eventType` row [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_references_behavioral_events_data_mapping_ref.htm&release=264.0.0&type=5). Rows from unmapped groups (Consent Log) still reach the engagement DMO through the All Event Data mappings (date, individual, ID), with every other column blank. **Do:** filter reports on action values, never on "all rows" (Field-observed).
- **Know which fields hoist into All Event Data.** Only envelope fields (`category`, `dateTime`, `deviceId`, `eventId`, `eventType`, `sessionId`) and recognized standard fields (`personalizationId`, `personalizationContentId`) move there; others stay prefixed per event. A custom field that stays prefixed isn't a recognized standard field (Field-observed).
- **Leave envelope fields unmapped on profile streams.** On `identity` and `partyIdentification`, don't map the fields labelled Session, Webpage Type, Page URL or Referrer URL; Individual and Party Identification have no such fields (Field-observed).
- **Map web `deviceId` to both Party Identification ID and Party** [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html). With only one, rows collide or float unattached, and identity resolution matches nothing. The SP setup guide also maps Party on Contact Point Email and Phone, and leaves address unmapped ([data-360-foundations.md](data-360-foundations.md)).
- **Device enrichment is available.** The schema guide lists optional fields derived from the user agent (device type, browser, OS) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html). In practice they arrive as `cdp_sys_*` fields in the engagement DLO; map them to the matching Website Engagement fields for device targeting (Field-observed field names).
- **Expect event types you didn't declare.** Beacon payloads can include them (observed: `MetadataUpdate`). Filter reports on explicit event types or actions.
- **`sourceLocale` is the page's locale** [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). Mapping it to Website Engagement Device Locale is a semantic override. If a true device locale is ever captured, move the site locale to a custom field.
- **Check PK/FK direction when one DLO feeds two DMOs.** A DLO can map to two DMOs keyed on different columns (one source row feeding both Party Identification and a subscription DMO, say), and neither key has to be the DLO's primary key. A reversed PK/FK mapping breaks joins without errors. An empty Related Field picklist when you create a relationship usually means the two fields' data types differ. (Field-observed.)
- **`Other`-category DLOs can map to Profile DMOs** such as Party Identification. Profile and Other DLOs can't map to Engagement DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5).

## 3. Targeting and data graphs

- **"At least one child row where A and B hold".** In the targeting rule, pick `Related Attributes` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_targeting_rules_create.htm&release=264.0.0&type=5), then the related object's `Count` · `Is Greater Than` · `0`, and put every row condition (value match, not-deleted flag) in its WHERE. An equality test on the count misses people with more matching rows than expected. Flat conditions on the child object evaluate independently, so they don't mean "one row meets all". Boolean operators take no value field. (Field-observed; operators are unpublished.)
- **Targeting on consent categories:** the pattern is in [field-guide-web.md](field-guide-web.md) §1.3.
- **Data graph Preview shows structure, not data.** **Preview** returns the graph's JSON structure [src](https://help.salesforce.com/s/articleView?id=data.c360_a_view_data_graph_metadata.htm&release=264.0.0&type=5); in practice it holds type placeholders and illustrative repeats. **Do:** use it to confirm a traversal path, and Data Explorer or SQL for values (Field-observed).
- **Remove graph fields only while in draft.** A draft graph lets you add and remove objects and fields; any other status allows additions only [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5). **Do:** select only what targeting needs, and never a field that must not appear in decision responses.
- **Batch updates can lag for active visitors.** Session extension "can sometimes delay the availability of lake house updates in your real-time data graph" [src](https://help.salesforce.com/s/articleView?id=data.c360_a_sess_ext_data_graphs.htm&release=264.0.0&type=5). **Do:** test batch-driven changes in a fresh browser session, and send facts that must change mid-session through real-time ingestion.
- **Isolate the platform from the browser.** Call the point on the authenticated endpoint with `context.individualId` set to a source Individual ID (a web device ID or a CRM ID) and `executionFlags: ["TestMode"]`, so no outputs are recorded to the data lake [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html). A right decision there but a wrong one in the browser means the browser session resolves to an unstitched anonymous ID, not a rule problem.
- **Prove unification in the browser with a temporary merge field.** Bind a decision attribute to a merge field that shows the unified individual ID; merge fields read attributes of the profile data graph [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5). The same value on two devices shows they unified. Remove it before go-live, and confirm with the link-object query in §4. (Field-observed technique.)

## 4. Measurement and SQL diagnosis

- **Zero rows? Remove filters one at a time.** Validate each remaining value with its own `GROUP BY` (page type, action, point), then group by `ssot__PersonalizationPointId__c` to read the real point ID. (Field-observed method.)
- **A rule matches nothing: find which sources write its Name/Type pair.** `field-verified (Query Editor)`

```sql
SELECT pi.ssot__DataSourceId__c AS data_source,
       pi.ssot__PartyIdentificationTypeId__c AS identification_type,
       pi.ssot__Name__c AS identification_name,
       COUNT(*) AS party_identification_rows
FROM ssot__PartyIdentification__dlm pi
GROUP BY 1, 2, 3
ORDER BY 4 DESC
```

  If only the web source writes the rule's pair, the other side lives elsewhere (a field on Individual, for example) and nothing can match. Also compare `COUNT(*)` with the distinct primary keys and read the ruleset's processing history. A steadily rising anonymous unified-profile count with no mixed-source profiles is the platform-level sign that web profiles never convert.
- **Acceptance test for web-to-CRM unification**, using the ruleset's link object; the API name gains the ruleset ID when one is set [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5). (Field-observed method.)

```sql
SELECT l.UnifiedRecordId__c AS unified_individual,
       SUM(CASE WHEN l.ssot__DataSourceId__c = '<WEB_SOURCE_ID>' THEN 1 ELSE 0 END) AS web_rows,
       COUNT(*) AS all_rows
FROM IndividualIdentityLink__dlm l
GROUP BY 1
HAVING SUM(CASE WHEN l.ssot__DataSourceId__c = '<WEB_SOURCE_ID>' THEN 1 ELSE 0 END) > 0
   AND COUNT(*) > SUM(CASE WHEN l.ssot__DataSourceId__c = '<WEB_SOURCE_ID>' THEN 1 ELSE 0 END)
```

  Each row is a unified profile that holds both web and non-web sources. Negative control: a fabricated test identifier must stay a separate unified profile.
- **Row-level impression reporting needs a materialized table.** Calculated insights must include at least one aggregate measure [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5), so they suit metrics, not "who saw which decision when". **Do:** write a batch data transform to a DLO output node [src](https://help.salesforce.com/s/articleView?id=data.c360_a_batch_transform_output_node_dlo.htm&release=264.0.0&type=5), joining engagement → Personalization Log (content ID) → point and decision → link object (inference).
- **Consent Log rows in engagement DMOs** have blank action columns (§2), so every report filters on explicit action values.
- **Missing anchors don't show in reports.** An anchor missing for one audience removes its views without a visible gap ([field-guide-web.md](field-guide-web.md) §5). Compare views per audience against page views per audience.
- More queries: [sql-cookbook.md](sql-cookbook.md) (Q2 point IDs, Q10 identity sanity).

## 5. Credits and consumption

- **Every web event row bills Streaming Pipeline**, including pages with no experience: website connector streams report that usage type. Events associated with a real-time data graph also count toward Real-Time Pipeline [src](https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5). **Do:** estimate from Digital Wallet and Personalization Log request counts.
- **Unification bills new or modified source profiles** after the first run [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5). Each rotated device ID is a new source profile, so rotating on every logout or signed-out arrival adds unification volume (inference).
- **Batch identity changes** into one full rerun (§1.3).
- **Decisions follow experience Locations.** Pages with no enabled matching experience made no decision request (Field-observed). An experience bound to the default page type, or to a broad `Page URL` wildcard [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5), requests a decision on every matching view. **Do:** before go-live, disable or delete proof-of-concept and test experiences still `Enabled` on broad locations.
- **Keep profile re-sends session-scoped**, not per page ([field-guide-web.md](field-guide-web.md) §2.4).

## 6. Rollout and UAT practice

- **Seed decoy records.** Proof-of-concept data should include records that must not match, so a working rule is shown to be selective, not just "the only row present".
- **Snapshot identity counts** (unified, known, anonymous) before and after every ruleset change (§1.3).
- **Run the acceptance test and its negative control** (§4) after the first full run that includes web data.
- **Test user switches and consent in the browser** ([field-guide-web.md](field-guide-web.md) §7).
- **Record test-environment errors.** Backend failures change what pages render and can masquerade as anchor or targeting defects.
- **Remove diagnostics before go-live:** the unified-ID merge field (§3), debug logging, version banners.
- **Monitor identity after launch:**
  - sign-ins that produce no `partyIdentification`
  - web rows per unified profile against the 25-record real-time cap (§1.2)
  - anonymous unified-profile growth
  - the Q10 checks in [sql-cookbook.md](sql-cookbook.md)

## 7. Privacy decisions requiring sign-off

- **The CMP category mapped to `Tracking`.** Never an always-on necessary category without sign-off ([SKILL.md](../SKILL.md)); how many categories the SDK cookie requires ([field-guide-web.md](field-guide-web.md) §1.1).
- **Consent categories stored as a profile attribute** ([field-guide-web.md](field-guide-web.md) §1.3).
- **The unbind policy.** A missed reset is recoverable; a spurious one splits a person across devices or rotates them mid-session.
  - Rotating whenever a browser arrives signed out (session expiry) mints a new Individual on each return visit. That means more unification, and more rows toward the 25 web and mobile records a real-time graph keeps [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
  - Not rotating keeps the browser resolving to that person for anyone who uses it, and attributes their browsing to that person, so it appears in that person's data subject export.
  - **Do:** choose with privacy. If browsers stay bound, gate personal experiences on a live signed-in signal from the current page.
- **Identifiers kept in browser storage.** List every one: site keys that survive sign-out, and the sitemap's own bound-identifier key. Any script on the origin can read them, so prefer opaque tokens to raw customer numbers.
- **Hashed identifiers** aren't anonymized when the source ID is short or numeric ([field-guide-web.md](field-guide-web.md) §2.1).
- **A fail-closed `Opt Out` ceiling** instead of `[]`. It needs sign-off, and whether it writes a Consent Log row is undocumented ([field-guide-web.md](field-guide-web.md) §1.2).

## Gaps and uncertainties

- Cross-object "Match to" behavior is documented in one sentence; its interaction with party-identifier criteria and its inability to be cleared are field-observed only.
- Undocumented: whether real-time runs honor `Case Sensitive`; whether match-rule objects must be real-time graph nodes; the effect of omitting an `isDataRequired` field; `cdp_sys_*` field names; All Event Data hoisting; `MetadataUpdate` events; envelope-only Consent Log rows in engagement DMOs.
- Inferred from primary keys, not stated: `partyIdentification` overwrite per device, and history re-attribution to a second person on the same device.
- Targeting-rule operators (`Count`, `Is Greater Than`, `contains`) are unpublished; confirm them in the decision wizard.
- Data graph Preview content and the per-audience reporting gap from missing anchors are observed behavior.

## Sources

Data 360 Help — identity resolution:
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines_cdp.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_realtime.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_type_compare.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_processing_frequency.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_identity_resolution.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5

Data 360 Help — modeling, graphs, insights, billing:
- https://help.salesforce.com/s/articleView?id=data.c360_a_automapping_dlo_dmo.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_view_data_graph_metadata.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_sess_ext_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_calculated_insights_sql_function.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_batch_transform_output_node_dlo.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5

Data 360 integration guide and Interactions SDK:
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-update-mobile-web-datastream.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-sdk-schema-quick-guide.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-perform-partial-update-on-record.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-user-data.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html

SP developer guide and SP Help:
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html
- https://help.salesforce.com/s/articleView?id=mktg.persnl_references_behavioral_events_data_mapping_ref.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_targeting_rules_create.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_use_predefined_templates.htm&release=264.0.0&type=5

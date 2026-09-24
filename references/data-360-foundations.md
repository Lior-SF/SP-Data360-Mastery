# Data 360 Foundations for Personalization

## Scope

- The Data 360 data layer that Salesforce Personalization (SP) reads: data streams, data lake objects (DLOs), data model objects (DMOs), mapping, the identity DMOs, identity resolution rulesets (match and reconciliation rules), unified outputs, and the data graphs that personalization points evaluate. Applies to any industry, channel and data source.
- Read this file for **how the platform works** (documented objects, rules, limits, names). Read [field-guide-data.md](field-guide-data.md) for **field-verified design lessons** (party-identifier design, "Match to", billable reruns, connector mapping traps) and [sql-cookbook.md](sql-cookbook.md) for **reporting SQL** (views, clicks, CTR, unified counts). Data graph use inside points and decisions: [decisioning.md](decisioning.md) §1–§2. Web identity events: [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §4.
- Baseline: Data 360 Help and developer docs at release 264.0.0. Labels: "(Field-observed, undocumented)" = seen in implementations, absent from docs; "(inference)" = reasoned from cited docs; "(UNVERIFIED)" = neither documented nor field-tested. The UI still shows "Data Cloud" in many labels.
- Placeholders: `<DLO_API_NAME>`, `<LINK_DMO>` (the ruleset's link object name without `__dlm`), `<TEST_SOURCE_ID>`, `<ID_NAME>`, `<ID_TYPE>`.

## Data pipeline: data stream → DSO → DLO → DMO

### Objects

| Object | What it is | Notes |
|---|---|---|
| Data stream | A job that pulls or receives data from a source through a connector | Carries a category fixed at save [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5), a refresh mode and a schedule [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_edit_settings.htm&release=264.0.0&type=5) |
| Data source object (DSO) | The source-side object a stream reads (a CRM object, a file, an Ingestion API object, a web/mobile schema event) | No Help page defines "DSO"; the term surfaces as `ssot__DataSourceObjectId__c` on DMO and link rows [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-individual-dmo.html) |
| Data lake object (DLO) | "A container for the data brought into Data 360"; created automatically by a stream, or manually | External DLOs point to federated data; unstructured DLOs (UDLOs) reference unstructured data and are created manually [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_lake_objects.htm&release=264.0.0&type=5) |
| Data model object (DMO) | "A harmonized grouping of data created from data streams, insights, and other sources"; a DLO is mapped to it | Standard (Customer 360 Data Model) or custom [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_ingestion_and_modeling.htm&release=264.0.0&type=5) |

- **Ingestion is as-is:** fields and data types are imported without transformation and written to DLOs; modeling then harmonizes those schemas by mapping DLOs to DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_ingestion_and_modeling.htm&release=264.0.0&type=5).
- **Step by step:** connector → data stream (category, primary key, event time or record-modified field, refresh mode, optional formula fields) → DLO (raw rows) → field mapping to one or more DMOs → relationships between DMOs → identity resolution on a Profile DMO → unified DMOs → data graphs, calculated insights, segments → SP.
- Monitor landing in two places. The **data stream** refresh history shows per run records processed, added, removed and problem records; the **DLO** refresh history shows hourly windows (kept 20 days) of total, added, updated and removed records. DLO added/removed counts reflect storage file rewrites, so a small load can show millions removed and added; use the stream history for business volumes and billing [src](https://help.salesforce.com/s/articleView?id=data.c360_a_datastream_dlo_refresh_history.htm&release=264.0.0&type=5).

### Categories

| Category | Use for | Rules |
|---|---|---|
| Profile | People, accounts, or any entity you segment, unify or enrich (devices, loyalty cards…) | Profile DLOs map to Profile or Other DMOs, never Engagement [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5) |
| Engagement | Time-series events | Requires an **Event Time Field** (Date/DateTime), not editable after setup; a mutable date (Updated Date, file extract date) duplicates rows with the same primary key. Engagement DLOs map only to Engagement DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5) |
| Other | Reference data (catalogs, stores, models); time-series data without an immutable date | Maps to Profile or Other DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5) |

- The category **can't be changed** after the stream is saved [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5).
- A DMO has no built-in category: it **inherits the category of the first DLO mapped to it**, and the mapping canvas then offers only compatible DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5).
- Reusing an existing DLO for a new file stream: the first stream defines primary key, event date time and record-modified field; Engagement DLOs need an Event Date Time assignment, Profile DLOs the Record Modified field if one was declared [src](https://help.salesforce.com/s/articleView?id=data.c360_a_guardrails_existing_data_lake_object.htm&release=264.0.0&type=5).

### Refresh modes

| Mode | Where | Behavior and gotchas |
|---|---|---|
| Incremental | Most non-file streams with a DateTime field | Pick the last-modified field; each run takes rows added or changed since the last run and reprocesses a few previous rows. Deletes need a Delete Record Flag in the source [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_edit_settings.htm&release=264.0.0&type=5) |
| Upsert | File-based connectors | Adds or changes rows; delete through a delete file [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_edit_settings.htm&release=264.0.0&type=5) |
| Full Refresh | Default when nothing else is available | Every run deletes all rows and replaces them with the new import [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_edit_settings.htm&release=264.0.0&type=5); a partial extract therefore shrinks the DLO to that extract (inference) |
| Web/mobile profile streams: Incremental or Partial | Each profile event stream of a website or mobile connector | Incremental blanks fields the update omits; Partial keeps them and by default applies only to events with the same device ID [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html). The page offers the choice only for profile streams, not the engagement stream (inference) |

- Salesforce CRM streams: incremental refresh every 10 minutes; periodic full refresh is off in new streams until you set an interval; formulas are recalculated only when a record changed. **Refresh Now** on the stream record runs a refresh on demand [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_schedule.htm&release=264.0.0&type=5).
- Ingestion API partial updates change only the fields in the payload, need Refresh Mode **Partial** and the **streaming** endpoint; bulk jobs are processed as upsert, so missing fields become null [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-perform-partial-update-on-record.html). Partial is offered only for Profile and Other streams and can't be changed after creation [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-create-ingestion-data-stream.html).

### Formula fields

- Added on the **New Data Stream** page (**New Formula Field**): label, API name, return type (Text, Number, DateTime, Date, Email, Phone, URL, Percent, Boolean), then a formula over stream fields, text, functions and operators, tested in the formula panel before save [src](https://help.salesforce.com/s/articleView?id=data.c360_a_formula_expression_library.htm&release=264.0.0&type=5).
- Salesforce connectors and Connector services don't support Email, Percent, Phone, Boolean or URL return types [src](https://help.salesforce.com/s/articleView?id=data.c360_a_formula_expression_library.htm&release=264.0.0&type=5).
- Typical personalization uses: a constant source label, a normalized identifier (trim/upper-case) so Exact matching works, or a composite key (inference).

### Mapping rules and restrictions

- A DLO can map to one or more DMOs; a DMO field accepts one source field, while one DLO field may feed several fields of the same DMO [src](https://help.salesforce.com/s/articleView?id=data.c360_a_map_custom_data_model_objects.htm&release=264.0.0&type=5).
- Mapping a Profile or Other DMO can't be saved until its primary key is mapped; an Engagement DMO also needs the Event dateTime field [src](https://help.salesforce.com/s/articleView?id=data.c360_a_required_data_mappings.htm&release=264.0.0&type=5).
- Automapping suggests targets from past mappings, exact, standardized and fuzzy name matches and synonyms; review every row [src](https://help.salesforce.com/s/articleView?id=data.c360_a_automapping_dlo_dmo.htm&release=264.0.0&type=5).
- Relationships: DMO relationships are 1:1 or N:1, and **cardinality can't be changed** after creation [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_model_object_relationships.htm&release=264.0.0&type=5). In segmentation, relationship joins are case-sensitive and not configurable: `c12d3` doesn't link to `C12D3` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_segment_canvas_interface.htm&release=264.0.0&type=5).
- DLO fields can't be deleted; a stream-owned DLO is extended from the Data Streams tab, not the Data Lake Objects tab [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_lake_objects.htm&release=264.0.0&type=5).
- **Fully qualified keys:** when several sources share key values, configure key qualifier fields on every DLO key field (primary or foreign), up to 20 active qualifiers; Data 360 propagates them to DMOs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_fully_qualified_keys.htm&release=264.0.0&type=5).
- Limits: 1,050 fields per data stream (800 of one type), 5,000 streams and 5,000 DLOs per org [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).

### How SP-related connectors create streams

- **Website / mobile app connector:** upload a schema; all engagement events land in **one Engagement stream (one DLO)**, and each Profile or Other event (`identity`, `partyIdentification`, `contactPointEmail`…) gets **its own stream** [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html). That data stream page says Data 360 ingests engagement data every 15 minutes and profile data every hour. The limits page lists a different expected Mobile and Web SDK latency: profile 2–3 minutes, engagement 2–3 minutes, real-time 300 ms [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5). Identity resolution treats Web SDK real-time data separately (§ Real-time matching). Engagement events share the primary key `eventId`; profile events are keyed on `deviceId` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html). Schema changes are additive and reach streams only through **Sync Schema** / **Add Events** ([field-guide-data.md](field-guide-data.md) §2).
- **Ingestion API:** Setup → **Ingestion API** → New → upload an OpenAPI 3.0.x `.yaml` schema; one data stream per object per connection; objects can't nest or be deleted, fields can't be removed; streaming and bulk patterns share a stream [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-connect-an-ingestion-source.html) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-ingestion-api-schema-req.html) [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-ingestion-api.html). Allow up to 1 hour for data to appear [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-create-ingestion-data-stream.html).

### Naming conventions

| Pattern | Meaning |
|---|---|
| `<Name>__dll` | DLO API name suffix; for example a UDLO named `X` is queried as `X__dll` [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-azure-udlo.html). DLO names: alphanumerics and underscores, start with a letter, no trailing or double underscore, ≤ 40 characters [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_lake_object_naming.htm&release=264.0.0&type=5) |
| `<Name>__dlm` | DMO API name suffix, for example `ssot__Individual__dlm` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5) |
| `ssot__` | Standard (legacy) DMOs and fields in the default data space; the `std__…Dmo__dlm` set and custom-field forms are in [sql-cookbook.md](sql-cookbook.md) "Names" |
| `{prefix}_…` | Other data spaces: a 1–3 character prefix fixed at creation, for example `DS1_Individual_dlm` in the doc sample [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_spaces_create.htm&release=264.0.0&type=5) |
| `__cio` | Calculated insight objects ([sql-cookbook.md](sql-cookbook.md) Q6) |

### Data spaces

- Every org has a **default** data space; more spaces segregate brands, regions or departments and need the Data Spaces add-on license [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_spaces_create.htm&release=264.0.0&type=5).
- A DLO can be added to several data spaces, with or without filters [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_data_lake_objects_to_a_data_space.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_filters_to_a_data_object.htm&release=264.0.0&type=5).
- SP: a personalization point belongs to exactly one data space, and its profile data graph must live there ([decisioning.md](decisioning.md) §1.1). Rulesets and data graphs are created in a data space [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_graph_data_structures.htm&release=264.0.0&type=5).

## Identity data model

### Objects and required relationships

| DMO (default data space) | Key fields | Required relationship |
|---|---|---|
| Individual `ssot__Individual__dlm` | `ssot__Id__c` (PK), `ssot__FirstName__c`, `ssot__LastName__c` | 1:N to every contact point and Party Identification |
| Party Identification `ssot__PartyIdentification__dlm` | `ssot__Id__c` (PK), `ssot__Name__c`, `ssot__IdentificationNumber__c`, `ssot__PartyId__c`, `ssot__PartyIdentificationTypeId__c` | Party → Individual.Id (N:1) |
| Contact Point Email `ssot__ContactPointEmail__dlm` | `ssot__Id__c`, `ssot__PartyId__c`, `ssot__EmailAddress__c` | Party → Individual.Id |
| Contact Point Phone `ssot__ContactPointPhone__dlm` | `ssot__Id__c`, `ssot__FormattedE164PhoneNumber__c`, `ssot__PartyId__c` | Party → Individual.Id |
| Contact Point Address `ssot__ContactPointAddress__dlm` | `ssot__Id__c`, `ssot__AddressLine1__c`, `ssot__CityId__c`, `ssot__PartyId__c`, `ssot__PostalCodeId__c`, `ssot__StateProvinceId__c` | Party → Individual.Id |
| Contact Point App `ssot__ContactPointApp__dlm` | `ssot__Id__c` | Party → Individual.Id |

Source: [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5). Contact Point OTT Service and Contact Point Social follow the same Party → Individual N:1 pattern; Contact Point Digital Id links through `IndividualId` instead [src](https://help.salesforce.com/s/articleView?id=data.c360_a_required_data_mappings.htm&release=264.0.0&type=5).

- Standard bundles set these mappings and relationships automatically; **custom streams must set them**, and identity resolution needs the Individual plus at least one contact point or Party Identification mapped [src](https://help.salesforce.com/s/articleView?id=data.c360_a_required_data_mappings.htm&release=264.0.0&type=5). A contact point or Party Identification row without a Party that resolves to an Individual can't take part in matching (inference).
- "Party" is the foreign key to the Individual (or Account); Party Identification needs ID, Party, Type, Number and Name mapped before it can be used [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5).
- Individual also carries `ssot__IsAnonymous__c` (text) and `ssot__LastModifiedDate__c` [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-individual-dmo.html); the first decides known vs anonymous counts, the second enables `Last Updated` reconciliation (§ Reconciliation rules).
- Field-name casing differs between pages (`ssot__IdentificationNumber__c` here vs `ssot__Identificationnumber__c` on the DMO reference); see [sql-cookbook.md](sql-cookbook.md) "Names".

### How web and mobile identity events land

| SDK profile event | DMO | Mapping (Web SDK connector tables) |
|---|---|---|
| `identity` | Individual | `deviceId` → Individual Id (PK), `dateTime` → Created Date, `firstName`, `lastName`, `isAnonymous` → Is Anonymous |
| `partyIdentification` | Party Identification | `userId` → Identification Number, `IDType` → Party Identification Type, `IDName` → Identification Name, `deviceId` → Party Identification Id |
| `contactPointEmail` | Contact Point Email | `deviceId` → Contact Point Email Id (PK), `email` → Email Address |
| `contactPointPhone` | Contact Point Phone | `deviceId` → Contact Point Phone ID (PK), `phone`, `phoneCountryCode` |
| (address fields) | Contact Point Address | `deviceId` → PK, `city`, `addressLine1`, `stateProvince`, `country`, `postalCode` |

Source: [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-web-connector-data-mappings.html).

- The SP guide's mapping differs from the Data 360 table [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html):
  - it maps `deviceId` → **Party** as well as the primary key on Party Identification, Contact Point Email and Contact Point Phone; the Data 360 table has no Party rows, yet identity resolution requires Party → Individual on each [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5). Follow the SP guide.
  - it says to leave the Contact Point Address DLO unmapped;
  - it maps `phoneNumber` → Telephone Number (the SDK translation table also uses `phoneNumber` [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html)) where the Data 360 table shows `phone` → Phone Number, and adds `userName` → External Record ID and `dateTime` → Created Date on the profile objects. Use the field names in your uploaded schema.
- Because profile objects are keyed on `deviceId`, each browser or app install is one source Individual with at most one row per profile object; a new email from the same device overwrites the previous one under Partial refresh (inference from the primary key).
- Mobile: the Engagement Mobile SDK sends the same profile event families through the mobile app connector ([mobile-and-channels.md](mobile-and-channels.md) §1.9).
- Automatic anonymous `identity` event, `isAnonymous` conventions and payload rules: [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §4.

## Identity resolution rulesets

### Ruleset setup and limits

1. **Identity Resolutions** tab → **New** → data space → primary DMO (Individual, Account, Lead or household; households need an Individual ruleset run first) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).
2. Optional **ruleset ID** of up to four characters: permanent, appended to every generated DMO name; with two rulesets on one object, at least one needs an ID. Note the generated DMO names before saving [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).
3. For Individual rulesets you can link all individuals that share the same individual ID and key qualifier [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).
4. Add match rules and reconciliation rules; optional filters on the primary DMO gate which source records enter [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).

- Permission: `Data Cloud Architect`. Disable `Run jobs automatically` while configuring and use **Run Now**; keep one active ruleset to reduce cost [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).
- Optional filter conditions on primary-DMO fields gate which source records enter matching [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5); without them a ruleset takes every source record of its primary DMO in its data space, with no per-stream "connect" step (inference). Every ruleset keeps at least one match rule (same src).
- Hard limits (5 rulesets per primary DMO and data space, 10 rules of 10 criteria, scheduled once a day, 15 KB record size, 50,000 source profiles and 75 identifiers per unified profile) and billable full-rerun triggers: [field-guide-data.md](field-guide-data.md) §1.2–§1.3 [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).

### Match rules

- Criteria inside a rule combine with **AND** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset.htm&release=264.0.0&type=5); rules in a ruleset give "multiple ways for records to match", so they act as **OR** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_rules_individuals.htm&release=264.0.0&type=5).
- **Default rules for Individuals** (all use `Individual - First Name` Fuzzy Medium + `Last Name` Exact): **Fuzzy Name and Normalized Email**, **…Phone**, **…Address** (Address Line 1 and Country Exact Normalized, City Exact), **…Phone and Normalized Email**. Records with the same `Individual.Id` match even without a rule (same src). None of the default rules can match anonymous web Individuals that carry no names (inference).
- **Custom rules** can use Party Identification (party identifier), the Identity Match object (external identity link), cross-object criteria [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5), and Device Advertiser ID [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_rules_individuals.htm&release=264.0.0&type=5). Matching on a single contact point is discouraged, except for unique external identifiers such as a party identifier [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5). SP's documented real-time rule is Party Identification / Identification Number / `Exact`, Match on Blank off, with the Party Identification Type and Name values [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5).
- A party identifier matches only when Identification Number, Identification Name and Party Identification Type are all identical; Match on Blank isn't allowed [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5).

### Match methods

| Method | Behavior |
|---|---|
| Exact | All objects and fields; same value **regardless of case** (`Maryanne` = `MARYANNE`) unless Case Sensitive is set |
| Exact Normalized | Specific Contact Point Email, Phone and Address fields (the page's table also lists Individual First Name); fixes case, white space, formatting and special characters (Gmail dots and `+` removed; phones parsed with libphonenumber). Usually higher consolidation than Exact |
| Fuzzy – High Precision | Nicknames, punctuation, international characters, cross-cultural spellings (William/Bill, Håkon/Hakon) |
| Fuzzy – Medium Precision | Initials, gender variants, shuffled names, sub-names (S./Sharon, Gabriel/Gabrielle) |
| Fuzzy – Low Precision | Loose similarity (Lisa/Liza, Lucia/Luc) |

Source: [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_criteria_fuzzy_normalized.htm&release=264.0.0&type=5). Fuzzy methods use a BERT-based model with a 0.7 confidence threshold and aren't available on Account fields. Normalized or fuzzy forms are used only for comparison; unified profiles store source values chosen by reconciliation (same src).

### Advanced criteria settings

- **Case Sensitive:** opt-in; without it upper and lower case match. A separate ruleset-level option, set at creation, links records only when Individual ID and fully qualified key match case-sensitively. **Match on Blank:** matches two blanks, over-merges sparse fields and is ignored in real time [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5). Docs disagree on scope: Help presents Case Sensitive as a general criterion setting, while the Apex API says `caseSensitiveMatch` is "available only when matching is based on the party identifier" [src](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_connectapi_input_cdp_identity_resolution_match_criteri.htm).
- **Cross-object "Match to":** one documented sentence ("the object you want to match to must be modeled properly") [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5). Field behavior and the recommendation to leave it empty on party-identifier criteria: [field-guide-data.md](field-guide-data.md) §1.1.

### Real-time matching, schedule and triggers

- Real-time runs every criterion as Exact or Exact Normalized regardless of the configured method, ignore Match on Blank, and the data is re-unified in the next scheduled run [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_real_time.htm&release=264.0.0&type=5). Only email and phone use Exact Normalized; all other fields are Exact. An input that isn't an exact match returns no profile. The real-time graph receives scheduled-run unified profiles once a day, and reconciliation rules are the same in all modes [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_type_compare.htm&release=264.0.0&type=5).
- Real-time unification needs an **Individual-based** ruleset whose output Unified Individual is the basis of a **real-time data graph** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_realtime.htm&release=264.0.0&type=5), created after the ruleset's first run completes [src](https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5). The docs describe no other real-time switch on the ruleset (inference).
- Scheduled processing: every 60 minutes to 24 hours depending on source; up to 18 hours after initial ingestion, a full refresh or a batch over 1 million records; streaming connectors after 1 hour or 500 changes; Web SDK real-time data immediately. Batch and federated records are hashed first, so unchanged records aren't rerun even after a full refresh [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_processing_frequency.htm&release=264.0.0&type=5). Rulesets run at least once a day after publication [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5).

### Outputs and naming

| Ruleset ID | Unified objects | Link objects |
|---|---|---|
| blank | `UnifiedIndividual__dlm`, `UnifiedContactPointEmail__dlm`, `…Phone`, `…Address`, `…App`, `UnifiedPartyIdentification__dlm` | `IndividualIdentityLink__dlm`, `ContactPointEmailIdentityLink__dlm`, `…Phone…`, `…Address…`, `…App…`, `PartyIdentificationIdentityLink__dlm` |
| `Test` (example) | `UnifiedssotIndividualTest__dlm`, `UnifiedssotContactPointPhoneTest__dlm`, … | `UnifiedLinkIndividualTest__dlm`, `UnifiedLinkContactPointEmailTest__dlm`, … |

Source: [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5).

- Every link object has `SourceRecordId__c` (source record Id), `UnifiedRecordId__c` (unified Id), `ssot__DataSourceId__c`, `ssot__DataSourceObjectId__c`, `CreatedDate__c`, `ssot__InternalOrganizationId__c`, plus any key qualifier fields; unified and link objects are 1:1 related (same src).
- Account rulesets produce `UnifiedLinkssotAccount__dlm` (same src). The doc's `Test` example is internally inconsistent (`UnifiedContactPointEmailTest__dlm` without `ssot`, `UnifiedLinkPartyIdentificationFzzy__dlm`), so copy real names from the Data Model tab.

### Consolidation rate

- Consolidation rate = `(1 − unified profiles / source records) × 100`, per data source in the documented calculated insight on the link object; sources with many duplicates consolidate more, and an unexpectedly high rate can signal source quality issues [src](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ci_consolidation_rate.htm&release=264.0.0&type=5).
- The ruleset summary shows the rate for the last successful run; compare rulesets on it [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5). Check it against what you know about source cleanliness, and spot-check unified profiles in Profile Explorer [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_optimize.htm&release=264.0.0&type=5).
- For personalization, read it per source: a device-keyed web source should consolidate strongly once sign-ins unify, while a clean CRM source stays low (inference). A web source at 0% after sign-ins points at the identifier contract, not the rule method.
- Known vs anonymous: a unified profile with any known source is known; one built only from anonymous sources is anonymous; Account profiles are always known [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_summary_anonymous_vs_known_profiles.htm&release=264.0.0&type=5). A source without Is Anonymous mapped always counts as known, and `0`, `No`, `N`, `F`, `False` or empty also count as known [src](https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5). An anonymous count of 0 with web data present therefore means Is Anonymous isn't mapped on the web Individual stream or arrives with a known-style value (inference).

## Reconciliation rules

- A reconciliation rule picks one value for a unified field that can't hold several (a name, a flag). Set a **default rule per object**, then **override per field**. It never changes source data or source systems [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_setfieldspecific.htm&release=264.0.0&type=5).

| Rule | Exactly what it does |
|---|---|
| Last Updated | Value from the most recently updated record, by the primary DMO's **Last Modified Date**; available **only when Last Modified Date is mapped** from the stream; ties are broken alphabetically |
| Most Frequent | Most frequent value; with Ignore Empty Values, null is never chosen even if most frequent; ties go to the last updated value |
| Source Priority | Ranks DLOs from most to least preferred; with Ignore Empty Values, the highest-priority non-null value wins; recommended for ID fields; when records from the same source match, field-level rules apply, and source-priority-on-source-priority falls back to last updated |

Source: [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5).

- **Ignore Empty Values** is optional and is **ignored for key fields** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_setdefault.htm&release=264.0.0&type=5). Reconciliation warnings (for example "Select a supported reconciliation rule for ID fields") don't block runs [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_warnings.htm&release=264.0.0&type=5).
- No documented default rule is named; read each object's rule on the ruleset page rather than assuming one (UNVERIFIED).
- **Not reconciled:** contact points (email, phone…). All of them stay on the unified profile; use source priority in activations instead [src](https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5).
- **Web prerequisite:** the web `identity` mapping sends `dateTime` to Individual **Created Date**, not Last Modified Date [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-web-connector-data-mappings.html), so `Last Updated` isn't available on that source unless you map a modified-date field (inference). Changing reconciliation rules triggers a billable full rerun ([field-guide-data.md](field-guide-data.md) §1.3).

### Effect on SP targeting

- A profile data graph rooted on Unified Individual exposes the **reconciled** unified fields at the root; targeting rules and merge fields on root attributes read those values (inference from [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5)).
- Child nodes under the root (source Individuals through Unified Link Individual, as in the documented graph example [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_graph_data_structures.htm&release=264.0.0&type=5); Party Identification, contact points, engagement) keep **per-source rows**, so `Related Attributes` conditions see every source's value, not the reconciled one (inference). Merge fields document the same split: direct attributes are single root values, related attributes are multi-valued and need a sort [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5).
- Consequences: a web source with higher priority or a later update can overwrite a CRM name or flag at the root; put web sources lowest and turn on Ignore Empty Values for names ([field-guide-data.md](field-guide-data.md) §1.4). Contact-point-based conditions must be written as related-attribute conditions because no single value is reconciled (inference).

## Data graphs for personalization

- **Types:** near real-time (standard) and real-time. Builder: App Launcher → **Data Graphs** → **New** → **Start from Scratch**; permission `Data Cloud Architect` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5).
- **Primary DMO** decides which related objects are reachable; primary key, key qualifier and foreign keys are pre-selected [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5). Any category except Engagement can be primary; related objects can be Profile, Other or Engagement; the result is one flattened, read-only JSON record per root [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_graph_data_structures.htm&release=264.0.0&type=5). The root key is the primary DMO's primary key [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_remove_root_key_ind.htm&release=264.0.0&type=5).
- **SP choice:** Unified Individual for real-time identity resolution [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5) (that page also says the profile graph "must be" real-time, while the point-level pages allow standard graphs for outbound and batch: [decisioning.md](decisioning.md) §1.2); recommender graphs need a Unified Individual, Individual or Account primary DMO [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_recommender_considerations.htm&release=264.0.0&type=5).
- **Relationships:** real-time graphs join only through the **parent's primary key** [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5) and allow only 1:1 and 1:N; N:1 is blocked in new or edited real-time graphs, while older N:1 graphs keep running with delayed parent updates. Standard graphs support N:1 [src](https://help.salesforce.com/s/articleView?id=data.c360_a_dg_n1_restriction.htm&release=264.0.0&type=5). Relate profile-extension data to Individual or Unified Individual by their primary key ([decisioning.md](decisioning.md) §1.3).
- **Calculated insights** join a graph only when built on a DMO in the graph, with its primary key as a dimension, at the root [src](https://help.salesforce.com/s/articleView?id=data.c360_a_add_calculated_insights_to_a_data_graph.htm&release=264.0.0&type=5).
- **Refresh:** standard graphs offer Every 30 Minutes, 1 Hour, 4 Hours, Daily (default), Weekly, Monthly or Streaming (no N:1, no ad hoc filters); real-time graphs update continuously; builds take 15 minutes to several hours [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5). The lakehouse copy of a real-time graph refreshes hourly; the limits page's standard list omits the 1-hour option [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5). SP's quick start prescribes a 30-minute interval [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_create_required_data_graphs.htm&release=264.0.0&type=5).
- **Editing:** fields and objects can be removed only in draft; otherwise only added [src](https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5). **Preview** shows the JSON structure [src](https://help.salesforce.com/s/articleView?id=data.c360_a_view_data_graph_metadata.htm&release=264.0.0&type=5).
- **Limits** (25 standard and 25 real-time graphs per org, 25 objects, 50 fields per DMO, 200 fields plus measures, 5 nesting levels, 1,000 records per DMO with a default of 100, 30-day engagement window, 100 million JSON records for real-time, performance degrading above 200 KB per real-time graph): [decisioning.md](decisioning.md) §1.6 [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5).
- **Record caching and sessions (real-time):** consumption limits set at creation. Caching keeps recently active known visitors in the real-time layer; if disabled, a known visitor's first page may not personalize while the profile loads from the lakehouse, and sub-second real-time profile entitlements aren't consumed. Session length: 30 minutes is the industry standard, 48 hours the maximum, and traffic spikes can end sessions early [src](https://help.salesforce.com/s/articleView?id=data.c360_a_record_caching_in_rt_data_graphs.htm&release=264.0.0&type=5). No default for caching is documented; check it on each graph. Session extension can delay lakehouse updates reaching an active visitor [src](https://help.salesforce.com/s/articleView?id=data.c360_a_sess_ext_data_graphs.htm&release=264.0.0&type=5).
- **How SP uses them:** a point is built on one profile data graph; real-time graphs get a live profile lookup, standard graphs evaluate only the JSON the caller sends (otherwise a blank anonymous profile), and WPM lists only real-time points [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5). Depth: [decisioning.md](decisioning.md) §1.

## QA checklist and queries

Run in Query Editor in the right data space [src](https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor.htm&release=264.0.0&type=5). Default data space names; swap the link and unified DMOs for your ruleset (§ Outputs). Run each statement separately, and never paste results containing identifiers into tickets.

| Stage | Check | Pass means |
|---|---|---|
| 1. Stream landed | Stream refresh history, then QA1 | Rows added in the test window; DLO count moves |
| 2. Mapping correct | QA2, QA3 | DMO count close to DLO count; no nulls in PK / Party / Number / Name |
| 3. Identity rows present | QA3, QA4 (this file), Q10a in [sql-cookbook.md](sql-cookbook.md) | Name/Type pairs equal the rule's values on both sides; every row has an Individual |
| 4. Unification happened | QA5, QA6, acceptance test in [field-guide-data.md](field-guide-data.md) §4 | Unified count moved; web and non-web sources share unified IDs; decoys stay separate |
| 5. Reconciliation outcome | QA7 | Root values for a known test profile follow the configured rule |
| 6. Graph record | Data Explorer, Query API lookup | The test profile's graph JSON holds the fields targeting needs |

**QA1. DLO row count** — `doc-derived (untested)`
```sql
SELECT COUNT(*) AS dlo_rows
FROM <DLO_API_NAME>__dll
```
- `<DLO_API_NAME>` is the object API name without the suffix, copied from the Data Lake Objects tab; Data 360 appends `__dll` for queries [src](https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-azure-udlo.html).

**QA2. Individual rows, anonymous flag and blanks per source** — `doc-derived (untested)`
```sql
SELECT i.ssot__DataSourceId__c AS data_source,
       i.ssot__IsAnonymous__c AS is_anonymous,
       COUNT(*) AS individuals,
       SUM(CASE WHEN i.ssot__FirstName__c IS NULL THEN 1 ELSE 0 END) AS blank_first_name,
       SUM(CASE WHEN i.ssot__LastModifiedDate__c IS NULL THEN 1 ELSE 0 END) AS no_last_modified
FROM ssot__Individual__dlm i
GROUP BY 1, 2
ORDER BY 3 DESC
```
- Field names from the Individual DMO reference [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-individual-dmo.html). `no_last_modified` equal to the row count means `Last Updated` reconciliation can't use that source.

**QA3. Party Identification key-field nulls per source** — `doc-derived (untested)`
```sql
SELECT pi.ssot__DataSourceId__c AS data_source,
       COUNT(*) AS rows_total,
       COUNT(DISTINCT pi.ssot__Id__c) AS distinct_pk,
       SUM(CASE WHEN pi.ssot__PartyId__c IS NULL THEN 1 ELSE 0 END) AS no_party,
       SUM(CASE WHEN pi.ssot__IdentificationNumber__c IS NULL THEN 1 ELSE 0 END) AS no_number,
       SUM(CASE WHEN pi.ssot__Name__c IS NULL OR pi.ssot__PartyIdentificationTypeId__c IS NULL THEN 1 ELSE 0 END) AS no_name_or_type
FROM ssot__PartyIdentification__dlm pi
GROUP BY 1
```
- Field names from the identity modeling page [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5). Name/Type pairs per source: [field-guide-data.md](field-guide-data.md) §4 (field-verified).

**QA4. Orphan identity rows and identifier formats** — `doc-derived (untested)`
```sql
SELECT pi.ssot__DataSourceId__c AS data_source,
       LENGTH(pi.ssot__IdentificationNumber__c) AS id_length,
       COUNT(*) AS rows_total,
       SUM(CASE WHEN i.ssot__Id__c IS NULL THEN 1 ELSE 0 END) AS rows_without_individual
FROM ssot__PartyIdentification__dlm pi
LEFT JOIN ssot__Individual__dlm i
  ON pi.ssot__PartyId__c = i.ssot__Id__c
WHERE pi.ssot__Name__c = '<ID_NAME>'
  AND pi.ssot__PartyIdentificationTypeId__c = '<ID_TYPE>'
GROUP BY 1, 2
ORDER BY 1, 2
```
- Different length clusters per source for one Name/Type pair mean the sources send different formats, which Exact never matches. With key qualifiers configured, add them to the join [src](https://help.salesforce.com/s/articleView?id=data.c360_a_fully_qualified_keys.htm&release=264.0.0&type=5).

**QA5. Unification and consolidation per source** — `doc-derived (untested)`
```sql
SELECT l.ssot__DataSourceId__c AS data_source,
       l.ssot__DataSourceObjectId__c AS data_source_object,
       COUNT(l.SourceRecordId__c) AS source_records,
       COUNT(DISTINCT l.UnifiedRecordId__c) AS unified_profiles,
       100.0 * (1 - COUNT(DISTINCT l.UnifiedRecordId__c) * 1.0 / COUNT(l.SourceRecordId__c)) AS consolidation_pct
FROM IndividualIdentityLink__dlm l
GROUP BY 1, 2
```
- Query Editor form of the documented consolidation insight, which groups by data source and data source object and uses `APPROX_COUNT_DISTINCT` [src](https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ci_consolidation_rate.htm&release=264.0.0&type=5). Total unified profiles: `SELECT COUNT(*) FROM UnifiedIndividual__dlm`. Largest profiles: [sql-cookbook.md](sql-cookbook.md) Q10c.

**QA6. Every source linked to one test profile** — `doc-derived (untested)`
```sql
SELECT l.UnifiedRecordId__c AS unified_individual,
       l.ssot__DataSourceId__c AS data_source,
       l.SourceRecordId__c AS source_individual
FROM IndividualIdentityLink__dlm l
WHERE l.UnifiedRecordId__c IN (
  SELECT UnifiedRecordId__c FROM IndividualIdentityLink__dlm
  WHERE SourceRecordId__c = '<TEST_SOURCE_ID>')
ORDER BY 2
```
- `<TEST_SOURCE_ID>` is a test device ID (`getAnonymousId()`) or a CRM Individual ID. Only one row means the test device isn't unified yet; re-run after the next ruleset run.

**QA7. Reconciled root vs source values for the test profile** — `doc-derived (untested)`
```sql
SELECT l.ssot__DataSourceId__c AS data_source,
       i.ssot__FirstName__c AS source_first_name,
       i.ssot__IsAnonymous__c AS source_is_anonymous,
       i.ssot__LastModifiedDate__c AS source_last_modified,
       u.ssot__FirstName__c AS unified_first_name,
       u.ssot__IsAnonymous__c AS unified_is_anonymous
FROM IndividualIdentityLink__dlm l
JOIN ssot__Individual__dlm i ON l.SourceRecordId__c = i.ssot__Id__c
JOIN UnifiedIndividual__dlm u ON l.UnifiedRecordId__c = u.ssot__Id__c
WHERE l.UnifiedRecordId__c IN (
  SELECT UnifiedRecordId__c FROM IndividualIdentityLink__dlm
  WHERE SourceRecordId__c = '<TEST_SOURCE_ID>')
```
- Both joins follow the documented CI pattern (source Id → `SourceRecordId__c`, `UnifiedRecordId__c` → `UnifiedIndividual__dlm.ssot__Id__c`) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5); unified field names mirroring `ssot__FirstName__c` / `ssot__IsAnonymous__c` are UNVERIFIED, so confirm them in the Data Model tab. If sources share Individual Id values, add key qualifiers to the Individual join (inference).
- Expected: the unified value equals the value the configured rule selects (highest-priority non-null source, latest modified, or most frequent). Contact points aren't reconciled; list them from `ContactPointEmailIdentityLink__dlm` by `UnifiedRecordId__c`.

**Data graph record check**
- Data Explorer → object type Data Graph → the graph → view the JSON; set **Real-time View: On** to read real-time instead of cached data [src](https://help.salesforce.com/s/articleView?id=data.c360_a_view_your_data.htm&release=264.0.0&type=5).
- Query API lookup by source ID: `GET /api/v1/dataGraph/{name}?lookupKeys=[<LINK_DMO>__dlm.SourceRecordId__c=<TEST_SOURCE_ID>]`, adding `live=true` for the latest data instead of the precalculated record; real-time graphs accept only primary-key and key-qualifier lookups [src](https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/c360a-api-v1-data-graphs-lookup.html).
- End-to-end: call the point with `TestMode` and `context.individualId` ([field-guide-data.md](field-guide-data.md) §3).

## Field-observed lessons

- **Triage by layer.** If a value is right in the browser payload but blank in the DMO, the mapping is at fault; if the row is missing from the DLO too, the stream (event not selected, schema not synced) or the payload is at fault. Check the DLO before debugging the sitemap (Field-observed, undocumented).
- **Profile streams keyed on device are idempotent.** Repeated page loads upsert one Individual and one Party Identification row per device, so row counts track devices, not visits. Several Individual rows per person are the designed outcome when devices rotate on logout (Field-observed; consistent with the `deviceId` primary key [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html)).
- **Confirm the qualifiers were saved.** On a Party Identification criterion, the Advanced Settings row showed an "Applied" indicator once Name and Type were saved; check it before spending a run (Field-observed, undocumented).
- **One person, several identifier formats.** Sources can carry the same identifier with and without a check digit, padding or prefix. Exact compares strings, so they never meet. **Do:** pick one canonical form, fix it at the source or with a formula field, and run QA4 before the first full run (Field-observed).
- **Contact points need the Party mapping too.** The Data 360 Web SDK connector table lists only the primary key for web contact points, while identity resolution requires Party → Individual [src](https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5). **Do:** follow the SP guide, which maps `deviceId` → Party on web email and phone [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html), and check auto-mapped canvases for the missing row.
- **Record counts before and after every ruleset change.** Snapshot unified, known and anonymous counts plus QA5 per source, so a change can be attributed; a rising anonymous count with no mixed-source profiles means web identities aren't converting (Field-observed; [field-guide-data.md](field-guide-data.md) §1.3).
- **Graphs expose profile facts, not page context.** Current-page facts (page type, URL, UTM) come from request context in targeting rules, not from the graph ([decisioning.md](decisioning.md) §6.3) (Field-observed).

## Gaps and uncertainties

- "Data source object (DSO)" has no Help definition; it appears only as a field (`Data Source Object`) and in API payloads.
- No default reconciliation rule or default record-caching setting is documented.
- The Data 360 Web SDK mapping tables omit the Party foreign key on Party Identification and contact points and map Contact Point Address; the SP guide adds Party on Party Identification, email and phone and leaves address unmapped. Phone and party-name field names also differ between pages (`phone` vs `phoneNumber`; `IDName` vs `IDNameWeb`).
- The SDK translation table describes `isAnonymous` `0` as anonymous and `1` as known, the reverse of the ingestion rule (`0` = known); see [web-sdk-and-sitemap.md](web-sdk-and-sitemap.md) §4.
- Case Sensitive scope: general criterion setting in Help, party-identifier only in the Apex API.
- Exact Normalized scope: the text names contact point fields only, the table also lists Individual First Name.
- Unified Individual field API names and the `Test`-ruleset examples on the link-object page are inconsistent; confirm names in the Data Model tab.
- How the reconciled root and per-source child rows interact in targeting is inferred from graph structure, not stated.
- Whether Query Editor accepts `__dll` names for every stream-created DLO, and every query above, is untested (`doc-derived (untested)`).

## Sources

Data 360 Help — ingestion and modeling:
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_lake_objects.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_ingestion_and_modeling.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_category.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_edit_settings.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_stream_schedule.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_datastream_dlo_refresh_history.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_guardrails_existing_data_lake_object.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_formula_expression_library.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_map_custom_data_model_objects.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_automapping_dlo_dmo.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_model_object_relationships.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_segment_canvas_interface.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_fully_qualified_keys.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_lake_object_naming.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_spaces_create.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_add_data_lake_objects_to_a_data_space.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_add_filters_to_a_data_object.htm&release=264.0.0&type=5
Data 360 Help — identity resolution:
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_individual.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_required_data_mappings.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_partyidentifier.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset_create.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_ruleset.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_rules_individuals.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_configure.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_criteria_fuzzy_normalized.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_match_rules_advanced_settings.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_real_time.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_match_type_compare.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_unify_realtime.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_processing_frequency.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_data_modeling_unified_and_link_objects.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_resolution_troubleshooting_ci_consolidation_rate.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_optimize.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_identity_resolution_summary_anonymous_vs_known_profiles.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_ingestion_anonymous_vs_known_profiles.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_setdefault.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_setfieldspecific.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_reconciliation_rules_warnings.htm&release=264.0.0&type=5

Data 360 Help — graphs, insights, query:
- https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_data_graph_data_structures.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_add_remove_root_key_ind.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_dg_n1_restriction.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_add_calculated_insights_to_a_data_graph.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_edit_a_data_graph.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_view_data_graph_metadata.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_record_caching_in_rt_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_sess_ext_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_view_your_data.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_calculated_insights_aggregates.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_query_editor.htm&release=264.0.0&type=5

Data 360 developer docs:
- https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-individual-dmo.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-web-connector-data-mappings.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-mobile-web-datastream.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-perform-partial-update-on-record.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-azure-udlo.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-ingestion-api.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-connect-an-ingestion-source.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-ingestion-api-schema-req.html
- https://developer.salesforce.com/docs/data/data-cloud-int/guide/c360-a-create-ingestion-data-stream.html
- https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-translating-sdk-events-to-web-connector-schemas.html
- https://developer.salesforce.com/docs/data/data-cloud-query-guide/references/data-cloud-query-api-reference/c360a-api-v1-data-graphs-lookup.html
- https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_connectapi_input_cdp_identity_resolution_match_criteri.htm

SP Help and developer guide:
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/integrate-salesforce-interactions-sdk.html
- https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_recommender_considerations.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_create_required_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5

# Headless Decisions: Read, QA and Write Personalization Points Through the Connect API

## Scope

- Reading a personalization point's decisions as JSON, checking them, and creating or changing decisions without the decision wizard, through the Personalization Connect REST API.
- Reading the profile data graph record a decision evaluates, through the Data 360 Connect API (§8).
- Baseline: Connect REST API v67.0 and SP Help at release 264.0.0. Concepts (points, decisions, targeting rules, merge fields, priority) are in [decisioning.md](decisioning.md) §5–§6; this file covers only the API mechanics.
- Labels:
  - Documented facts carry `[src](url)`. The input schema in §3 comes from the API reference's published schema.
  - "(Field-verified)": a request run in a real org that produced the stated result.
  - "(Field-observed, undocumented)": seen in responses, absent from the docs.
  - "(UNVERIFIED)": not yet confirmed by a doc or a test. Re-test field results after every seasonal release.
- Placeholders: `<INSTANCE>`, `<POINT_API_NAME>`, `<DECISION_API_NAME>`, `<CONTENT_SCHEMA_NAME>`, `<PROFILE_DATA_GRAPH_NAME>`, `<ATTRIBUTE_NAME>`, `<CHILD_DMO>`, `<FIELD>`, `<LINK_DMO>` (identity link DMO), `<SOURCE_ID>`, `<UNIFIED_ID>`, `<RECORD>`, `<ORG_SESSION_OR_OAUTH_TOKEN>`. Names and IDs in the examples (`Homepage_Hero`, `Customer_Profile_RT`, `0f1e2d3c4b5a6978`) are fake.

## 1. When to use it

- **Review every decision at once.** One `GET` returns all decisions with their full rule trees, instead of opening each one in the wizard.
- **Bulk edits.** Change a value, a URL or a condition across many decisions in one request.
- **Clone.** Copy a decision to another point, or to a test point, with identical rules.
- **Backup and version control.** Keep the `GET` output in a repository and diff it before and after a change (inference: the JSON is complete enough to rebuild a decision, §4).

## 2. Endpoints and request basics

- **Resources** [src](https://developer.salesforce.com/docs/platform/connect-rest-api/references/connect-rest-api-personalization):

  | Method | Resource | Does |
  |---|---|---|
  | `POST` | `/personalization/personalization-points` | Creates a point |
  | `GET` | `/personalization/personalization-points/{idOrName}` | Reads a point and its decisions |
  | `PUT` | `/personalization/personalization-points/{idOrName}` | Updates a point, decisions included |
  | `DELETE` | `/personalization/personalization-points/{idOrName}` | Deletes a point |

- **URL:** `https://<INSTANCE>/services/data/v67.0` followed by the resource [src](https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_building_url.html). `{idOrName}` takes the record ID or the API name, so `<POINT_API_NAME>` works.
- **Version:** `targetingRules` on a decision input is available from v67.0, merge-field `fieldName`, `objectPath` and sort settings from v67.0, and `mergeFields` from v66.0 [src](https://developer.salesforce.com/docs/platform/connect-rest-api/references/connect-rest-api-personalization). Use v67.0 or later.
- **Decisions have no resource of their own.** They're read and written inside the point. `POST` on `/{idOrName}` returns `HTTP Method 'POST' not allowed. Allowed are DELETE,GET,HEAD,PUT` (Field-verified).
- **How `PUT` treats `decisions[]` (Field-verified):**
  - **Add:** send every existing decision plus the new one at the end. The new decision is created with a new `id` and the next priority.
  - **Update in place:** an existing decision sent back with the same `name` keeps its `id` and `createdDate`; only `lastModifiedDate` changes. Reporting tied to the decision ID survives the edit.
  - **No delete by omission:** a body that leaves out an existing decision is rejected as a whole with `You cannot update records for the PersonalizationPoint object.`, and nothing changes. Delete decisions in the UI.
  - **No rules:** a decision sent without `targetingRules` reads back as `targetingRules: null`, the `Always (No Rules)` form.
- **Read raw values.** Responses are minimally HTML entity-encoded by default, so `&` in a URL comes back as `&amp;`. Send `X-Chatter-Entity-Encoding: false` [src](https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_encoding.html). Writing an encoded value back would store the entity text (inference), so always read raw before you write.
- **Example request** (fake values; `Homepage_Hero` stands for `<POINT_API_NAME>`):

  ```http
  GET https://<INSTANCE>/services/data/v67.0/personalization/personalization-points/Homepage_Hero
  Authorization: Bearer <ORG_SESSION_OR_OAUTH_TOKEN>
  X-Chatter-Entity-Encoding: false
  ```

  The response is the point with `decisions[]`; each decision carries `name`, `state`, `targetingRules` and `attributeValues` (§4).
- **Auth and method override:** Connect REST API uses OAuth 2.0 over HTTPS. A client that can't send `PUT` can `POST` with `?_HttpMethod=PUT` [src](https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_architecture.html); the override is untested on personalization resources (UNVERIFIED).

## 3. Input schema (documented)

`PUT` and `POST` take a `PersonalizationPointInput` body [src](https://developer.salesforce.com/docs/platform/connect-rest-api/references/connect-rest-api-personalization):

| Object | Properties |
|---|---|
| `PersonalizationPointInput` | `name`, `label`, `description`, `dataSpaceName`, `profileDataGraphName`, `schemaName` or `schemaEnum` (not both), `source`, `isAuthenticationRequired`, `maxItemsCount`, `abnExperimentName`, `rootPersonalizationPointId`, `sourceRecordId`, `decisions[]` |
| `PersonalizationDecisionInput` | `name`, `label`, `description`, `personalizerName`, `state`, `targetingRules`, `attributeValues[]` |
| `PersonalizationAttributeValueInput` | `attributeName` or `attributeEnum` (not both), `value`, `mergeFields[]` |
| `PersonalizationMergeFieldInput` | `name`, `resourceType`, `objectName`, `fieldName`, `objectPath[]`, `sortByFieldName`, `sortOrder`, `defaultText` |
| `RuleGroup` | `type`, `operator`, `rules[]` |

- **Enums:**
  - `state`: `Draft`, `Live`.
  - Rule `type`: `CalculatedInsight`, `Field`, `Group`, `RelatedField`.
  - Group `operator`: `And`, `Or`.
  - Merge field `resourceType`: `CalculatedInsight`, `DirectAttribute`, `RelatedAttribute`, `SegmentMembershipsDmo`; `sortOrder`: `Ascending`, `Descending`.
  - `source`: `Agentforce`, `BlockBuilder`, `ExperienceBuilder`, `FlowBuilder`, `PersonalizationApp`, `PersonalizationCampaign`.
- **Constraints stated in the schema:**
  - Decision names must be unique within a point.
  - A decision-defined schema needs `personalizerName`, the recommender must be active, and its content schema must match the point's.
  - A decision with no targeting rules applies unconditionally, the same as `Always (No Rules)`.
  - An attribute value holds at most 20,000 characters, and attribute values must be unique within a decision.
  - Every merge-field handlebar reference in a value must match a declared merge field.
  - Direct-attribute merge fields need `objectName` and `fieldName`. Related-attribute and calculated-insight merge fields also need `objectPath`, `sortOrder` and `sortByFieldName`. Segment-membership merge fields take neither `objectName` nor `fieldName`.
  - `profileDataGraphName` is optional unless targeting rules reference profile attributes.
- **Not in the schema:** a priority field, and the properties of `Field` and `RelatedField` rules (the schema defines only their `type`). §4 fills that gap from field results.
- **Limits still apply:** 25 decisions per point, 50 targeting conditions per decision and 10 merge fields per decision [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5).

## 4. Rule tree and decision shape

- **Decision on read (Field-observed).** `GET` adds read-only keys to each decision: `id` (prefix `9pb`), `url`, `criteria`, and created and modified dates and user IDs. There's no priority field. `Always (No Rules)` reads as `targetingRules: null`.
- **Merge fields (Field-observed).** A value references a merge field as `{{{<MERGE_FIELD_NAME>}}}`, and `objectPath` runs from the graph root (empty for a direct attribute).
- **Rule nodes.** These shapes were written through `PUT` and rendered correctly in the decision wizard (Field-verified):

  | `type` | Keys on input |
  |---|---|
  | `Group` | `operator`, `rules[]` |
  | `Field` | `fieldName`, `predicate` |
  | `RelatedField` | `relatedObjectsPath[]`, `fieldName`, `aggregateFunction`, `predicate`, `preAggregationLogicalOperator`, `preAggregationRules[]` |

  - `predicate` is `{operator, type, values[]}`. Names seen, a partial list: Text `Equals`, `In`, `Contains`, `HasValue` (empty `values`); Number `GreaterThan`, `Equals`; Boolean `IsTrue`, `IsFalse` (no `values` key). Numbers travel as strings (`"0"`).
  - `aggregateFunction` values seen: `Count` on a top-level related condition, `AtLeastOne` on a condition nested in its `WHERE`.
  - The wizard's "Count · Is Greater Than · 0 · WHERE …" ([field-guide-data.md](field-guide-data.md) §3) is a `RelatedField` with `Count`, a `relatedObjectsPath` from the graph root, and the `WHERE` rows in `preAggregationRules`. Inside it, a `Field` tests the counted object, and a `RelatedField` with `AtLeastOne` tests one of its children, with a path relative to the counted object.
  - Each nested `AtLeastOne` condition is evaluated on its own, so two of them can be satisfied by different child rows (inference from the shape; [field-guide-data.md](field-guide-data.md) §3).
  - **Exclusion: "no child row where X".** A nested condition can't express it: `AtLeastOne` with a negative operator means "at least one row that isn't X", which any other row satisfies. Add a separate top-level `RelatedField` instead, with `aggregateFunction: Count`, the full `relatedObjectsPath` from the graph root down to the child, `fieldName` set to the child DMO's primary key, `predicate` Number `Equals` `["0"]`, and the X conditions in `preAggregationRules`. Written through `PUT`, it displays in the wizard as `Count` · `Is Equal To` · `0` · `WHERE …` (Field-verified). Whether it evaluates true for a profile with no matching rows is (UNVERIFIED).

```json
{ "type": "RelatedField", "aggregateFunction": "Count", "fieldName": "<CHILD_PRIMARY_KEY>__c",
  "relatedObjectsPath": ["IndividualIdentityLink__dlm", "ssot__Individual__dlm", "<PARENT_DMO>__dlm", "<CHILD_DMO>__dlm"],
  "predicate": { "operator": "Equals", "type": "Number", "values": ["0"] },
  "preAggregationLogicalOperator": "And",
  "preAggregationRules": [
    { "type": "Field", "fieldName": "<FIELD>__c",
      "predicate": { "operator": "In", "type": "Text", "values": ["<EXCLUDED_1>", "<EXCLUDED_2>"] } }
  ] }
```

  - The count runs over every row reachable from the root, so with a unified root it covers all source records linked to the person, not one parent record (inference).
- **Generic example.** The targeting from the wizard reads as: a direct attribute contains a value, and the person has at least one loyalty member with a tier in a list and a child row where a flag is false.

```json
{
  "type": "Group",
  "operator": "And",
  "rules": [
    { "type": "Field", "fieldName": "<FIELD>__c",
      "predicate": { "operator": "Contains", "type": "Text", "values": ["<VALUE>"] } },
    { "type": "RelatedField", "aggregateFunction": "Count", "fieldName": "ssot__Id__c",
      "relatedObjectsPath": ["IndividualIdentityLink__dlm", "ssot__Individual__dlm", "ssot__LoyaltyProgramMember__dlm"],
      "predicate": { "operator": "GreaterThan", "type": "Number", "values": ["0"] },
      "preAggregationLogicalOperator": "And",
      "preAggregationRules": [
        { "type": "RelatedField", "aggregateFunction": "AtLeastOne", "fieldName": "ssot__LoyaltyTierId__c",
          "relatedObjectsPath": ["ssot__LoyaltyMemberTier__dlm"], "preAggregationRules": [],
          "predicate": { "operator": "In", "type": "Text", "values": ["<TIER_1>", "<TIER_2>"] } },
        { "type": "RelatedField", "aggregateFunction": "AtLeastOne", "fieldName": "<FLAG>__c",
          "relatedObjectsPath": ["<CHILD_DMO>__dlm"], "preAggregationRules": [],
          "predicate": { "operator": "IsFalse", "type": "Boolean" } }
      ] }
  ]
}
```

## 5. Turn a GET response into a PUT body

The response isn't accepted as-is. These conversions were needed (Field-verified):

- **Remove `contextName`** from every rule. Input rejects it: `Unrecognized field "contextName"`.
- **Remove read-only keys** that aren't in the input schema (§3): `id`, `url`, `status`, `criteria`, `createdById`, `createdDate`, `lastModifiedById`, `lastModifiedDate`.
- **Drop `null` values.** The verified request carried none; whether `null` is rejected is (UNVERIFIED).
- **Read with `X-Chatter-Entity-Encoding: false`**, or decode `&amp;` and other entities before writing (§2).

A minimal converter for a raw `GET` response saved as `point.json`:

```python
import json, sys

READ_ONLY = {"id", "url", "status", "criteria", "contextName", "createdById",
             "createdDate", "lastModifiedById", "lastModifiedDate", "rootPersonalizationPointId"}

def clean(node):
    if isinstance(node, dict):
        return {k: clean(v) for k, v in node.items() if k not in READ_ONLY and v is not None}
    if isinstance(node, list):
        return [clean(v) for v in node]
    return node

json.dump(clean(json.load(open(sys.argv[1]))), sys.stdout, ensure_ascii=False, indent=2)
```

`rootPersonalizationPointId` is in the input schema for derived points; the verified request left it out. Keep it for a derived point (UNVERIFIED).

## 6. Safe workflow

1. **Practice on a test point.** Create an empty point with the same content schema and data graph. Copying one known-good decision into it in `Draft` proves the round trip without touching live traffic.
2. **Back up first.** Save a raw `GET` of the target point before every write.
3. **Send the whole point.** Build the body from the backup, change only what you mean to, and keep every existing decision in `decisions[]`, in its current order. Leaving one out rejects the whole request (§2).
4. **Write as `Draft`.** `Draft` decisions aren't evaluated [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5).
5. **Verify.**
   - Run `GET` again and diff it with the body you sent.
   - Open the decision in the wizard and check that every condition displays.
   - Check `Priority` in the point's `Personalization Decisions` list.
   - Read both test profiles' records (§8) and check that they hold the data the rules need.
   - Request the point with `executionFlags: ["TestMode"]` for a profile that should match and one that shouldn't. Test mode records no outputs to the data lake [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html). This is the Decisioning API on the tenant endpoint, not the Connect API, and its authenticated variant takes a Data 360 access token instead of the org session; endpoints and body fields are in [decisioning.md](decisioning.md) §5.3. Example body (fake values):

     ```json
     { "context": { "individualId": "0f1e2d3c4b5a6978" },
       "personalizationPoints": [ { "name": "Homepage_Hero" } ],
       "executionFlags": ["TestMode"] }
     ```

     On the page itself, `SalesforceInteractions.Personalization.fetch(["Homepage_Hero"])` requests the point for the current browser's profile.
6. **Go live.** Set `state` to `Live` in another `PUT`, or in the UI.

## 7. QA checklist for a point's decisions

Run it on the raw `GET` output before go-live and after every edit:

- At most one decision has `targetingRules: null`, and it has the lowest priority. A decision below a catch-all never serves, because decisions are evaluated in priority order [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5) (inference).
- Every decision meant to serve is `Live`.
- No value has leading or trailing whitespace, and no `Live` decision holds a placeholder (`Test`, sample URLs) or a diagnostic merge field ([field-guide-data.md](field-guide-data.md) §3).
- Each `{{{…}}}` token matches a merge field `name` on the same attribute, and `defaultText` is set wherever an empty value would break the content [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5).
- Every `relatedObjectsPath`, `objectPath` and `fieldName` exists in the point's profile data graph; only fields in the graph can be used for targeting [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5).
- A mistyped condition value saves without an error and never matches (Field-observed). Diff values across sibling decisions, and check the stored values with `SELECT <FIELD>__c, COUNT(*) FROM <DMO>__dlm GROUP BY <FIELD>__c` before writing an `In` list. If the excluded values plus the required one cover every stored value, the exclusion is equivalent to "every row is the required value".
- Decisions with similar names have the conditions their names imply.

## 8. Read the profile a decision sees (data graph lookup)

A decision's rules run against the visitor's record in the point's profile data graph. Reading that record as JSON shows which condition fails, without building a Flow (the Flow action is in [troubleshooting.md](troubleshooting.md), "A consent change or sign-in isn't reflected").

- **Resources** (Data 360 Connect API, documented from v59.0) [src](https://developer.salesforce.com/docs/data/connectapi/references/spec):

  | Method | Resource | Returns |
  |---|---|---|
  | `GET` | `/ssot/data-graphs/data/{dataGraphEntityName}?lookupKeys=[…]` | Records matching a lookup key |
  | `GET` | `/ssot/data-graphs/data/{dataGraphEntityName}/{id}` | The record whose root primary key is `{id}`; `live` (v63.0) toggles live lookup |
  | `GET` | `/ssot/data-graphs/metadata?dataGraphEntityName=<PROFILE_DATA_GRAPH_NAME>` | The graph definition |

- **URL and auth:** the same `https://<INSTANCE>/services/data/v67.0` base as §2, with the caller's own org session. No Data 360 tenant token is needed (Field-verified).
- **Lookup keys** [src](https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_ConnectAPI_CdpQuery_static_methods.htm):
  - The root's primary key, `[ssot__Id__c=<UNIFIED_ID>]`.
  - A source ID through the identity link DMO, `[<LINK_DMO>__dlm.SourceRecordId__c=<SOURCE_ID>]`. For the standard Individual graph `<LINK_DMO>` is `IndividualIdentityLink`; the graph metadata lists the exact name. A web device ID and a batch-loaded record ID both worked, sent with the brackets unencoded (Field-verified). If a client rejects the URL, encode it as `%5B…%3D…%5D`.
  - `dataspace` defaults to `default`.
- **Example requests** (fake values; `Customer_Profile_RT` stands for `<PROFILE_DATA_GRAPH_NAME>`, `0f1e2d3c4b5a6978` for a web device ID):

  ```http
  GET https://<INSTANCE>/services/data/v67.0/ssot/data-graphs/data/Customer_Profile_RT?lookupKeys=[IndividualIdentityLink__dlm.SourceRecordId__c=0f1e2d3c4b5a6978]
  GET https://<INSTANCE>/services/data/v67.0/ssot/data-graphs/data/Customer_Profile_RT?lookupKeys=[IndividualIdentityLink__dlm.SourceRecordId__c=0f1e2d3c4b5a6978]&noCache=true
  GET https://<INSTANCE>/services/data/v67.0/ssot/data-graphs/metadata?dataGraphEntityName=Customer_Profile_RT
  ```

  Send each with `Authorization: Bearer <ORG_SESSION_OR_OAUTH_TOKEN>`. The first reads the real-time copy, the second the standard copy, the third the graph definition.
- **Which copy answers:** by default the lookup reads the real-time graph and falls back to the standard graph if the real-time one is unavailable; `noCache=true` reads the standard copy [src](https://developer.salesforce.com/docs/data/connectapi/references/spec).
- **Response shape (Field-verified):**
  - A match returns `{"data":[{"json_blob__c":"<RECORD>"}],"done":true,"metadata":{}}`.
  - `json_blob__c` is the record as a JSON string, HTML entity-encoded (`&quot;`). Decode the entities, then parse the string. Whether `X-Chatter-Entity-Encoding: false` returns it raw is (UNVERIFIED).
  - No match returns `{"data":[],"done":true,"metadata":{}}`.
- **Metadata response (Field-verified):** each object with its fields, `dataType` and key flag (`keyCol`), the join fields between objects, and the graph's real-time settings (record caching, session length). Use it to pick the primary key for a `Count` condition (§4) and to check every `relatedObjectsPath`.

A decoder for a lookup response saved as `record.json`. It prints how many rows each path holds, so a missing node stands out:

```python
import html, json, sys
from collections import Counter

resp = json.load(open(sys.argv[1]))
counts = Counter()

def walk(node, path):
    for key, value in node.items():
        if isinstance(value, list):
            counts[path + key] += len(value)
            for row in value:
                walk(row, path + key + " > ")

for row in resp["data"]:
    record = json.loads(html.unescape(row["json_blob__c"]))
    print("root:", {k: v for k, v in record.items() if not isinstance(v, list)})
    walk(record, "")
for path, n in sorted(counts.items()):
    print(f"{n:5}  {path}")
```

The record holds personal data. Mask names, member numbers, device IDs and federated IDs before sharing it outside the project team.

**Reading the result (Field-observed):**

- **One lookup returns the whole person.** A device ID returns the unified record with links from every source. A link being present proves nothing: check what's nested under the link that should carry the business data.
- **Fresh sessions exist only in the real-time copy.** A device first seen today returned the real-time record, while `noCache=true` returned no match. The stored link DMO in Query Editor also lacked that device. The standard copy and the stored links pick a device up only after identity resolution and the next graph refresh. For a live web session, use the default lookup.
- **Child rows are capped.** A profile with more than 100 identity links returned 100 links plus the current device. That matches the documented default of 100 records per DMO, sorted by primary key and adjustable up to 1,000 [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limit_child_records_data_graph.htm&release=264.0.0&type=5). Links past the cap, and everything under them, are absent, so related-object rules can fail for heavily linked profiles (inference). Test identities reused across many browsers hit it first. Use a sort and limit or a condition on the link node, and test with identities that have few devices.
- **Diagnose "did not qualify."** Take the decision's rules from a `GET` of the point (§4) and walk them against the record:
  - Root `Field` conditions read the root's values.
  - Every `RelatedField` path must exist in the record, in the shape the rule expects.
  - `Count` counts the rows reachable along the path.

  Then confirm with the `TestMode` request in §6. If a condition fails only because data is missing from the record while the rows exist in Query Editor, the cause is in the graph or identity data, not the decision.

## Gaps and uncertainties

- Whether `PUT` matches existing decisions by `name` or by position in `decisions[]`. The verified update kept both the same, so keep the order when you edit (UNVERIFIED).
- Deleting a decision through the API: omission is rejected (§2), and no decision resource is documented.
- How priority is set through the API. The input has no priority field, and creation order sets the initial priority [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5). A decision appended at the end of `decisions[]` got the next priority (Field-verified). Whether reordering the array changes the priority of existing decisions is (UNVERIFIED); change priority in the UI.
- Keys of `CalculatedInsight` rules, `Or` groups below the root, and operators beyond the partial list in §4 are undocumented. Build one in the wizard, `GET` it, and copy the shape.
- Whether `Count` with `Equals 0` evaluates true for a profile with no related rows (UNVERIFIED).
- A data graph record can hold a link with nothing nested under it, while the source rows exist in the DMOs (Field-observed). In the case seen, the source record had no stored identity link, its ruleset runs ended with records skipped for exceeding the documented 15 KB size [src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5) ([field-guide-data.md](field-guide-data.md) §1), and it carried dozens of duplicate contact points because each load gave them new primary keys (Field-observed). That the skip produced the empty link is inference, and whether related contact points count toward the 15 KB is (UNVERIFIED). **Check:** the identity resolution run status for "skipped … greater than 15KB", and the contact point rows per source record. **Fix:** keep contact point primary keys stable across loads and remove the duplicates. Whether the record then links on the next run is (UNVERIFIED).
- Whether the decision engine reads the same record the lookup returns, including the fallback to the standard copy (inference; the docs describe the lookup, not the engine's read).

## Sources

Connect REST API:
- https://developer.salesforce.com/docs/platform/connect-rest-api/references/connect-rest-api-personalization
- https://developer.salesforce.com/docs/data/connectapi/references/spec
- https://developer.salesforce.com/docs/atlas.en-us.apexref.meta/apexref/apex_ConnectAPI_CdpQuery_static_methods.htm
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_building_url.html
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_encoding.html
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_architecture.html

SP Help and developer guide:
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html

Data 360 Help:
- https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=data.c360_a_limit_child_records_data_graph.htm&release=264.0.0&type=5

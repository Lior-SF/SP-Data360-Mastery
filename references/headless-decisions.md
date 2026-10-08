# Headless Decisions: Read, QA and Write Personalization Points Through the Connect API

## Scope

- Reading a personalization point's decisions as JSON, checking them, and creating or changing decisions without the decision wizard, through the Personalization Connect REST API.
- Baseline: Connect REST API v67.0 and SP Help at release 264.0.0. Concepts (points, decisions, targeting rules, merge fields, priority) are in [decisioning.md](decisioning.md) §5–§6; this file covers only the API mechanics.
- Labels:
  - Documented facts carry `[src](url)`. The input schema in §3 comes from the API reference's published schema.
  - "(Field-verified)": a request run in a real org that produced the stated result.
  - "(Field-observed, undocumented)": seen in responses, absent from the docs.
  - "(UNVERIFIED)": not yet confirmed by a doc or a test. Re-test field results after every seasonal release.
- Placeholders: `<INSTANCE>`, `<POINT_API_NAME>`, `<DECISION_API_NAME>`, `<CONTENT_SCHEMA_NAME>`, `<PROFILE_DATA_GRAPH_NAME>`, `<ATTRIBUTE_NAME>`, `<CHILD_DMO>`, `<FIELD>`.

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
- **Read raw values.** Responses are minimally HTML entity-encoded by default, so `&` in a URL comes back as `&amp;`. Send `X-Chatter-Entity-Encoding: false` [src](https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_encoding.html). Writing an encoded value back would store the entity text (inference), so always read raw before you write.
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

  - `predicate` is `{operator, type, values[]}`. Names seen, a partial list: Text `Equals`, `In`, `Contains`, `HasValue` (empty `values`); Number `GreaterThan`; Boolean `IsTrue`, `IsFalse` (no `values` key). Numbers travel as strings (`"0"`).
  - `aggregateFunction` values seen: `Count` on a top-level related condition, `AtLeastOne` on a condition nested in its `WHERE`.
  - The wizard's "Count · Is Greater Than · 0 · WHERE …" ([field-guide-data.md](field-guide-data.md) §3) is a `RelatedField` with `Count`, a `relatedObjectsPath` from the graph root, and the `WHERE` rows in `preAggregationRules`. Inside it, a `Field` tests the counted object, and a `RelatedField` with `AtLeastOne` tests one of its children, with a path relative to the counted object.
  - Each nested `AtLeastOne` condition is evaluated on its own, so two of them can be satisfied by different child rows (inference from the shape; [field-guide-data.md](field-guide-data.md) §3).
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
3. **Send the whole point.** Build the body from the backup, change only what you mean to, and keep every decision in `decisions[]`. Whether `PUT` replaces the list or merges it is (UNVERIFIED), so an omitted decision may be deleted.
4. **Write as `Draft`.** `Draft` decisions aren't evaluated [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5).
5. **Verify.**
   - Run `GET` again and diff it with the body you sent.
   - Open the decision in the wizard and check that every condition displays.
   - Check `Priority` in the point's `Personalization Decisions` list.
   - Request the point with `executionFlags: ["TestMode"]` for a profile that should match and one that shouldn't. Test mode records no outputs to the data lake [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html).
6. **Go live.** Set `state` to `Live` in another `PUT`, or in the UI.

## 7. QA checklist for a point's decisions

Run it on the raw `GET` output before go-live and after every edit:

- At most one decision has `targetingRules: null`, and it has the lowest priority. A decision below a catch-all never serves, because decisions are evaluated in priority order [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5) (inference).
- Every decision meant to serve is `Live`.
- No value has leading or trailing whitespace, and no `Live` decision holds a placeholder (`Test`, sample URLs) or a diagnostic merge field ([field-guide-data.md](field-guide-data.md) §3).
- Each `{{{…}}}` token matches a merge field `name` on the same attribute, and `defaultText` is set wherever an empty value would break the content [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5).
- Every `relatedObjectsPath`, `objectPath` and `fieldName` exists in the point's profile data graph; only fields in the graph can be used for targeting [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5).
- A mistyped condition value saves without an error and never matches (Field-observed). Diff values across sibling decisions.
- Decisions with similar names have the conditions their names imply.

## Gaps and uncertainties

- `PUT` on a point that already has decisions: replace or merge, and whether an existing decision keeps its `id` when it's sent back by `name`. Decision IDs appear in attribution data (inference), so compare `id` before and after the first write to a live point (UNVERIFIED).
- How priority is set through the API. The input has no priority field, and creation order sets the initial priority [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5). In one point read through `GET`, array order matched creation order; whether `decisions[]` order maps to priority on write is (UNVERIFIED).
- Keys of `CalculatedInsight` rules, `Or` groups below the root, and operators beyond the partial list in §4 are undocumented. Build one in the wizard, `GET` it, and copy the shape.
- Whether `Count` with `Equals 0` evaluates true for a profile with no related rows (UNVERIFIED).

## Sources

Connect REST API:
- https://developer.salesforce.com/docs/platform/connect-rest-api/references/connect-rest-api-personalization
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_building_url.html
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_encoding.html
- https://developer.salesforce.com/docs/platform/connect-rest-api/guide/intro_architecture.html

SP Help and developer guide:
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_add.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_point_decision_add_merge_fields.htm&release=264.0.0&type=5
- https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5
- https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html

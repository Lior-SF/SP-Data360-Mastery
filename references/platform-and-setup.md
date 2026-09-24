# SP Platform, Setup, Permissions and Data Model

## Scope
- Covers Salesforce Personalization (SP) positioning and architecture on Data 360, channels, editions/licenses/credits, renames, every documented SP permission, Data 360 prerequisites, the `Personalization Setup` page (all tabs), foundational / dashboard / attribution deployments, data kits, preconfigured use cases, default data graph assignment, the SP DMO catalog with API names, consent, limits, consumption, and the 260→264 feature timeline.
- Read before answering: "how do I set up SP", "which permission/permission set", "what does deploy X install", "which DMO / API name", "is this a documented limit", "why is targeting/consent failing", or any question where Marketing Cloud Personalization (MCP) knowledge could leak in.
- Baseline: help release 264.0.0 + current developer guides. Only 264 of the SP help is indexed, so older-release deltas come from release notes (260 = Spring '26 [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=262.0.0&type=5), 262 = Summer '26 [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_c360_truth.htm&release=262.0.0&type=5), 264 = Winter '27 [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_c360_truth.htm&release=264.0.0&type=5)).

## 1. What SP is and its architecture

### Positioning and packaging
- "Salesforce Personalization in Marketing Cloud Next is a Customer 360 application that uses Data 360 to provide personalized experiences across Salesforce clouds." [src](https://help.salesforce.com/s/articleView?id=mktg.mc_persnl.htm&release=264.0.0&type=5)
- Uses "objective-based (using ML), or rules-based content recommenders"; simple use cases can use rules to surface specific content assets. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics.htm&release=264.0.0&type=5)
- Delivered as (1) "A Customer 360 Personalization application that centralizes connected and personalized experiences across clouds" and (2) "Personalization as a Service that uses Data 360 to provide real-time personalization functionality to Salesforce customers across channels." [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_how_it_works.htm&release=264.0.0&type=5)
- Lives in the Salesforce org: setup spans Salesforce Setup, Data 360 Setup, and the Data 360 and Salesforce Personalization apps. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_assigning_permissions.htm&release=264.0.0&type=5)

### Data layer (Data 360)
- Data spaces are logical partitions; a data space contains data graphs built from DMOs; SP reads those graphs and uses its **own DMOs** for eligibility and content decisions. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_how_it_works.htm&release=264.0.0&type=5)
- Requires a profile data graph (eligibility) and an item data graph (recommender input); each is "a single, flattened, read-only data graph record". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5)
- Inputs: profile and item data graphs, calculated insights, segments, real-time behavioral data. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_cloud_and_einstein_personalization_learn_about.htm&release=264.0.0&type=5)

### Real-time data flow and decision pipeline
1. Web SDK interaction data is ingested simultaneously into the real-time layer and the standard data layer.
2. Identity resolution matches in real time; an unknown user gets a new profile.
3. The known/anonymous profile in the real-time data graph is updated with engagement and profile events.
4. Real-time insights and segments are calculated and written to the real-time profile data graph.
5. At decision time SP calls the Data 360 profile API for the updated profile. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_cloud_and_einstein_personalization_learn_about.htm&release=264.0.0&type=5)
- Pipeline for a point on a real-time profile data graph: request (point IDs + individual ID) → profile API → experiment/decision targeting → execute (Dynamic Content returns configured attribute text; Recommendations call the recommendation service with profile data graph + recommender ID) → return → log decision in Data 360. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5)

### Channels and entry points
| Channel | Mechanism | Notes |
| --- | --- | --- |
| Web | Salesforce Interactions SDK + Personalization module; namespace `SalesforceInteractions.Personalization`, calls the Decisioning API | Required for SP setup [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_websdk_ep_module.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-web-experiences.html) |
| Mobile, pro-code | Personalization module of the Engagement Mobile SDK + Data 360 module; `fetchDecisions` | Dec '25 (260) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_mobile_experiences.htm&release=260&type=5) |
| Mobile, low-code | "Salesforce Personalization module of the Marketing Cloud Unified Mobile SDK"; components and content zones registered in Data 360 Setup; iOS, Android, React Native, Flutter; QR-code preview | Aug '26 (264) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_mobile_lowcode.htm&release=264.0.0&type=5) |
| Server-side | `POST /personalization/decisions` (unauthenticated) or `POST /personalization/authenticated/decisions` (`Authorization: Bearer` Data Cloud access token) | [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-authenticated-request.html) |
| Batch | Batch Personalization on a Data 360 segment → output DMO → DMO activation (MCE, GCP, S3, Azure, SFTP) | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_create_batch_persnl.htm&release=264.0.0&type=5) |
| Salesforce apps | Flow invocable action `Get Personalization Decisions` ("available in Salesforce orgs with the Personalization license") | [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/get-personalization-decision-invocable-action-reference.html) |
| MC Next email / landing pages | Dynamic content variations = SP personalization points, decisions, targeting rules | [src](https://help.salesforce.com/s/articleView?id=mktg.mktg_content_personalization_ep.htm&release=264.0.0&type=5) |
| Agentforce | Agentforce for SP; Agentforce Adaptive Websites (Dec '25) | [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=260&type=5) |

### Editions, licenses, credits
- Editions (Lightning Experience): `Developer`, `Enterprise`, `Professional`, `Unlimited`; "requires an active Data 360 license". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_standard_editions_and_licenses.htm&release=264.0.0&type=5)
- Release-note "Where:" lines (260/262/264): "Professional, Enterprise, Unlimited, and Developer editions with the Salesforce Personalization add-on" [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_rt_setup_ui_updates.htm&release=260&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_preconfig_use_case_setup.htm&release=262.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_mobile_lowcode.htm&release=264.0.0&type=5); the 264 Data Visualization note says "with a Salesforce Personalization license" [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_data_viz_tab.htm&release=264.0.0&type=5).
- Contradiction: the Setup Guide banner reads "Available in: Salesforce **Enterprise** and **Unlimited** Editions with the Personalization Starter add-on." [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_d360_setup_for_personalization.htm&release=264.0.0&type=5)

| Aspect | Personalization License | Personalization Card |
| --- | --- | --- |
| Scope | Full-featured primary license, complete Personalization app | "consumption-based add-on or a limited, standalone license" |
| Primary use | High-volume real-time web and app | Adds credits to the full license, or as a standalone license unlocks SP in other Salesforce apps: Email Personalization in MC Advanced, cross-cloud (Sales, Service, Loyalty), Agentforce — not web/mobile |
| Included credits | 50 million | 1 million |
| Attribution models | 20 | 2 |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_standard_editions_and_licenses.htm&release=264.0.0&type=5)
- Channel test: the Personalization License "supports delivery across your website, mobile app, and other channels outside Salesforce clouds" (so an external contact-center app or backend calling the Decisioning API needs it; inference); the Card is "for personalization use cases other than web and mobile apps" inside Salesforce apps (MC Advanced email, Sales/Service/Loyalty Cloud, Agentforce), with 2 attribution models. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_standard_editions_and_licenses.htm&release=264.0.0&type=5)
- Card allows only "1 objective-based recommender" (limits page; the licenses page doesn't state it). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5) The licenses page describes the Card both as a standalone license and as extending "the capabilities of the full license by adding more credits". Add-on naming varies: "Personalization Starter add-on" (Setup Guide banner, above) vs "Salesforce Personalization add-on" (release notes). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_standard_editions_and_licenses.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_web_data_streams.htm&release=260&type=5)
- Billable usage type: `Personalization Decision`. `MCP+ (AMER)`, `MCP+ (APAC)`, `MCP+ (EMEA)`, `Salesforce Personalization`, `Salesforce Personalization Card` → Personalization Credits; `Salesforce Personalization (Flex)`, `MCP+ (AMER Flex)`, `MCP+ (APAC Flex)`, `MCP+ (EMEA Flex)` → Flex Credits; tracked in Digital Wallet. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_billable_usage_types.htm&release=264.0.0&type=5)

## 2. Terminology history and renames
| Old | Current | Evidence and residue |
| --- | --- | --- |
| Data Cloud | Data 360 | "As of October 14, 2025, Data Cloud has been rebranded to Data 360"; UI still shows `Data Cloud` (App Launcher item, `Data Cloud Setup`, `Data Cloud Salesforce Connector`, `Data Cloud Architect`) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_dc_releases.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_enable_data_360_deploy_persnl_data_kits.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_permission_set_update_data_cloud_connector_permissions.htm&release=264.0.0&type=5) |
| Response template | Content schema | "Content Schemas (previously called Response Templates)"; release not stated; API names unchanged: sObject `PersonalizationSchema`, DMO `PersonalizationSchema__dlm`, field `PersonalizationSchemaId__c` [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationSchema.htm) |
| Manual Content | Dynamic Content (personalization type) | "Dynamic Content (formerly called Manual Content)"; content is stored on the decision, not in Data 360; DMO docs still give `PersonalizationType__c` examples "Recommendations or Manual Content" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_content_schema_using.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html) |
| Einstein Personalization | Salesforce Personalization | No rename note in indexed docs (release UNVERIFIED); residue: dev guide slug `/docs/marketing/einstein-personalization/`, help IDs `persnl_setup_data_cloud_and_einstein_personalization_learn_about`, `persnl_setup_real_time_identity_resolution_for_einstein_personalization` [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/overview.html) |
| Interaction Studio | Marketing Cloud Personalization | A different product: "Marketing Cloud Personalization (formerly Interaction Studio)" [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers.htm&release=264.0.0&type=5) |
| Personalization Schema DMO (dev) | Personalization Content Schema DMO (help) | Same object, two labels [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_dmos.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/data-model-object-reference.html) |
- 264 pages still say "response template" (personalization point overview, terminology table, WPM prerequisites, experiment considerations); treat as synonyms. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_terms.htm&release=264.0.0&type=5)
- Recommender wording: terminology page says "goal-based recommendations or rule-based recommendations"; UI/setup say "objective-based" (`Maximize Revenue`, `Maximize Clicks`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_terms.htm&release=264.0.0&type=5)
- The `Decisioning API` is "the primary service endpoint used by Salesforce Personalization to request and process personalized decisions". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_terms.htm&release=264.0.0&type=5)

## 3. Permissions

### Standard permission sets
- `Personalization Admin`: "full control to configure and manage", create/read/update/delete. `Personalization User`: channel marketers, "without granting unnecessary access to underlying data configuration". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5)
- System permissions in **both** sets: `Access Personalization Platform`, `Allows user access Data 360` (sic), `Attribution Model User`, `Personalization Intelligence User`, `Use CRM Analytics Templated Apps`, `View Developer Name`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5)

| Object settings | Personalization Admin | Personalization User |
| --- | --- | --- |
| Data Graph Definitions, Data Model Field, Data Model Object, Data Model Taxonomy, Data Model Category, Data Space Definitions, Data Space, Data Object Tag Suggestion | Read, View All | Read, View All |
| Experiments, Streaming App Data Connectors, Personalization Points, Personalization Recommenders, Content Schemas | Read, Create, Edit, Delete, View All, Modify All | Read, Create, Edit, Delete, View All |
| Engagement Signals, Personalization Objectives, Batch Decisions, Engagement Signal Compound Metrics, Attribution Models, Market Segment Definitions | Read, Create, Edit, Delete, View All, Modify All | Read, View All |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5)
- Assign: Setup → `Users` → user → `Permission Set Assignments` → `Edit Assignments` → select set → `Add` → save. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_set.htm&release=264.0.0&type=5)
- Customize: Setup → `Permission Sets` → `Clone` next to Admin or User → unique name → edit (needs `Manage Profiles and Permission Sets`). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_permission_set_create.htm&release=264.0.0&type=5)

### Task-level requirements (verbatim labels from "User Permissions Needed")
| Task | Required | Source |
| --- | --- | --- |
| Deploy a preconfigured use case | `Personalization Intelligence Admin permission set` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_deploy.htm&release=264.0.0&type=5) |
| Install a Personalization Intelligence dashboard | `Personalization Intelligence User permission set` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5) |
| Create / enable a custom attribution configuration | `Personalization Intelligence User` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5) |
| Assign default data graphs to data spaces | `Personalization Admin` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_default_dg_to_ds.htm&release=264.0.0&type=5) |
| Create engagement signals / recommenders (Agentforce setup page) | `Personalization Admin permission set` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_agentforce_configure_personalization.htm&release=264.0.0&type=5) |
| Create, manage, view experiments | `Personalization Points` + `Experiments` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_create.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_manage.htm&release=264.0.0&type=5) |
| Modify decisions / add merge fields | `Create and Edit Personalization Points` + `Create and Edit Personalization Decisions` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_modify.htm&release=264.0.0&type=5) |
| Set up Personalization in MC Next setup | `Data Cloud Architect permission set` AND Salesforce Admin profile AND `Marketing Cloud Admin permission set` | [src](https://help.salesforce.com/s/articleView?id=mktg.mktg_data_graph_setup.htm&release=264.0.0&type=5) |
| Create batch personalizations | `Personalization Batch Decision` + `Market Segment Definitions` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_create_batch_persnl.htm&release=264.0.0&type=5) |
| Configure / map a Personalization campaign | `Personalization User` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_campaign_create.htm&release=264.0.0&type=5) |
| Access Web Personalization Manager (WPM) | `Web Personalization Manager user permission set` (access page only; the prerequisites page says `Personalization Admin` or `Personalization User`; see gotchas) | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_access_web_personalization_manager.htm&release=264.0.0&type=5) |
| Use Data 360 for Personalization (CRM connector) | `Data Cloud Architect` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_connect_salesforce_org_with_ep_data_data_cloud.htm&release=264.0.0&type=5) |
| Enable Data 360; schedule required CIs | "A Data Cloud Architect is required"; "A Data 360 Admin can complete this task" | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_enable_data_360_deploy_persnl_data_kits.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_schedule_required_ci.htm&release=264.0.0&type=5) |
| Add Goods Product custom fields | `Customize Application` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_add_custom_fields_to_goods_product_dmo.htm&release=264.0.0&type=5) |
| Configure localization | `Change and Edit` (sic) | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_localization_configure.htm&release=264.0.0&type=5) |

### Data 360 connector permission set (mandatory step)
- Setup → `Permission Sets` → `Data Cloud Salesforce Connector` → `System Permissions` → enable `Access Personalization Platform` → save → `Object Settings` → Read + View All Records on `Data Graph Definitions`, `Data Model Objects`, `Data Spaces`, `Personalization Points`, `Personalization Content Schemas`, `Personalization Recommenders`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_permission_set_update_data_cloud_connector_permissions.htm&release=264.0.0&type=5)

### Permission gotchas
- Conflict (docs disagree): the WPM access page's "User Permissions Needed" table says "Web Personalization Manager user permission set" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_access_web_personalization_manager.htm&release=264.0.0&type=5); the WPM prerequisites page says "Users need a Personalization Admin or Personalization User permission set to access Web Personalization Manager" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_prerequisites.htm&release=264.0.0&type=5). The standard permission sets page lists only those two sets and no WPM-named set [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5). Practical rule: assign `Personalization Admin` or `Personalization User`; if WPM still refuses access, check Setup → `Permission Sets` for a WPM-named set in the org. WPM also needs third-party cookies enabled in the browser.
- Conflict: object settings give `Personalization User` Create on Personalization Recommenders, but the Agentforce setup page requires `Personalization Admin permission set` to create recommenders and engagement signals (User has Read-only on Engagement Signals). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_agentforce_configure_personalization.htm&release=264.0.0&type=5)
- `Personalization Intelligence User` appears both as a system permission inside the standard sets and as a "permission set" name; `Personalization Intelligence Admin` appears only as a required permission set for Use Case Setup. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5)
- No SP permission set license (PSL) name is documented; only permission sets.

## 4. Data 360 prerequisites, data spaces, Personalization Setup

### Prerequisites
- "We recommend that you install and configure Data 360 before setting up Personalization and deploying foundational data." A data kit with foundational data "is installed after you purchase Salesforce Personalization". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_deploy_foundational_data.htm&release=264.0.0&type=5)
- Data spaces: SP connects to any data space; a default data space ships with Data 360; more require an add-on license; ensure **enhanced data space security** is enabled in the data space section of Data 360 Setup. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_space_requirements.htm&release=264.0.0&type=5)
- CRM data from another org: Salesforce CRM Connector (`Data Cloud Architect`); no big objects; tasks/events archived after 1 year aren't ingested; Bulk API extraction concurrency 25 requests of 20 s or longer. Path: `Data Cloud Setup` → `Salesforce CRM` → `New` → select org → `Connect`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_connect_salesforce_org_with_ep_data_data_cloud.htm&release=264.0.0&type=5)
- Real-time identity resolution: map Personalization DLOs to DMOs first; custom match rule Object `Party Identification`, Field `Identification Number`, Match Method `Exact`, `Match on Blank` unchecked, name ≤80 chars; real-time matching compares against unified profiles in the ruleset's real-time data graph. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5)
- Real-time IR supports only exact and exact-normalized matching (emails, phones); fuzzy conditions run in batch; use the unified individual as the profile data graph root so real-time IR applies. Recommended Individual-ruleset custom rules: `Identity Match` / `Identity Match Type` = `lead-to-contact` and `device-to-known`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_add_recommended_rules_to_ir_ruleset.htm&release=264.0.0&type=5)
- Maximize Revenue (retail) needs Goods Product fields `UnitPrice__c` (number) and `ImageUrl__c` (text). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_add_custom_fields_to_goods_product_dmo.htm&release=264.0.0&type=5)

### Onboarding sequence (Setup Guide, 11 steps)
1. Getting to Know SP → 2. Assign permissions → 3. Enable Data 360 and deploy data kits → 4. Schedule required CIs → 5. Build a Data 360 sitemap (Sitemap Builder Chrome extension) → 6. Configure a website connector → 7. Upload an event schema (JSON) → 8. Configure and map data streams ("the data kits only deploy datastreams used for analytics and attribution") → 9. Identity resolution rules → 10. Create required data graphs ("you can use two": real-time profile + standard item) → 11. CIs for targeting. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_d360_setup_for_personalization.htm&release=264.0.0&type=5)
- Data graph creation: set consumption limits for real-time graphs; real-time joins must use the parent DMO primary key; the guide says "Select a 30 minute refresh interval". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_create_required_data_graphs.htm&release=264.0.0&type=5) Newly created or edited real-time graphs block N:1 relationships (1:1 and 1:N only); older real-time graphs with N:1 keep running but parent-DMO changes aren't reflected until rebuild/refresh; standard graphs still support N:1. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=data.c360_a_dg_n1_restriction.htm&release=264.0.0&type=5)

### Personalization Setup page map (Setup → Quick Find `Personalization` → `Personalization Setup` → "Personalization Setup Options")
| Tab | Sections and actions | Source |
| --- | --- | --- |
| `Foundational Setup` | `Deploy Foundational Data` (`Select Data Space` → `Deploy`); `Personalization Pipeline Intelligence Dashboard Setup` (CRM Analytics check, `Enable`); `Install the Personalization Pipeline Intelligence Dashboard` (`Select Data Space` → `Install`); `Personalization Attribution Intelligence Setup` (`Select Data Space and IR Ruleset` → `Deploy`) | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_deploy_foundational_data.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5) |
| `Data Graph Defaults` | `Data Space` → `Default Profile Data Graph`; global on/off toggle | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_default_dg_to_ds.htm&release=264.0.0&type=5) |
| `Use Case Setup` | `Deploy Preconfigured Use Cases` | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_deploy.htm&release=264.0.0&type=5) |
| `Advanced Setup` | `Localization` toggle → `Select Data Space` (must have foundational data) → item localization DMO + locale field → optional profile locale fallback (ignored when the decision request carries a locale) | [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_localization_configure.htm&release=264.0.0&type=5) |
- The Feb '26 (260) "improved workflow" reorganized these pages and "changes how you select and manage data spaces" for deployment and dashboard installation. [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_rt_setup_ui_updates.htm&release=260&type=5)
- MC Next path: Setup → `Customer Engagement` → `Go to Personalization Setup` → `Start Setup` → data space → `Deploy`. [src](https://help.salesforce.com/s/articleView?id=mktg.mktg_data_graph_setup.htm&release=264.0.0&type=5)

### Deploy Personalization Foundational Data (per data space)
| Requirement | What is deployed |
| --- | --- |
| DMOs | Personalization Point, Personalization Decision, Personalization Content Schema, Personalizer, PersonalizationLog |
| Connectors and data streams | A Salesforce CRM data stream for each of those 5 DMOs; an Ingestion API connector + data stream for Personalization Log (including the Ingestion API Schema File) |
| Object mapping | "Installed DMOs are fully mapped during data stream creation." |
| Calculated insights | `Daily Personalization Uniques`, `Daily Personalization Requests` — installed but **must be manually scheduled** |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_deploy_foundational_data.htm&release=264.0.0&type=5)
- DMO relationships deployed are not listed in the doc (see Gaps).

### Install a Personalization Pipeline Intelligence Dashboard
- One dashboard per data space; CRM Analytics must be enabled (`Enable` → Getting Started → `Enable CRM Analytics`); data space must already have foundational data and both CIs; "These calculated insights, and any associated queries, are billable events within Data 360." [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5)

### Deploy Preconfigured Personalization Attribution Intelligence Data
- Optional; needed for add-to-cart, order, revenue attribution; requires Product Browse Engagement, Shopping Cart Engagement, Product Order Engagement objects; target data space must already have foundational data; IR ruleset optional; deployment detects an existing deployment. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Installs: DLOs `{dataspacePrefix}_{irSuffix}_PersnlPointFirstTouchViewAttr`, `_PersnlPointLastTouchViewAttr`, `_PersnlContentFirstTouchViewAttr`, `_PersnlContentLastTouchViewAttr`; matching DMOs with `__dlm`; attribution models `{dataspacePrefix}_{irSuffix}_DefaultAttribution_FT` and `_DefaultAttribution_LT`; a Salesforce CRM data stream per attribution DMO; full mapping; no CIs (example SQL provided). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Naming: default data space adds no prefix; no IR ruleset → no `{irSuffix}`; IR ruleset with empty suffix → `e_s_`; IR ruleset starting with a number on the default data space → `n_s_{irSuffix}`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Predefined configurations measure `Views`, `Clicks`, `Add to carts`, `Orders`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_settings.htm&release=264.0.0&type=5)
- Custom configuration: App Launcher → `Attributions` → `New` → data space → IR ruleset or `No IR Ruleset` → `First Touch`/`Last Touch` + attribution window → 2–4 funnel stages; each stage's engagement signal "must have an active relationship with the Personalization Log DMO". [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5)
- Enabling a draft creates a `Personalization Point Output DMO` and a `Personalization Point Content Output DMO` (names must differ). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_enable_draft.htm&release=264.0.0&type=5)

### Including Personalization Components in Data Kits
- Packageable: `Personalization Recommenders`, `Engagement Signals`, `Personalization Objectives`; dependencies (objective, engagement signals, mapped DMOs, data graph relationships) are auto-added, but related/mapped objects of the data graph are not — add them or pre-create them in the target org; "Packages don't currently support adding filters"; publish with Package Manager. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_including_components_in_data_kits.htm&release=264.0.0&type=5)
- May '26 (262): import single components from a data kit during object creation (engagement signals, personalization points, response templates). [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=262.0.0&type=5)

## 5. Preconfigured recommender use case and default data graph assignment (262)

### Use Case Setup (June '26)
- "Intended for new Salesforce Personalization customers"; creates a fully mapped profile data graph, item data graph, recommender, content schema, required CIs. [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_preconfig_use_case_setup.htm&release=262.0.0&type=5)
- Hard constraints: the data space must contain **no** profile data graphs; one deployment per data space; verification flags missing or unmapped objects that must be fixed before deploy. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_wtk.htm&release=264.0.0&type=5)
- Steps: `Use Case Setup` → `Deploy Preconfigured Use Cases` → data space → `Select` → `Maximize Product Revenue` or `Maximize Article Clicks` → `Next` → Use Case Verification and Setup (choose a unified individual DMO for the real-time profile data graph; red X = missing/unmapped; fix via the Behavioral Events data stream; green checks enable `Deploy`) → `Deploy` → then add decisions to the personalization point. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_deploy.htm&release=264.0.0&type=5)

| Use case | Profile DG | Item DG | Content schema | Recommender | Personalization point | CI |
| --- | --- | --- | --- | --- | --- | --- |
| Maximize Revenue Products | Real-Time Data Graph | Product Data Graph | Product Recommendations Schema | Maximize Revenue Product Recommender | Product Recommendations | Top Sellers |
| Maximize Clicks Articles | Real-Time Data Graph | Article Data Graph | Product Recommendations Schema | Maximize Clicks Article Recommender | Article Recommendations | — |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_what_deployed.htm&release=264.0.0&type=5)

### Default profile data graph ↔ data space (June '26)
- Auto-populates the profile data graph when that data space is selected; can be overridden per configuration. [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_default_profile_dg_to_ds_assgmnt.htm&release=262.0.0&type=5)
- On by default; the `Data Graph Defaults` toggle disables **all** assignments globally (no per-space disable); editing a default doesn't change existing SP configurations. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_default_dg_to_ds.htm&release=264.0.0&type=5)

## 6. Personalization DMOs

### Pipeline DMOs (design time + runtime)
| DMO | Purpose | API name (SP dev guide) | API name (Data 360 DMO guide, "Available in 254 and later") |
| --- | --- | --- | --- |
| Personalization Point | Eligibility, content decisions, presentation | `PersonalizationPoint__dlm` | `std__PersonalizationPointDmo__dlm` |
| Personalization Decision | Decisioning for eligibility and content | `PersonalizationDecision__dlm` | `std__PersonalizationDecisionDmo__dlm` |
| Personalization Content Schema | Decision configuration options + response shape | `PersonalizationSchema__dlm` | `std__PersonalizationSchemaDmo__dlm` |
| Personalizer | Whether to call an extra service (e.g., recommender) at runtime | `Personalizer__dlm` | `std__PersonalizerDmo__dlm` |
| Personalization Log | Pipeline operational + attribution data | `PersonalizationLog__dlm` | `std__PersonalizationLogDmo__dlm` |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_dmos.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-dmo.html) [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html)
- Point fields: `DeveloperName__c`, `Name__c`, `PersonalizationSchemaId__c`, `Status__c` (e.g., `Active`, `Processing`, `Deleting`), `ProfileDataGraphId__c`, `Source__c` (e.g., Personalization App or Experience Builder). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-dmo.html)
- Decision fields: `PersonalizationPointId__c`, `PersonalizerId__c`, `PersonalizationDecisionPriority__c`, `Criteria__c` (targeting rules). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-decision-dmo.html)
- Schema fields: `PersonalizationType__c`, `ContentObject__c`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-schema-dmo.html)
- Log fields: `PersonalizationRequestId__c`, `PersonalizationId__c`, `PersonalizationContentId__c`, `RequestStartDateTime__c`, `AugmentingStageTimeMillis__c`, `QualifyingStageTimeMillis__c`, `PersonalizingStageTimeMillis__c`, `ResponseTimeMillis__c`, `IndividualId__c`, `PersonalizationType__c`, plus (documented without `__c`) `PersonalizationPointId`, `PersonalizationDecisionId`, `PersonalizerId`, `Content`, `ContentLength`, `NumContentItems`, `DmoLabel`, `DmoApiName`, `DmoRecordId`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html)
- Unauthenticated Decisioning API diagnostics go to the PersonalizationLog entry, not the response. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-pipeline-diagnostics.html)
- Request `context` is recorded "as an extension of Personalization Record in the Personalization Record Data Lake Object (DLO)". [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html)

### Attribution DMOs (first/last touch: 100% of value to first/last qualifying view or impression)
| DMO | Aggregated by | API name |
| --- | --- | --- |
| Personalization Point First Touch View-Based Attribution | Personalization point | `PersnlPointFirstTouchViewAttr__dlm` |
| Personalization Content First Touch View-Based Attribution | Content | `PersnlContentFirstTouchViewAttr__dlm` |
| Personalization Point Last Touch View-Based Attribution | Personalization point | `PersnlPointLastTouchViewAttr__dmo` on the dev DMO page; the attribution deployment page gives `{dataspacePrefix}_{irSuffix}_PersnlPointLastTouchViewAttr__dlm` — treat `__dmo` as a doc typo |
| Personalization Content Last Touch View-Based Attribution | Content | `PersnlContentLastTouchViewAttr__dlm` |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_dmos.htm&release=264.0.0&type=5) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-click-attribution-dmo.html) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Deployed attribution objects carry the `{dataspacePrefix}_{irSuffix}_` prefix (see §4), so org API names differ from the bare names above. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5)
- Conflict: the dev DMO index describes the Last Touch rows as engagement/click-based and hosts them at `...-click-attribution` URLs; the help page and the DMO pages call them view-based. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/data-model-object-reference.html)

### Experiment DMOs
| DMO | API name | Content |
| --- | --- | --- |
| Experiment | `ssot__AbnExperiment__dlm` | Name, description, state, start/stop, primary metrics |
| Experiment Cohort | `ssot__AbnExperimentCohort__dlm` | Control/treatment cohorts, allocation weights |
| Experimentation Log | `ssot__AbnExperimentLog__dlm` | Per-event data |
| Experimentation Summary | `ssot__AbnExperimentationSummary__dlm` | Metrics, participant counts, statistics |
| Experimentation Daily Summary | `ssot__AbnExperimentationDailySummary__dlm` | Daily aggregates |

[src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/experiment-dmo.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/experimentation-log-dmo.html)
- The Data 360 DMO guide also lists `std__AbnExperimentLogDmo__dlm` (254+). [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-abnexperimentlogdmo-dmo.html)
- Experimentation Log fields: `PersonalizationPointId__c`, `PersonalizationDecisionId__c`, `PersonalizationId__c`, `Requestid__c`, `AbnExperimentId__c`, `AbnExperimentCohortId__c`, `TreatmentValueText__c`, `PoolAssignmentNumber__c`, `TrackingKeyText__c`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/experimentation-log-dmo.html)

### Batch Personalization Output DMO
- API name is auto-generated from the batch personalization name; primary key `Id__c`; fields `ProfileID__c`, `IndividualId__c`, `KQ_Id__c`, `SegmentId__c`, `PersonalizationPointId__c`, `PersonalizationPointApiName__c`, `PersonalizationDecisionId__c`, `PersonalizationBatchDecisionId__c`, `PersonalizationId__c`, `LastUpdatedDateTime__c`, `ActivationData__c` (decision JSON), `UnifiedIndividualId__c`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/batch-personalization-output-dmo.html)

### Recommendation inference logs (Data 360 standard DMOs)
- `std__PersnlRcmdItemLogDmo__dlm` ("Available in 262 and later"): per-item contextual-bandit signals, child of Persnl Rcmd Log DMO; fields include `std__PropensityScoreNbr__c`, `std__IsForcedExplore__c` (epsilon-Thompson hybrid exploration), `std__InferencePolicyType__c` (cold-start vs fully trained), `std__ItemRoleType__c`, `std__PersonalizationIdentifier__c`, `std__PersonalizerId__c`, `std__DataSpace__c`. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-persnlrcmditemlogdmo-dmo.html)

### Standard engagement DMOs carrying personalization fields
- Website Engagement DMO: `ssot__PersonalizationId__c`, `ssot__PersonalizationContentId__c`, `ssot__PersonalizationRequestId__c`, `ssot__PerslServiceProviderName__c`, `ssot__OfferId__c`, `ssot__OfferTreatmentId__c`, `ssot__PromotionId__c`, `ssot__CorrelationId__c`. [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html)
- Out-of-the-box engagement destinations: `Product Engagement` → event type `catalog` → Product Browse Engagement (`catalog-object-view-start`, `catalog-object-click`; payload has `id`, `type` = `Product`); `Website Engagement` → `userEngagement` → Website Engagement (`personalization-view`, `personalization-click`; no `id`/`type`). Manually sent events must include `personalizationId` and `personalizationContentId`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html)
- Engagement DMOs whose `PersonalizationContentId` has a foreign key to Personalization Log `Id` (attribution-eligible): Website, Website Item, Product Browse, Shopping Wishlist (and Item), Shopping Cart Product, Sales Order Product, Media, Lead, Social Message, Promotion Engagement. Per-DMO citations are in measurement-and-attribution.md §1.6; example [src](https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-productbrowseengagementdmo-dmo.html).

### Platform sObjects
- `PersonalizationPoint`, `PersonalizationDecision`, `PersonalizationSchema` — API 62.0+; points and decisions support ChangeEvent, Feed, History, OwnerSharingRule, Share. [src](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationPoint.htm) [src](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationDecision.htm)

## 7. Consent
- Only documented purpose constant: `SalesforceInteractions.ConsentPurpose.Tracking` = `Tracking` ("general behavioral tracking"); statuses `SalesforceInteractions.ConsentStatus.OptIn` = `Opt In`, `...OptOut` = `Opt Out`; consent object needs `provider`, `purpose`, `status`. [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html)
- The SDK "doesn't store or transmit any collected data until it has been granted explicit consent" and waits for `Opt In`; supply via `init({ consents })` (array or Promise) or `updateConsents()`; read with `getConsents()` (`ConsentWithMetadata[]`). [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html) On revoke it "immediately stops emitting events". [src](https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-salesforce-interactions-web-sdk.html)
- MCP ≠ SP (migration article, MCP breadcrumb): SP "Explicit consent is required", unspecified → opt-out, no consent config → "all users are treated as opted-out"; MCP defaults to implicit opt-in and uses purpose `'Personalization'`, which the Data 360 Web SDK example says `Tracking` "Replaces"; SP adds `interactions:onConsentGrant` next to `interactions:onConsentRevoke`. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5)
- Answer: SP documents **no separate "Personalization" purpose**; `Tracking` gates collection.
- Mobile: fetch errors `CONSENT` / `.consent` = "User consent is not set to opt-in"; `isConsentOptIn()` is false for unset and opt-out; "A consent change does not automatically retry a prior content request"; low-code guidance: "Personalization must remain disabled until the user explicitly opts in." [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-lowcode-android.html) [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-lowcode-flutter.html)
- Engagement Mobile SDK states: `optIn` transmits and flushes the queue; `optOut` drops and deletes queued events; `pending` is the SDK-managed default. [src](https://developer.salesforce.com/docs/data/data-cloud-engagement-mobile-sdk/guide/c360a-api-engagement-mobile-sdk-consent-management-v3.html)
- Server-side and batch: SP docs don't say the Decisioning API, the invocable action or batch jobs check Data 360 consent (undocumented). Data 360 provides the controls: consent attributes as segment filters [src](https://help.salesforce.com/s/articleView?id=data.c360_a_using_consent_preferences_in_segmentation.htm&release=264.0.0&type=5); `Contact Point Consent` (L3) and `Contact Point Subscription Consent` (L4) filters on contact points in DMO activations [src](https://help.salesforce.com/s/articleView?id=data.c360_a_batch_dmo_activation.htm&release=264.0.0&type=5); "We suggest checking for consent before using this data in any marketing platform" [src](https://help.salesforce.com/s/articleView?id=data.c360_a_checking_consent_preferences_activation.htm&release=264.0.0&type=5). Pattern (inference): batch → consent filter in the target segment and in the DMO activation; server-side → add the consent DMO to the profile data graph and gate each decision with a `Related Attributes` condition, or enforce consent in the caller. The batch contact-point filter checks reachability ("individuals who can be contacted"), not consent [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_create_batch_persnl.htm&release=264.0.0&type=5).
- Web decisioning: whether `Personalization.fetch` is blocked without opt-in is not stated (UNVERIFIED). The dev example uses `consents: []`; under SP defaults that likely means opted-out (inference, UNVERIFIED). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html)

```javascript
SalesforceInteractions.init({
  consents: [{ provider: "<ConsentProvider>", purpose: SalesforceInteractions.ConsentPurpose.Tracking,
               status: SalesforceInteractions.ConsentStatus.OptIn }],
  personalization: { dataspace: "default" } // required if >1 data space; omitted → `default`
});
```

## 8. Considerations and limits

### Personalization point considerations
- One data space per point; the profile data graph must be in that data space; recommenders are selectable only if built on the same profile data graph; targeting uses direct attributes, related attributes, CIs, segment memberships. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5)
- A point can require authentication → evaluated only via the authenticated Decisioning API endpoint. Initial decision priority = creation order (editable) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5); a person qualifying for several decisions gets only one. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_terms.htm&release=264.0.0&type=5)
- WPM lists only points built on real-time profile data graphs. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5) Personalization campaigns support only Dynamic Content schemas and the web channel; WPM uses the Data 360 Web Connector base URL. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_campaign_prereq.htm&release=264.0.0&type=5)

### Real-time vs standard profile data graph
| | Real-time | Standard |
| --- | --- | --- |
| Use | Latency-sensitive web/mobile, in-session behavior | Outbound messaging, batch |
| Profile lookup | Data 360 profile API | Skipped |
| Caller sends | Individual ID | Full profile data graph JSON |
| If profile not sent | n/a | Blank anonymous profile → profile-based targeting rules and recommender filters evaluate **false** |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5)
- Batch and MC Growth/Advanced sends include the profile automatically [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5). Conflict: help says put the JSON "in the context object"; the API reference has a separate `profile` body parameter ("A Data 360 Hot Layer Profile … skips retrieving the profile"). [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html)

### Decisioning API constraints
- Base URI `https://{tenantSpecificEndpoint}`; aliases `/personalization/v1/decisions`, `/personalization/v1/authenticated/decisions`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-reference.html)
- "Make sure all personalization points use the same profile data graph" in one request; mobile SDK doesn't group by data graph for you. `executionFlags`: `TestMode` (no outputs recorded to the data lake), `ContextOnly` (no profile lookup), `EnableDiagnostics`; `context` wins on duplicate keys; for accounts send `profileId` instead of `individualId`. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html)
- Diagnostics: returned only for authenticated calls; `decisionId` on unauthenticated calls → 408 `SPECIFIED_DECISION_NOT_SUPPORTED` → HTTP 400; overload → 406 `TOO_MANY_REQUESTS` → HTTP 429 ("throttle or hold-off"); 533 `RECOMMENDER_CONTENT_SIZE_EXCEEDED` → truncated. Diagnostic codes are not HTTP codes. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-pipeline-diagnostics.html)
- Mobile `fetchDecisions` default timeout 10 seconds. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-android.html)

### SP limits (264)
| Area | Limit |
| --- | --- |
| Recommenders per org (all data spaces) | 10 (1 objective-based with Personalization Card); increase via Support |
| Full recommender data refresh | Daily |
| Recommendation requests per minute per tenant | 60000 |
| Recommendations returned | 24 |
| Recommender objectives per org | 10 |
| Include/exclude filter conditions | 10 |
| Item DG CI values considered (dimensions + measures) | Top 100 |
| Profile DG filter values per condition; DMO values in filter comparisons | 100; 100 |
| Direct related objects to root DMO per item DG | 20 |
| Engagement signals: per objective-based recommender (training) / per org / per data space | 25 / 100 / 100 |
| Filters per engagement signal; related DMOs per signal; referenced field levels in a DG | 10; 1; 3 |
| Engagement signal metrics / compound metrics per org and per data space | 100 each |
| Metrics per engagement signal | 10 |
| Attribution models per org (active + inactive) / per data space | 20 / 10 |
| Stages per attribution config; signals per stage; metrics per config | 4; 1; 5 |
| Active batch personalization jobs per org | 20 |
| Decisions per personalization point | 25 |
| Targeting conditions per decision or experiment | 50 |
| Merge fields across attribute fields per decision | 10 |

[src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5)
- Max personalization points per Decisioning API request: not documented. MC Next Dynamic Content: 25 personalization points per email/landing page, 15 variations per component. [src](https://help.salesforce.com/s/articleView?id=mktg.mktg_content_personalization_ep.htm&release=264.0.0&type=5)
- Experiments: ≥1,000 participants per cohort; first cohort = control; unallocated % → control. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_considerations.htm&release=264.0.0&type=5)

### Data 360 data graph limits that bind SP
| Limit | Standard DG | Real-time DG |
| --- | --- | --- |
| Data graphs per org (hard) | 25 | 25 |
| Draft data graphs per org | 5 | 5 |
| Scheduled refreshes per day | 1 (changeable) | 24; instant for active sessions, lakehouse copy hourly |
| JSON records per data graph | 200 million | 100 million |
| Max size | — | 200 KB (performance may degrade above) |
| Objects per DG; fields per DMO; total fields + measures; measures per CI | 25; 50; 200; 5 | same |
| Engagement events in a DG; max engagement age | 100; 30 days (720 hours) | not listed; 30 days (720 hours) |
| Nesting levels below primary DMO; records per DMO | 5; 1,000 (default 100) | same |

[src](https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5)
- Data graphs per org rose from 10 to 25 on Apr 14, 2026. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_changelog_usage_and_access.htm&release=264.0.0&type=5)

### Latency and real-time behavior
- Docs promise "within milliseconds" (real-time IR + SP) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5) and "decisioning times in milliseconds" (standard DG path) [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5); no numeric SLA.
- Record caching keeps recently active known visitors in the real-time layer; if disabled, "the first page visited by your known visitors might not show personalization immediately", and sub-second real-time profiles and entities entitlements aren't consumed. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_record_caching_in_rt_data_graphs.htm&release=264.0.0&type=5)
- Measure latency with the Personalization Log `...StageTimeMillis__c` and `ResponseTimeMillis__c` fields. [src](https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html)

### Credit consumption
- SP: each `Personalization Decision` consumes Personalization or Flex credits (see §1). [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_billable_usage_types.htm&release=264.0.0&type=5)
- Data 360 (Flex): `Data 360 Real-Time Pipeline` = profile events + engagement events + API calls processed in the sub-second real-time layer when tied to a real-time data graph; `Data 360 Streaming Pipeline` covers Website/Mobile App connector streams; batch CIs bill under `Data 360 Prep`; plus Segmentation and Activation. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5) Credits bought before Feb 24, 2026 are Data Services (real-time equivalent: `Sub-second Real-Time Events`); later purchases can be either. [src](https://help.salesforce.com/s/articleView?id=data.c360_a_data_usage_types.htm&release=264.0.0&type=5)
- Real-time data graphs also meter `Sub-second Real-Time Profiles & Entities` (Data 360 Real-Time Profile card) = unique active visitors per billing month; data graph refresh cost depends on refresh frequency, model structure and fields updated (one product-category change can refresh thousands of profiles). [src](https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_data_graphs.htm&release=264.0.0&type=5)
- Batch on a unified-individual data graph uses one individual ID per unified profile "to avoid unnecessary credit consumption for duplicate decisions" [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_create_batch_persnl.htm&release=264.0.0&type=5); with contact point filtering, decisions (and credits) can be fewer than segment members. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_persnl_faqs.htm&release=264.0.0&type=5)

## 9. Feature timeline (Personalization Features Released by Month + 264)
| Month | Rel. | Feature | Meaning |
| --- | --- | --- | --- |
| Dec '25 | 260 | Personalize Mobile Experiences with Engagement Mobile SDK | Pro-code Personalization module for iOS/Android |
| Dec '25 | 260 | Curate Website Content with Agentforce Adaptive Websites | Agent-curated site content from real-time signals |
| Jan '26 | 260 | [MCP] Extend MCP Data to SP with Marketing Cloud Next for Personalization | One-time MCP metadata/catalog export into Data 360 |
| Feb '26 | 260 | Set Up Salesforce Personalization With an Improved Workflow | Reorganized Setup pages and data space selection |
| Feb '26 | 260 | Automate Testing Using Experimentation as a Service | Experiment Connect + Runtime Experiment Assignment APIs |
| Feb '26 | 260 | Show or Hide Recommendations Based on Date and Time | `Is Before Current DateTime` / `Is After Current DateTime` |
| Feb '26 | 260 | Sort Rule-Based Recommendations Meaningfully | Sort by item DG attributes or profile DG CIs |
| Feb '26 | 260 | Build Data 360 Sitemaps Using the Sitemap Builder | Low/no-code Chrome extension |
| Feb '26 | 260 | Use Real-Time Calculated Affinities | Affinities in targeting rules, segments, filters |
| Mar '26 | 260 | Personalize Decision Responses with Merge Fields | Profile DG attributes and segment IDs in responses |
| Mar '26 | 260 | Maximize Revenue with Impactful Promotion Recommendations | OOTB promotion recommender |
| Mar '26 | 260 | Capture More Relevant Engagement Data for Evaluation | More engagement-signal filter operators |
| Mar '26 | 260 | [MCP] Sitemap Converter; Customized Web Data Streams | MCP→Data 360 sitemap/metadata transfer aids |
| Apr '26 | 260 | Localize Recommendations | `Advanced Setup` → Localization with fallbacks |
| May '26 | 262 | Build and Customize Experience Templates | Templates in SP app; sitemap templates auto-migrated [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_build_customize_experience_templates.htm&release=262.0.0&type=5) |
| May '26 | 262 | Individual Objects in Data Kits | Import single components at creation |
| May '26 | 262 | Deliver Consistent Recommendations with Fallbacks | Fallback recommender, no duplicates |
| May '26 | 262 | [MCP] Campaign and Segment Folder Permissions | MCP role change only |
| Jun '26 | 262 | Preconfigured Recommender Use Case | `Use Case Setup` tab |
| Jun '26 | 262 | Personalization Campaigns | Guided config; web + Dynamic Content only |
| Jun '26 | 262 | Default Profile Data Graph to Data Space | `Data Graph Defaults` tab |
| Jun '26 | 262 | Tailor Recommendations for Accounts | Rule-based recommenders on account profiles |
| Jun '26 | 262 | Date and Numeric Placeholders | `{!MinDate}`, `{!MaxAge}` resolved at runtime |
| Jul '26 | 262 | Related Attributes and CIs in Decisions | Multi-value merge fields with sort criteria |
| Jul '26 | 262 | Recommend Offers Across Catalogs Using Indirect Signals | Custom objectives link indirect signals to offers |
| Aug '26 | 264 | Analyze Experiment Results with the Data Visualization Tab | Summary cards, odds of winning, trend charts |
| Aug '26 | 264 | Deliver Personalized Mobile Experiences Without Rebuilding Your App | Low-code mobile (iOS, Android, React Native, Flutter) |

[src](https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=260&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=262.0.0&type=5) [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=264.0.0&type=5)

## MCP confusion traps
- "Consent is implicit; only an explicit opt-out stops events" — MCP only. SP requires explicit opt-in; missing config = everyone opted out. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5)
- "Use consent purpose `Personalization`" — MCP. SP / Data 360 Web SDK uses `Tracking`. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5)
- "Editions are Growth and Premium" — MCP. SP: Developer/Enterprise/Professional/Unlimited + SP add-on on Data 360. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_about.htm&release=264.0.0&type=5)
- "100 user attributes per dataset; export up to 10 million users per day per dataset" — MCP limits; SP has data spaces, not datasets, and the §8 limits. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_limits.htm&release=264.0.0&type=5)
- "CRM integration needs Enterprise+ CRM, ModifyAllData, and an email mapping field" — MCP's CRM integration; SP ingests CRM via the Data 360 Salesforce CRM Connector (`Data Cloud Architect`). [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_salesforce_crm_prereqs.htm&release=264.0.0&type=5)
- "Einstein Recipes / Einstein Decisions (next-best-offer)" — MCP ML. SP uses recommenders (objective/rule-based) and personalization decisions; "Einstein Studio Model Predictions" in SP is Data 360 Einstein Studio. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_machine_learning.htm&release=264.0.0&type=5)
- "Catalog is a graph-based setup" — MCP. SP "uses a flat, table-based setup structure" on Data 360 DMOs. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_benefits.htm&release=264.0.0&type=5)
- "Grant Salesforce Customer Support access for up to 1 year in the Personalization UI" — MCP. No SP equivalent documented (SP lives in the org; UNVERIFIED which access mechanism applies). [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers_access_salesforce_setup.htm&release=264.0.0&type=5)
- "Campaigns = web, server-side, triggered, open-time email, mobile campaigns" — MCP. SP "Personalization Campaigns" (262) are a guided web-only, Dynamic Content-only flow on personalization points. [src](https://help.salesforce.com/s/articleView?id=mktg.mc_pers.htm&release=264.0.0&type=5)
- MCE Content Builder "Dynamic Content" (subscriber-attribute rules) is unrelated to the SP `Dynamic Content` personalization type [src](https://help.salesforce.com/s/articleView?id=mktg.mc_ceb_dynamic_content.htm&release=264.0.0&type=5); MC Next email/landing-page dynamic content **is** backed by SP points, decisions, targeting rules [src](https://help.salesforce.com/s/articleView?id=mktg.mktg_content_personalization_ep.htm&release=264.0.0&type=5).
- Doc hygiene: `mc_pers_*` = MCP, `mc_persnl_*`/`persnl_*` = SP; the `products` tag "Marketing|Salesforce Personalization" also appears on MCP pages — trust the breadcrumb. `developer.salesforce.com/docs/marketing/personalization/` is MCP; even the SP Localization article links to MCP `sitemap-implementation`. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_localization_configure.htm&release=264.0.0&type=5)
- The monthly release table mixes both products — check the `Product` column (e.g., the Sitemap Converter and folder-permission items are MCP). [src](https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=260&type=5)
- `MCP+` SKUs consume **Personalization Credits** for SP decisions; don't infer an MCP-only entitlement from the SKU name. [src](https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_billable_usage_types.htm&release=264.0.0&type=5)

## Gaps and uncertainties
- Einstein Personalization → Salesforce Personalization rename date/release not found (older help and release notes before 260 are not indexed).
- Release in which "response template" → "content schema" and "Manual Content" → "Dynamic Content" changed is not stated; stored enum value of `PersonalizationType__c` after the rename is UNVERIFIED.
- No SP permission set license (PSL) names; `Personalization Intelligence Admin` and `Web Personalization Manager user` permission sets are referenced but their contents are undocumented.
- Two DMO naming sets (`PersonalizationLog__dlm` vs `std__PersonalizationLogDmo__dlm`; `ssot__AbnExperimentLog__dlm` vs `std__AbnExperimentLogDmo__dlm`); which appears in a given org is UNVERIFIED — check Data Model in the org.
- Foundational deployment doesn't list DMO relationships it creates.
- Max personalization points per Decisioning API request, per-request latency SLA, and Decisioning API rate limit (other than 60000 recommendation requests/min/tenant and HTTP 429) are undocumented.
- Whether web `Personalization.fetch` is blocked without `Tracking` opt-in, and whether server-side/batch decisions honor Data 360 consent, are undocumented; §7 lists the Data 360 consent controls to apply instead.
- Credit impact of `TestMode` calls, WPM previews, and experiment control cohorts is undocumented.
- Edition conflict (Setup Guide "Enterprise and Unlimited … Personalization Starter add-on" vs editions page) and the WPM / recommender permission conflicts remain unresolved in docs.

## Sources
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.mc_persnl.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_how_it_works.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_standard_editions_and_licenses.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_billable_usage_types.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_terms.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_limits.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_basics_dmos.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_cloud_and_einstein_personalization_learn_about.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_graphs_using.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_sets_to_users.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_assign_standard_permission_set.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_permission_set_create.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_permission_set_update_data_cloud_connector_permissions.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_assigning_permissions.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_data_space_requirements.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_connect_salesforce_org_with_ep_data_data_cloud.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_websdk_ep_module.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_deploy_foundational_data.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_install_pers_pipeline_dashboard.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_pers_attribution_intel_data_deploy.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_including_components_in_data_kits.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_wtk.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_what_deployed.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_use_case_deploy.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_default_dg_to_ds.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_real_time_identity_resolution_for_einstein_personalization.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_add_custom_fields_to_goods_product_dmo.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_setup_localization_configure.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_d360_setup_for_personalization.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_enable_data_360_deploy_persnl_data_kits.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_schedule_required_ci.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_create_required_data_graphs.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_considerations.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_real_time_profile_data_graphs.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_standard_profile_data_graphs.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_content_schema_using.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_prerequisites.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_wpm_access_web_personalization_manager.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_create.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_considerations.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_create_batch_persnl.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_campaign_create.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_campaign_prereq.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attribution_settings.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_custom_create.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_analytics_attrib_config_enable_draft.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_agentforce_configure_personalization.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mktg_content_personalization_ep.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mktg_data_graph_setup.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.mc_ceb_dynamic_content.htm&release=264.0.0&type=5
- SP help (mktg): https://help.salesforce.com/s/articleView?id=mktg.persnl_exp_manage.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_personalization_point_decision_modify.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_qs_add_recommended_rules_to_ir_ruleset.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.persnl_batch_persnl_faqs.htm&release=264.0.0&type=5
- Data 360 help: https://help.salesforce.com/s/articleView?id=data.c360_a_dg_n1_restriction.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_billing_considerations_for_data_graphs.htm&release=264.0.0&type=5
- Data 360 help: https://help.salesforce.com/s/articleView?id=data.c360_a_dc_releases.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_limits_and_guidelines.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_changelog_usage_and_access.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_create_a_data_graph.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_record_caching_in_rt_data_graphs.htm&release=264.0.0&type=5
- Data 360 help: https://help.salesforce.com/s/articleView?id=data.c360_a_flex_credits_for_data360.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=data.c360_a_data_usage_types.htm&release=264.0.0&type=5
- Release notes: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=260&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_personalization_features_released_by_month.htm&release=262.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=260&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=262.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_personalization.htm&release=264.0.0&type=5
- Release notes: https://help.salesforce.com/s/articleView?id=release-notes.rn_c360_truth.htm&release=262.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_c360_truth.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_rt_setup_ui_updates.htm&release=260&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_mobile_experiences.htm&release=260&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_preconfig_use_case_setup.htm&release=262.0.0&type=5
- Release notes: https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_default_profile_dg_to_ds_assgmnt.htm&release=262.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_build_customize_experience_templates.htm&release=262.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_personalize_mobile_lowcode.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=release-notes.rn_persnl_data_viz_tab.htm&release=264.0.0&type=5
- SP developer guide: https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/overview.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-web-experiences.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/request-personalization-through-sitemap.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/track-personalization-engagement.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-reference.html
- SP developer guide: https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-request-personalization.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-authenticated-request.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/decisioning-api-pipeline-diagnostics.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-android.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-lowcode-android.html
- SP developer guide: https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalize-mobile-experiences-lowcode-flutter.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/get-personalization-decision-invocable-action-reference.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/data-model-object-reference.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-dmo.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-decision-dmo.html
- SP developer guide: https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-schema-dmo.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-log-dmo.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/personalization-point-click-attribution-dmo.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/experiment-dmo.html · https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/experimentation-log-dmo.html
- SP developer guide: https://developer.salesforce.com/docs/marketing/einstein-personalization/guide/batch-personalization-output-dmo.html
- Data 360 / SDK / object reference: https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent.html · https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-consent-data.html · https://developer.salesforce.com/docs/data/salesforce-interactions-sdk/guide/c360a-api-salesforce-interactions-web-sdk.html · https://developer.salesforce.com/docs/data/data-cloud-engagement-mobile-sdk/guide/c360a-api-engagement-mobile-sdk-consent-management-v3.html · https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-website-engagement-dmo.html
- Data 360 / SDK / object reference: https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-personalizationlogdmo-dmo.html · https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-abnexperimentlogdmo-dmo.html · https://developer.salesforce.com/docs/data/data-cloud-dmo-mapping/guide/c360dm-si-persnlrcmditemlogdmo-dmo.html · https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationPoint.htm · https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationDecision.htm
- Data 360 / SDK / object reference: https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_PersonalizationSchema.htm
- MCP pages cited only in MCP ≠ SP context: https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_sitemap_consent_mgmt.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_mcn_for_pers_benefits.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_about.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_limits.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_salesforce_crm_prereqs.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_machine_learning.htm&release=264.0.0&type=5 · https://help.salesforce.com/s/articleView?id=mktg.mc_pers_access_salesforce_setup.htm&release=264.0.0&type=5

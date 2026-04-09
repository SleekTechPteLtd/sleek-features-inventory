# Notify accounting team on questionnaire completion

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Notify accounting team on questionnaire completion |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (authenticated Sleek app user); System delivers Slack notification to accounting staff |
| **Business Outcome** | When regional configuration allows it, the accounting team is alerted in Slack as soon as the accounting questionnaire is completed, with company context and assigned accounting roles so setup can continue without delay. |
| **Entry Point / Surface** | Sleek API: `POST` `/v2/notify/send-slack-message` (mounted under `/v2/notify`); body `companyId` (required), `isTaxOnly` (optional boolean). Invoked from the client after accounting questionnaire completion (see tests and accounting onboarding comments). |
| **Short Description** | If the `send_slack_message_enabled` property under the customer feature `accounting_set_up` is enabled, the service loads the company, resolves the company owner and accounting resource roles (accounting manager, senior accountant, junior accountant), selects a CMS-configured message template based on whether all three roles are assigned and whether the flow is tax-only, then posts a payload to the internal Slack notifications service so Slack can notify the team with company name, entity type, and role-holder context. If the flag is off, the API returns success with a message that Slack notification is disabled for the region. |
| **Variants / Markets** | Unknown (gated per environment/region via CMS app features, not hard-coded to a country list in this controller) |
| **Dependencies / Related Flows** | `app-features-util` / Sleek CMS `AppFeatureService` (`accounting_set_up` → `send_slack_message_enabled`, template keys `default`, `resource-complete`, `resource-incomplete`); `accounting-workflow-util.sendSlackMessage` → HTTP `POST` to `${sleekSlackApiBaseUrl}/event/accounting-conclusion` with `SLACK_NOTIFICATIONS_API_KEY`; `company-resource-util.findCompanyResources` for staff assignment; accounting questionnaire and onboarding flows that call this endpoint after completion |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (read by id); `companyusers` (owner with `is_owner: true`, populated user for client email); `companyresourceusers` (with `user` and `resource_role` populated for accounting-manager, senior-accountant, junior-accountant) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm which client surfaces call this endpoint after questionnaire completion and whether `isTaxOnly` is still used in production paths. Template variable names in code comments refer to AFM/SA/JA while payload uses `accountManagerEmail`, `seniorAccountantEmail`, `accountingJuniorEmail`—confirm Slack service maps these consistently. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route** (`controllers-v2/send-slack-message.js`): `POST` `/send-slack-message` with `userService.authMiddleware`; validates `companyId` (string), optional `isTaxOnly`; rejects invalid `ObjectId` and missing company; reads `getAppFeatureList()` then `getAppFeaturePropByNameAndCategory(..., "accounting_set_up", "customer")` and `getAppFeatureProp(..., "send_slack_message_enabled")`; branches on `enabled`; builds emails via `CompanyUser.findOne({ company, is_owner: true }).populate("user")` and `companyResourceUtil.findCompanyResources(company._id, ["accounting-manager","senior-accountant","junior-accountant"])`; chooses `sendSlackMessageTemplates["resource-complete"]` vs `resource-incomplete` when not tax-only and when all three roles present vs not; default/humanized `company_type` via local `humanize`; calls `sendSlackMessage({ accountManagerEmail, seniorAccountantEmail, accountingJuniorEmail, clientEmail, companyName, companyType, template, ... })`.
- **Slack integration** (`utils/accounting-workflow-util.js`): `sendSlackMessage` merges task variables with `source` from `PLATFORM` + `NODE_ENV` and posts JSON to `config.sleekSlackApiBaseUrl` + `/event/accounting-conclusion` with `authorization: SLACK_NOTIFICATIONS_API_KEY` via `requestCreator.createRequestPromise`.
- **Feature flags** (`utils/app-features-util.js`): `getAppFeatureList`, `getAppFeatureProp`, `getAppFeaturePropByNameAndCategory` backed by `AppFeatureService` (CMS) or local mock in test.
- **Staff resolution** (`utils/company-resource-util.js`): `findCompanyResources` queries `CompanyResourceUser.find({ company })`, populates `user` and `resource_role`, filters non-deleted roles matching requested staff role types.
- **Tests** (`tests/controllers-v2/send-slack-message/send-slack-message.js`): documents `POST /v2/notify/send-slack-message`; stubs feature list with `send_slack_message_enabled` and template map; references accounting questionnaire routes in comments.

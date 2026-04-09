# Submit HubSpot marketing forms

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit HubSpot marketing forms |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (anonymous or identified) |
| **Business Outcome** | Marketing and sales capture leads in HubSpot with browser tracking context and optional contact or onboarding fields, without requiring a Sleek login. |
| **Entry Point / Surface** | `sleek-back` HTTP API: `POST /v2/crm-service/hsf`. Intentionally **unauthenticated** (auth middleware removed; reference ticket SA-13471) so embedded marketing surfaces and anonymous visitors can submit. Typically called from web or app clients that collect `hutk` and optional fields. |
| **Short Description** | The handler validates `hutk` (HubSpot tracking cookie) as required and optional `email`, then optionally validates onboarding and contact fields (`app_onboarding_version`, `app_onboarding_reason`, `firstname`, `lastname`, `company`, `phone`). It selects a HubSpot form GUID from config (default vs `saveForLater` when `formVersion === 3`) and posts to HubSpot’s form submissions API with `platform`, field payload, and `context.hutk`. Success returns HubSpot’s `inlineMessage`; HubSpot or validation failures map to generic error responses. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **External**: HubSpot Forms API `POST https://api.hsforms.com/submissions/v3/integration/submit/{portalId}/{formGuid}` with `Authorization: Bearer ${HUBSPOT_API_TOKEN}`; portal and form GUIDs from `config.hubspot`. **Same repo**: `services/crm-service.js` also implements `uploadContactToHubspot` (contacts API + `CompanyUser`) — a separate path from marketing form submissions. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None (this flow does not read or write MongoDB; HubSpot is the system of record for the submission). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app-router.js`

- **`router.use("/v2/crm-service", require("./controllers-v2/crm-service"))`** — base path `/v2/crm-service` for the router below.

### `controllers-v2/crm-service.js`

- **`POST /hsf`** → `getHubspotFormsHandler.executePostHubspotForms`. Comment: auth middleware removed so the API is callable without user auth (SA-13471).

### `controllers-v2/handlers/crm-service/hubspot-forms.js`

- **`executePostHubspotForms`**: `validationUtils.validateOrReject` — required `hutk` (string); optional `email` (string). Second validation block for optional `app_onboarding_version`, `app_onboarding_reason`, `firstname`, `lastname`, `company`, `phone`. Reads `config.hubspot.portalId`, `formGuid`; if `req.body.formVersion === 3`, uses `config.hubspot.saveForLaterformGuid`. Calls `postHubspotForms(hutk, email, portalId, formGuid, additionalFields)`. **200** → `{ message: response }` (HubSpot inline message). HubSpot promise rejection → generic `INVALID_REQUEST` with error payload. Catch-all → `INTERNAL_SERVER_ERROR`.

### `services/crm-service.js`

- **`postHubspotForms(hutk, email, portalId, formGuid, additionalFields)`**: Builds POST to `https://api.hsforms.com/submissions/v3/integration/submit/${portalId}/${formGuid}` with JSON body: `submittedAt`, `fields` starting with `platform` (`process.env.PLATFORM`), optional `email` and each present additional field, `context: { hutk }`. Uses `axios.post` with `Authorization: Bearer ${process.env.HUBSPOT_API_TOKEN}`. On **200**, returns `response.data.inlineMessage`; otherwise throws/logs HubSpot error payload.

### `tests/controllers-v2/crm-service/hubspot-forms.js`

- **`POST /v2/crm-service/hsf`**: nocks `api.hsforms.com` form submit; asserts **200** and `message` equals mocked `inlineMessage`; second case adds `app_onboarding_reason`.

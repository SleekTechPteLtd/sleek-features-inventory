# Load workflow RAF payload

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Load workflow RAF payload |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing / compliance admin (authenticated staff opening the CDD Answers page) |
| **Business Outcome** | Staff can review how customer due diligence inputs map onto the Risk Assessment Form (RAF) for a given company workflow by loading the correct RAF object from API-backed workflow and company data. |
| **Entry Point / Surface** | **sleek-website** admin standalone page `/admin/sleek-workflow/cdd-answers/?companyWorkflowId=…` (webpack entry `admin/sleek-workflow/cdd-answers`). Also reachable via link from the incorporation RAF task UI (`incorp-company-risk-assessment-form.js` → `href` with `companyWorkflowId`). |
| **Short Description** | On mount, reads `companyWorkflowId` from the query string, calls `getCompanyWorkflowById` then `getCompany` for the workflow’s company id. Chooses a nested RAF key: `cdd_incorporation_raf` when `workflow_type` is the CDD process (`customer-due-diligence`), otherwise `transfer_raf` or `incorporation_raf` from `company.is_transfer`. Sets React state from `response.data.data[taskKey]` and renders tabs over `sections[1]` and `sections[2]` (slices index 1–2), questions, factors, scores, and `raf_generated_at`. |
| **Variants / Markets** | **Multi-tenant** workflow types include CDD Refresh and SG Transfer (`camunda-workflow-constants` table). Typical Sleek markets **SG, HK, UK, AU**; which workflows populate which RAF keys per tenant is **Unknown** from this frontend pass. |
| **Dependencies / Related Flows** | **API**: `getCompanyWorkflowById` → `GET /v2/sleek-workflow/company-workflows/:companyWorkflowId`; `getCompany` → `GET /companies/:companyId`. **Constants**: `CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` (`customer-due-diligence`) vs incorporation/transfer keys. **Upstream**: Camunda workflow data shape under `data.*`; **related UI**: `cdd_incorporation_raf` task metadata in `camunda-customer-due-diligence.js`. **Backend**: sleek-back (or workflow service) persists company workflow payload — not read here. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`, `src/views/admin/sleek-workflow/services/api-camunda.js` (`getCompanyWorkflowById`), `src/utils/api.js` (`getCompany`), `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js` (re-exports `CUSTOMER_DUE_DILIGENCE`), `src/views/admin/sleek-workflow/constants/workflow-constants/camunda-customer-due-diligence.js`. |
| **DB - Collections** | **Unknown** from these views (all data via REST). Company workflow and company records are persisted server-side; no MongoDB collection names in the listed files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `cdd_sba_raf` or other RAF keys should appear in this viewer (only three keys are branched in `getTaskDefinitionKey`). Exact API auth surface for `GET /v2/sleek-workflow/company-workflows/:id` and `GET /companies/:id` for this route. Whether slicing `sections` to `[1,2]` is intentional for all markets. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`

- **Query param**: `companyWorkflowId` from `URLSearchParams(window.location.search)`; error if missing.
- **RAF key selection** (`getTaskDefinitionKey`): if `workflowData.workflow_type === CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` → `"cdd_incorporation_raf"`; else `companyDetails.is_transfer ? "transfer_raf" : "incorporation_raf"`.
- **Payload extraction**: `setRafData(get(response, \`data.data.${taskDefinitionKey}\`))` after workflow and company responses.
- **Empty states**: no `rafData`, no `sections`, empty `sections`, or missing `raf_generated_at` → “RAF assessment not generated yet” or “No RAF data available”.
- **Render**: `rafData.sections.slice(1, 3)` drives two tabs; Material-UI `Tabs` / `Tab`; nested `Factor` for `factors` / recursive `factor.factors`; `moment` formats `raf_generated_at`.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getCompanyWorkflowById`**: `GET ${getBaseUrl()}/v2/sleek-workflow/company-workflows/${params.companyWorkflowId}` via `getResource` (shared headers / `checkResponseIfAuthorized` in `handleResponse`).

### `src/utils/api.js`

- **`getCompany(companyId)`**: `GET ${getBaseUrl()}/companies/${companyId}` (optional `?load[]=fye`); used only to read `is_transfer` for non-CDD workflow types in this flow.

### `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`

- **`CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE`**: imported from `camunda-customer-due-diligence.js`; **`PROCESS_INSTANCE_KEY`** is `"customer-due-diligence"` (used for the CDD branch in `getTaskDefinitionKey`).

### `src/views/admin/sleek-workflow/constants/workflow-constants/camunda-customer-due-diligence.js`

- Documents task **`cdd_incorporation_raf`** (Company RAF) alongside `cdd_form_submission` and `cdd_sba_raf`; confirms naming alignment with the viewer’s CDD branch.

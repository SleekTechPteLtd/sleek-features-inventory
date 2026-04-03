# Review CDD answers for RAF impact

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review CDD answers for RAF impact |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal admin (compliance, risk, and operations staff using the Sleek admin area) |
| **Business Outcome** | Internal users can see how customer due diligence questionnaire answers and scores roll up into Risk Assessment Form (RAF) sections for incorporation or transfer workflows, supporting compliance and risk review. |
| **Entry Point / Surface** | **sleek-website** admin standalone page: **`/admin/sleek-workflow/cdd-answers/?companyWorkflowId=<id>`** (webpack bundle `admin/sleek-workflow/cdd-answers`). Often opened from the incorporation RAF task UI via a new-tab link that passes `companyWorkflowId` (`incorp-company-risk-assessment-form.js`). |
| **Short Description** | Reads `companyWorkflowId` from the query string, loads the company workflow (`GET /v2/sleek-workflow/company-workflows/:id`) and company (`GET /companies/:id`), then selects the RAF payload key: `cdd_incorporation_raf` for CDD Refresh workflows (`workflow_type === customer-due-diligence`), otherwise `transfer_raf` or `incorporation_raf` from `company.is_transfer`. Renders “CDD Answers” / “Impact on RAF” with generation time, two tabs over `sections[1]` and `sections[2]` only, and nested questions, factors, formatted answers, and optional per-answer scores. |
| **Variants / Markets** | **Multi-tenant** via API-backed workflow and company data; workflow list includes CDD Refresh and SG Transfer among others. Typical Sleek markets **SG, HK, UK, AU**; exact RBAC and which tenants populate which RAF keys — **Unknown** without backend review. |
| **Dependencies / Related Flows** | **API**: `getCompanyWorkflowById` → `/v2/sleek-workflow/company-workflows/:companyWorkflowId`; `getCompany` → `/companies/:companyId`. **Constants**: `CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` (`customer-due-diligence`) in `camunda-workflow-constants.js` (re-exports `camunda-customer-due-diligence.js`). **Upstream**: Camunda workflows that persist `data.cdd_incorporation_raf`, `data.incorporation_raf`, or `data.transfer_raf` on the company workflow. **Related**: `regenerateRAFAnswers` in `api-camunda.js` (separate risk-assessment endpoint; not called by this read-only view). **Note**: CDD workflow also defines `cdd_sba_raf` in constants; this viewer only branches the three keys above in `getTaskDefinitionKey`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`, `src/views/admin/sleek-workflow/cdd-answers/index.js`, `src/views/admin/sleek-workflow/services/api-camunda.js` (`getCompanyWorkflowById`), `src/utils/api.js` (`getCompany`), `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`. **sleek-back** (or workflow service): implements REST payloads — not read in this pass. |
| **DB - Collections** | **Unknown** from these views (all data via REST; no MongoDB references in the listed files). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Why only `rafData.sections.slice(1, 3)` (first section omitted); whether SBA RAF (`cdd_sba_raf`) should be surfaced in a similar viewer. Which server permission guards `GET /v2/sleek-workflow/company-workflows/:id` and `GET /companies/:id` for this page. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry / webpack

- **`webpack/paths.js`**: entry `admin/sleek-workflow/cdd-answers` → `./src/views/admin/sleek-workflow/cdd-answers/index.js`.
- **`webpack/webpack.common.js`**: outputs `admin/sleek-workflow/cdd-answers/index.html` with chunks `admin/sleek-workflow/cdd-answers`, `vendor`.

### `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`

- **Query**: `companyWorkflowId` from `URLSearchParams(window.location.search)`; if missing → error “Company Workflow ID is required”.
- **Load sequence**: `getCompanyWorkflowById({ companyWorkflowId })` → `companyId` from `response.data.company` → `getCompany(companyId)` for `companyDetails`.
- **`getTaskDefinitionKey(workflowData, companyDetails)`**: if `workflowData.workflow_type === CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` → `"cdd_incorporation_raf"`; else `companyDetails.is_transfer ? "transfer_raf" : "incorporation_raf"`.
- **State**: `setRafData(get(response, \`data.data.${taskDefinitionKey}\`))`.
- **Empty / not ready**: requires non-empty `rafData.sections` and `rafData.raf_generated_at`; messages “RAF assessment not generated yet” vs “No RAF data available”.
- **UI**: Header “CDD Answers”, subtitle “Impact on RAF”, `moment(rafData.raf_generated_at)` timestamp. `filteredSections = rafData.sections.slice(1, 3)` — two Material-UI tabs from section indices 1–2 only; `tabIndex` initial `1`.
- **`Factor`**: Renders `factor.question`, `formatAnswer` on `answerObj.answer` (arrays joined, booleans Yes/No), optional `answerObj.score`, recursive `factor.factors`.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`getCompanyWorkflowById`**: `GET ${getBaseUrl()}/v2/sleek-workflow/company-workflows/${params.companyWorkflowId}` via `getResource` / `handleResponse` (`checkResponseIfAuthorized`, default headers).

### `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`

- **`CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE`**: imported from `workflow-constants/camunda-customer-due-diligence.js`.
- **`CAMUNDA_WORKFLOW_TABLE_CONSTANTS.WORKFLOW_TYPE`**: lists “CDD Refresh” (`customer-due-diligence`) and “Transfer” (`sg-transfer`) among workflow types (context for internal workflow browsing).

### `src/views/admin/sleek-workflow/constants/workflow-constants/camunda-customer-due-diligence.js`

- **`PROCESS_INSTANCE_KEY`**: `"customer-due-diligence"`.
- **`TASK_DATA.CDD_INCORPORATION_RAF`**: `task_definition_key` / `doneness_key` `cdd_incorporation_raf`; RAF copy references “Company Risk Assessment Form (RAF)”.

### Cross-link from workflow task UI

- **`src/views/admin/sleek-workflow/workflow-task/tasks/common-incorporation/incorp-raf-components/incorp-company-risk-assessment-form.js`**: `href` to `/admin/sleek-workflow/cdd-answers/?companyWorkflowId=${processSavedData._id}` with `target="_blank"` (per existing inventory evidence).

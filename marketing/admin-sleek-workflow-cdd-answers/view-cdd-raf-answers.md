# View CDD RAF answers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | View CDD RAF answers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Marketing admin (authenticated staff using the Sleek admin area) |
| **Business Outcome** | Staff can open a standalone read-only page to review Customer Due Diligence questionnaire answers, per-answer scores, and how they affect the Risk Assessment Form (RAF), with a clear generation timestamp for auditability. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/sleek-workflow/cdd-answers/?companyWorkflowId=<id>`** — standalone bundle (`#root`); opened in a new tab from the incorporation RAF UI via a “view log” style link that passes `companyWorkflowId` (`incorp-company-risk-assessment-form.js`). |
| **Short Description** | Reads `companyWorkflowId` from the query string, loads the company workflow via `GET /v2/sleek-workflow/company-workflows/:id`, then loads company details via `GET /companies/:companyId` to choose which RAF payload key to read (`cdd_incorporation_raf` for CDD workflows, otherwise `transfer_raf` vs `incorporation_raf` from `is_transfer`). Renders **two Material-UI tabs** from `rafData.sections` (slices indices 1–2 only), each tab listing questions with nested factors, formatted answers, and optional scores; shows **“Generated on”** from `raf_generated_at`. |
| **Variants / Markets** | **Multi-tenant** via company/workflow data from sleek-back; typical Sleek markets **SG, HK, UK, AU**. Exact RBAC on `company-workflows` and which workflows populate RAF keys — **Unknown** without sleek-back review. |
| **Dependencies / Related Flows** | **API**: `getCompanyWorkflowById` → `/v2/sleek-workflow/company-workflows/:companyWorkflowId`; `getCompany` → `/companies/:companyId`. **Constants**: `CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` for workflow type; RAF task keys in `camunda-customer-due-diligence.js`. **Upstream**: CDD / incorporation RAF tasks that persist `data.<rafKey>` on the workflow. **Related**: `regenerateRAFAnswers` in `api-camunda.js` (separate endpoint; not invoked by this read-only view). |
| **Service / Repository** | **sleek-website**: `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`, `src/views/admin/sleek-workflow/cdd-answers/index.js`, `src/views/admin/sleek-workflow/services/api-camunda.js`, `src/utils/api.js`, `src/views/admin/sleek-workflow/constants/camunda-workflow-constants.js`, `src/views/admin/sleek-workflow/constants/workflow-constants/camunda-customer-due-diligence.js`. **sleek-back** (or workflow service): implements `/v2/sleek-workflow/company-workflows/*` and company payloads — **not read in this pass**. |
| **DB - Collections** | **Unknown** from these views (all data via REST). Persistence is server-side; no MongoDB references in the listed files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Why only `sections.slice(1, 3)` (first section omitted); whether tab labels always match product expectation when backend adds/removes sections. Which server permission guards `GET /v2/sleek-workflow/company-workflows/:id` for this page. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry / webpack

- **`webpack/paths.js`**: entry `admin/sleek-workflow/cdd-answers` → `./src/views/admin/sleek-workflow/cdd-answers/index.js`.
- **`webpack/webpack.common.js`**: outputs `admin/sleek-workflow/cdd-answers/index.html` with chunks `admin/sleek-workflow/cdd-answers`, `vendor`.

### `src/views/admin/sleek-workflow/cdd-answers/index.js`

- `domready` → `ReactDOM.render(<CDDAnswers />, document.querySelector("#root"))`; imports `cdd-answers.css`.

### `src/views/admin/sleek-workflow/cdd-answers/cdd-answers.js`

- **Query param**: `companyWorkflowId` from `URLSearchParams(window.location.search)`; if missing → error “Company Workflow ID is required”.
- **Load**: `getCompanyWorkflowById({ companyWorkflowId })`; `companyId` from `response.data.company`; `getCompany(companyId)` for `companyDetails`.
- **RAF key selection** (`getTaskDefinitionKey`): if `workflowData.workflow_type === CAMUNDA_WORKFLOW_CONSTANTS.CUSTOMER_DUE_DILIGENCE.PROCESS_INSTANCE_KEY` (`customer-due-diligence`) → `cdd_incorporation_raf`; else `companyDetails.is_transfer ? "transfer_raf" : "incorporation_raf"`.
- **Payload**: `setRafData(get(response, \`data.data.${taskDefinitionKey}\`))`.
- **Empty / not ready**: requires `rafData.sections` non-empty and `rafData.raf_generated_at`; messages “RAF assessment not generated yet” vs “No RAF data available”.
- **Tabs**: `filteredSections = rafData.sections.slice(1, 3)` — **two tabs** from section indices 1 and 2 only; `Tabs` `value={tabIndex - 1}`, `onChange` sets `tabIndex` (initial `useState(1)` → first tab selected).
- **Rendering**: Per section, maps `rafSection.questions`; each question renders `Factor` recursively for `factors`; `Factor` prints `factor.question`, `answerObj.answer` (via `formatAnswer` for array/boolean/string), and `answerObj.score` when defined.
- **Header**: title “CDD Answers”, subtitle “Impact on RAF”, timestamp `moment(rafData.raf_generated_at).format('DD MMM YYYY; HH:mm:ss Z')`.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- `getCompanyWorkflowById`: `GET ${base}/v2/sleek-workflow/company-workflows/${params.companyWorkflowId}`.

### `src/utils/api.js`

- `getCompany`: `GET ${base}/companies/${companyId}`.

### Cross-link from workflow task UI

- `src/views/admin/sleek-workflow/workflow-task/tasks/common-incorporation/incorp-raf-components/incorp-company-risk-assessment-form.js`: `href={\`/admin/sleek-workflow/cdd-answers/?companyWorkflowId=${processSavedData._id}\`}` with `target="_blank"`.

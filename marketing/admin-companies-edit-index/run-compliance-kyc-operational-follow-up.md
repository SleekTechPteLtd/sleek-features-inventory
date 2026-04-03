# Run compliance KYC and operational follow-up

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Run compliance KYC and operational follow-up |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Internal support staff (Sleek Admin — company edit access) |
| **Business Outcome** | Internal staff can advance per-person and company-level KYC, spin up or open Camunda-backed workflows, record and extend corporate compliance deadlines (AGM/annual return style), and keep an auditable comment thread on the company so regulatory and service tasks stay visible and completed. |
| **Entry Point / Surface** | **Sleek Admin** → **Company edit** at `/admin/companies/edit/?cid=<companyId>` (optional `tab=comments`, `editUserFunction` / `editUserId` for workflow handoff). **Deadline Management** sub-view: primary **Deadlines** button toggles inline `Deadlines` panel (same route). **Comments**: tab/link on company edit opens comments panel; URL `?cid=…&tab=comments`. **Workflows**: deep links from KYC/incorporation tasks to company edit; **Workflow list** for Camunda tasks after `handleStartKyc` / incorporation start. |
| **Short Description** | On the company edit shell, operations users work **Sleek KYC** sections (`CompanySleekKycSection`, v2 status via `getKycStatusV2` / `updateCompanyUserKycStatusV2`), start or align **KYC workflows** (`handleStartKyc` from `workflow-util`, HK KYC CMS flags, `getKycCompanyWorkflows` for active instances), optionally trigger **Camunda** processes (e.g. HK incorporation via `startProcess` + `CAMUNDA_WORKFLOW_CONSTANTS`, open workflow task in new tab). **Internal comments** load and post through Sleek Auditor (`getCompanyComments` / `postCompanyComment`, paginated). **Regulatory deadlines** use the embedded `Deadlines` component: load AGM/annual-return-related dates via `getAGMDeadlines`, create/update typed deadlines via `postDeadline` / `putDeadline`. **CS workflow** entry via `CSWorkflowButton` when CMS `workflow` is enabled. |
| **Variants / Markets** | Behaviour gated by CMS (`sleek_kyc`, `kyc_refresh`, `hk_kyc_workflow`, `kyc_raf`, `workflow`, onboarding bypass flags). Typical Sleek markets **SG, HK, UK, AU**; exact tenant toggles — use **Unknown** where not confirmed from this client. |
| **Dependencies / Related Flows** | **HTTP (sleek-website `api.js`)**: `GET /admin/companies/:id`, `GET /admin/companies/:id/get-agm-deadlines`, `POST /admin/companies/:id/deadlines`, `PUT /admin/companies/:id/deadlines/:deadlineId` — company and deadline persistence (backend sleek-back). **Sleek Auditor** (`api-sleek-auditor.js`): `GET`/`PUT` `…/v2/sleek-auditor/api/log/company/:companyId/comment/`. **WFE** (`api-wfe.js`): `getKycCompanyWorkflows` → `GET /v2/workflow/api/company-workflows/:companyId/kyc/`. **Camunda** (`api-camunda.js`): `POST /v2/sleek-workflow/:processName/start` (e.g. HK incorporation RAF). **Related inventory**: `marketing/admin-sleek-workflow-workflow-task/work-client-camunda-workflows-from-admin.md`, `marketing/admin-companies-edit-index/maintain-company-registration-profile.md` (parent page). |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/index.js`, `src/views/admin/companies/edit/deadlines.js`, `src/utils/api.js`, `src/utils/api-sleek-auditor.js`, `src/utils/api-wfe.js`, `src/views/admin/sleek-workflow/services/api-camunda.js`, `src/utils/workflow-util.js`, `src/components/company-sleek-kyc-section`, `src/views/admin/workflow/cs-workflow-button`. **sleek-back / workflow / auditor services** (not in this repo): REST handlers behind the above paths. |
| **DB - Collections** | Unknown (persistence not defined in sleek-website; likely Company, CompanyUser, deadline and audit-log collections on backend). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC on company edit vs comments vs deadline writes; whether all markets use the same AGM/AR deadline types; full mapping of `CompanySleekKycSection` API surface without reading that component file. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/edit/deadlines.js` (`Deadlines`)

- **Data load**: `componentDidMount` → `reloadCommonData` → `fetchCommonData`: **`api.getAGMDeadlines(companyId)`**, **`api.getCompany(companyId)`** — hydrates `lastAgmDeadLine`, `extendedAgmDeadLine`, `dateAgmHeld`, `lastAnnualReturnDeadLine`, `extendedAnnualReturn`, `dateAnnualReturnFiled`, and `company.financial_year`.
- **Updates**: `handleSubmitUpdateDeadline` → JSON body `{ type, deadline_at }` — **`api.putDeadline(companyId, deadlineId, { body })`** or **`api.postDeadline(companyId, { body })`** when no `_id`. Types include `extended_annual_general_meeting`, `date_annual_general_meeting_held`, `extended_annual_return`, `date_annual_return_filed`.
- **UI**: Blueprint `DateInput` + Submit per editable row; snackbar on success; optional Back (`handleClickBackButton`).

### `src/views/admin/companies/edit/index.js` (`AdminCompaniesEditView`)

- **Comments**: `loadCommentsAndHistory` / `handleShowCommentsAndHistory` — **`getCompanyComments({ companyId, skip })`**; `handlePostComment` — **`postCompanyComment`** with `entry_type: "comment"`, author from `user`, `text`; `history.pushState` for `tab=comments`; load-more pagination (`skip` += 20).
- **KYC & workflows**: Imports **`CompanySleekKycSection`**, **`handleStartKyc`**; state `kycCompanyWorkflows`; **`apiWfe.getKycCompanyWorkflows`** in load path (`workflowType: "kyc"`); **`getCamundaKycWorkflow(companyUserId)`**; KYC refresh tab label when `kyc_refresh` CMS + `KYC_STATUSES_V2`; **`updateCompanyUserKycStatusV2`** for status pushes; dialogs directing staff to **Workflow list** after starting KYC.
- **Camunda**: **`startProcess`** from `api-camunda` — e.g. `handleStartHKIncorporation` with `CAMUNDA_WORKFLOW_CONSTANTS.HK_INCORPORATION.PROCESS_INSTANCE_KEY`, body `company_id`, `company_name`, `is_via_raf_button`; `window.open` to `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…` for incorporation / risk assessment handoff.
- **CS workflow**: **`CSWorkflowButton`** when `workflow.enabled` from CMS.
- **Deadlines embed**: `handleClickDeadlines` toggles `deadlinesPageIsVisible`; **`renderBodyContent`** when true returns **`<Deadlines company={…} user={…} handleClickBackButton={handleClickDeadlines} />`** (replacing main body); primary **Deadlines** button in toolbar (alongside other company actions).

### `src/utils/api.js` (deadlines + company)

- **`getAGMDeadlines`**: `GET ${base}/admin/companies/:companyId/get-agm-deadlines`
- **`postDeadline`**: `POST ${base}/admin/companies/:companyId/deadlines`
- **`putDeadline`**: `PUT ${base}/admin/companies/:companyId/deadlines/:deadlineId`

### `src/utils/api-sleek-auditor.js`

- **`getCompanyComments` / `postCompanyComment`**: `…/v2/sleek-auditor/api/log/company/:companyId/comment/` (GET list; PUT-style post for new comment per implementation).

### `src/utils/api-wfe.js`

- **`getKycCompanyWorkflows`**: `GET /v2/workflow/api/company-workflows/:companyId/kyc/` with query `admin`, optional `companyUserId`, `businessKey`.

### `src/views/admin/sleek-workflow/services/api-camunda.js`

- **`startProcess`**: `POST ${base}/v2/sleek-workflow/${processName}/start`

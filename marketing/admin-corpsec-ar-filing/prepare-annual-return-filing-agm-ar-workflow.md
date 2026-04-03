# Prepare annual return filing from AGM and AR workflow

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Prepare annual return filing from AGM and AR workflow |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (Sleek admin users working the Corpsec AR filing surface). |
| **Business Outcome** | Staff can pull the right company and **AGM & AR** Camunda workflow, consolidate workflow-linked and ad hoc uploads, choose which files feed generation, and proceed to ACRA-oriented annual return preparation without hunting across unrelated workflows. |
| **Entry Point / Surface** | **sleek-website** admin: **Corpsec → AR Filing** — `/admin/corpsec/ar-filing/` (`AdminLayout`, `sidebarActiveMenuItemKey="corpsec"`, `sidebarActiveMenuSubItemKey="ar-filing"`). Optional query: `?cid={companyId}` and `?processId={camundaProcessId}` (e.g. deep link from AGM & AR workflow task). |
| **Short Description** | Operators search and select a company, then pick an **AGM & AR** workflow instance (filtered from WFE Camunda workflows by title containing `AGM & AR`). The UI loads workflow document IDs from corpsec AR filing APIs, resolves file metadata, classifies rows (partially signed, signed, financial statement), and auto-selects filenames unless excluded by CMS `ar_filing` regex rules. They can upload additional PDF/images, toggle which workflow and manual files participate, then trigger answer generation (payload: `fileIds` + `manuallyUploadedFileIds`). |
| **Variants / Markets** | **SG** (ACRA annual return and workflow copy are Singapore corporate secretary context). Other markets not encoded in this view — **Unknown** if the same page is reused elsewhere. |
| **Dependencies / Related Flows** | **WFE**: `getCompanyWorkflows` with `includedWorkflows: ["camunda"]` — workflow list and `processId` from workflow URL. **Main API (corpsec v2)**: `GET /v2/corpsec/ar-filing/{companyId}/processes/{processId}`, `GET .../documents`, `POST .../generate-answers`, `POST .../upload-document`, `POST .../update-status`, plus file service `getFileDetails`, `deleteFile`. **CMS**: `ar_filing` feature (`document_exclusion_regex_patterns`, answer `response_format.schema`). **Related**: admin **Sleek Workflow** task UI links to this page (`/admin/sleek-workflow/workflow-task/`); **Go to Workflow** opens workflow task by `processId`. Downstream: answer review, ACRA submission details, retry flows (other components on same page). |
| **Service / Repository** | **sleek-website**: `src/views/admin/corpsec/ar-filing/index.js`, components under `src/views/admin/corpsec/ar-filing/components/`. **Backend**: corpsec AR filing and file APIs (not in this repo). |
| **DB - Collections** | **Unknown** from sleek-website; persistence for AR filing state and files lives behind `/v2/corpsec/ar-filing/...` and file endpoints. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC for `/v2/corpsec/ar-filing` vs general admin. Whether non-SG companies can appear in the workflow list with different titles. Backend retention when manual uploads are deleted via `deleteFile`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/corpsec/ar-filing/index.js` (`ARFilingView`)

- **Bootstrap**: `getPlatformConfig` → `ar_filing` CMS feature for `answerSchema` and `document_exclusion_regex_patterns`; `getUser` from admin common.
- **URL**: `queryString.parse` → `cid`, `processId`; `setUrlParams` syncs `cid` / `processId` on company/workflow change.
- **Companies**: `api.getCompanies` / `api.fetchCompany`; `getCompanies` default `limit: 10`.
- **Workflows**: `getCompanyWorkflows({ companyId, includedWorkflows: ["camunda"] })`; keeps workflows whose `title` includes `AGM_AR_TITLE` (`"AGM & AR"`), labels `AGM & AR {financial_year_end}`, `value` = `processId` from workflow `url`.
- **AR filing load**: `api.getAnnualReturnFiling`, `api.getAnnualReturnFilingDocuments` → merges `partiallySignedFileIds`, `signedFileIds`, `financialStatementFileIds` into `workflowDocumentIds`; `fetchSourceDocuments` calls `api.getFileDetails` per id; `shouldAutoSelectDocument` uses exclusion regexes; `fetchManuallyUploadedDocuments` hydrates saved manual ids from filing record.
- **Manual upload**: `api.uploadARFilingDocument(companyId, FormData)`; `api.deleteFile` for manual removal.
- **Generate**: `api.generateAnnualReturnFilingAnswers` with body `{ fileIds, manuallyUploadedFileIds }`; polling via `getAnnualReturnFiling` when status `pending`.
- **Retry editing**: `api.updateStatusAnnualReturnFiling` with `status: staff_reviewing` (constant `AR_FILING_STATUSES`).

### `src/views/admin/corpsec/ar-filing/components/CompanySelector.js`

- React-select with debounced search: `onSearchCompanies` → `api.getCompanies` via parent with `query: { name, limit: 10 }`, `admin: true`; link to `/admin/company-overview/?cid=...`.

### `src/views/admin/corpsec/ar-filing/components/WorkflowSelector.js`

- Disabled when no `companyId`, loading, or empty workflows; displays loading / empty placeholders.

### `src/views/admin/corpsec/ar-filing/components/DocumentList.js`

- Renders only when `selectedWorkflow` set; checkboxes for `selectedDocumentsForFiling`; labels `documentType` (partially-signed, signed, financial-statement); **Go to Workflow** → `onGoToWorkflow` (`/admin/sleek-workflow/workflow-task/?processId=`); `FileActions` for preview/actions.

### `src/views/admin/corpsec/ar-filing/components/ManualUploadSection.js`

- Hidden without `selectedWorkflow`; file input `accept=".pdf,.jpg,.jpeg,.png"`, multiple; upload disabled when `annualReturnFilingData.status === "submitted"`; lists manual docs with select/delete (when allowed) and `FileActions`.

### `src/utils/api.js`

- Endpoints: `GET ${getBaseUrl()}/v2/corpsec/ar-filing/${companyId}/processes/${processId}/documents`, same base path for process resource, `POST .../generate-answers`, `POST .../upload-document`, `POST .../update-status`, etc.

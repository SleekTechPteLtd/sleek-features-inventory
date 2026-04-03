# Review client KYC activity

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Review client KYC activity |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin / operations staff (Sleek Admin users who open the KYC Activity screen for a client user) |
| **Business Outcome** | Staff can see a person’s KYC-related events across their companies, filter the timeline, and jump into validation or Camunda KYC workflows when action is required—supporting compliance review and operational follow-up. |
| **Entry Point / Surface** | **sleek-website** admin: **KYC Activity** at `/admin/kyc-activity/` with required query **`userId`** (e.g. linked from company overview: `/admin/kyc-activity/?userId=…&companyIds=…`). `AdminLayout` with `sidebarActiveMenuItemKey="companies"`, `workflowPage`, drawer hidden. |
| **Short Description** | Loads **platform config** (`getPlatformConfig` / `kyc_activity` app feature) to build **Purpose of KYC** filter options from CMS `purpose_of_kyc`. Loads the client’s **company memberships** via `getCompanyUsersFromUserId` for the **Company name** multi-select. Fetches a **POST** body with sort direction, date range (`dateFrom`/`dateTo`), selected `companyIds`, and `purposesOfKyc`, then renders events **grouped by calendar year** with date/time, company name, purpose, and HTML **content**. Row actions depend on latest row + invitation/KYC/refresh state: **START KYC** (`handleStartKyc`), **REVIEW KYC** / **VIEW KYC** (`getKycCompanyWorkflows` → `redirectToKycWorkflow` to sleek-workflow task UI or legacy new-workflow). URL query is kept in sync with filters via `history.replaceState`. |
| **Variants / Markets** | **Unknown** — KYC purpose labels are CMS-driven; underlying KYC flows vary by tenant (e.g. UK vs default in `kyc-status-utils` is unrelated to this page’s list API). |
| **Dependencies / Related Flows** | **`getKYCActivity`**: `POST {base}/v2/company-users/kyc-activity/{userId}` with JSON body (`sort`, `dateFrom`, `dateTo`, `companyIds`, `purposesOfKyc`). **`getCompanyUsersFromUserId`**: `GET {base}/users/{userId}/company-users`. **`getPlatformConfig`**: `kyc_activity` / `purpose_of_kyc` for filter labels. **`handleStartKyc`** (`workflow-util`): Camunda `startProcess` for KYC or legacy **`startKyc`** (`api-wfe`), Onfido report generation when enabled, `updateCompanyUserKycStatus`, audit log. **`getKycCompanyWorkflows`**: `GET {base}/v2/workflow/api/company-workflows/{companyId}/kyc/?admin=true&companyUserId=…`. **`redirectToKycWorkflow`**: opens `/admin/sleek-workflow/workflow-task/` or `/admin/new-workflow/?companyId=…&workflow=kyc`. Upstream: company-user / workflow services (not in this repo). |
| **Service / Repository** | **sleek-website**: `src/views/admin/kyc-activity/index.js`, `src/views/admin/kyc-activity/kyc-activity.js`, `src/utils/api.js`, `src/utils/api-wfe.js`, `src/utils/workflow-util.js`, `src/utils/kyc-status-utils.js`. **Backend** (not in repo): company-users KYC activity aggregation, workflow engine. |
| **DB - Collections** | **Unknown** from this frontend — persistence is behind **v2** APIs and workflow services. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-admin roles are restricted server-side for `kyc-activity` and workflow admin endpoints (not visible in these files). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/kyc-activity/index.js`

- **Shell**: `domready` → `ReactDOM.render` `<KYCActivity />`; `getUser` from admin common; passes `user` to `AdminLayout` with `sidebarActiveMenuItemKey="companies"`, `hideDrawer`, `workflowPage`, `uiStretchVertically`.
- **Body**: Renders `KYCActivityContent`.

### `src/views/admin/kyc-activity/kyc-activity.js` (`KYCActivityContent`)

- **Query**: Parses `userId`, `companyIds` (comma list), `purposesOfKyc`, `sort`, `dateFrom`, `dateTo` from `window.location.search`.
- **Config**: `getPlatformConfig({ platform: "admin" })` → `getAppFeatureProp(..., "kyc_activity").value.purpose_of_kyc` → checkbox options; if no `purposesOfKyc` in URL, selects all purposes.
- **Companies**: `getCompanyUsersFromUserId(query.userId)` populates company filter options.
- **Data**: When `platformConfig` is set, `getKYCActivity(userId, { body: JSON.stringify({ sort, dateFrom, dateTo, companyIds, purposesOfKyc }) })` — items grouped by year via `lodash/groupBy` on `createdAt`; displays `user` name from response.
- **URL sync**: `replaceState` with `userId`, `sort`, `dateFrom`, `dateTo`, `companyIds`, `purposesOfKyc`.
- **Actions**: `handleStartKYC` → `handleStartKyc` from `workflow-util`; `handleViewKYC` → `apiWfe.getKycCompanyWorkflows({ companyId, companyUserId, isAdmin: true })` then `redirectToKycWorkflow`. `resolveButton` uses `KYC_STATUSES_V2` for READY_FOR_VALIDATION, `kycRefresh` in-progress vs started, verified, etc.

### `src/utils/api.js`

- **`getKYCActivity`**: `POST ${getBaseUrl()}/v2/company-users/kyc-activity/${userId}`.
- **`getCompanyUsersFromUserId`**: `GET ${getBaseUrl()}/users/${userId}/company-users`.

### `src/utils/api-wfe.js`

- **`getKycCompanyWorkflows`**: `GET /v2/workflow/api/company-workflows/{companyId}/kyc/?admin={isAdmin}` with optional `companyUserId`, `businessKey` query params.

### `src/utils/workflow-util.js`

- **`handleStartKyc`**: Resolves Camunda vs legacy KYC from `camunda_workflow` / `kyc` feature; may call `generateOnfidoReport`; **`handleStartCamundaKyc`** → `startProcess` with `CAMUNDA_WORKFLOW_CONSTANTS.KYC.PROCESS_INSTANCE_KEY`; else **`startKyc`** from `api-wfe`, `regenerateCompanyUserNamecheckReport`, `kycRecordAuditLog`, `updateCompanyUserKycStatus` with `kyc_trigger_status: "started"`.

### `src/utils/kyc-status-utils.js`

- **`redirectToKycWorkflow`**: If workflow present, `window.open` `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…`; else `/admin/new-workflow/?companyId=…&workflow=kyc`.

### Other references

- **`src/views/admin/company-overview/index.js`**: Navigates to `/admin/kyc-activity/?userId=${userId}&companyIds=${companyId}`.
- **Supporting UI**: `src/views/admin/kyc-activity/select-checkbox-with-all.js` (company and purpose multi-selects).

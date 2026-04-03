# Bulk trigger CDD from CSV

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Bulk trigger CDD from CSV |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance (Admin) |
| **Business Outcome** | Compliance can queue Customer Due Diligence (CDD) refresh for many companies in one action by uploading a CSV of company IDs, instead of triggering workflows one company at a time. |
| **Entry Point / Surface** | Sleek Admin > **Manage Workflows** > **CDD Workflows** (`/admin/cdd-workflows/`) — **Bulk Trigger CDD** in the page header (next to the “CDD Workflows” title and description). |
| **Short Description** | Opens a modal that checks for an in-progress bulk upload (via ongoing-upload API); if none, accepts a CSV where column A lists one MongoDB-style company ObjectId per row (24 lowercase hex). Validates client-side, then `POST`s the file to the workflow service. On success, returns a batch id and optionally loads per-company status; the parent page shows a toaster and switches to the **CDD Batch** tab to monitor progress. Only users in the **Compliance** Sleek group can use the button (others see it disabled with a tooltip). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek workflow API** (`getBaseUrl()`): `GET /v2/sleek-workflow/customer-due-diligence/bulk-cdd-ongoing`, `POST /v2/sleek-workflow/customer-due-diligence/bulk-cdd-upload` (multipart `file`), `GET /v2/sleek-workflow/customer-due-diligence/bulk-upload/:batchId`; same page hosts **CDD Refresh List** (`GET .../list`) and **CDD Batch** listing (`GET .../bulk-batches`), batch detail, and **Retry** failed items (`POST .../bulk-batches/:batchId/retry`). |
| **Service / Repository** | sleek-website; customer-due-diligence / sleek-workflow backend (not in this repo) |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend persistence, queueing, and MongoDB collections for bulk batches are not visible in sleek-website; whether concurrent bulk uploads are blocked server-side as well as in the UI. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page shell**: Webpack entry `admin/cdd-workflows/index` → `src/views/admin/cdd-workflows/index.js` — `CddWorkflowsPage` with `AdminLayout` (`sidebarActiveMenuItemKey="cdd-workflows"`, `hideDrawer={true}`), header copy describing bulk CDD by CSV, tabs **CDD Refresh List** and **CDD Batch**.
- **Compliance gate**: `checkComplianceAccess()` — `api.isMember({ query: { group_name: SLEEK_GROUP_NAMES.COMPLIANCE } })`; `BulkTriggerCddModal` receives `disabled={!hasComplianceAccess}` and `disabledMessage="Only Compliance group members can bulk trigger CDD."`
- **Modal — CSV contract**: `BulkTriggerCddModal.js` — `COMPANY_ID_REGEX = /^[a-f0-9]{24}$/`; `parseCsvAndValidateCompanyIds` reads text, splits lines, takes first CSV column per row, rejects invalid rows with row numbers or empty file message.
- **Modal — upload flow**: `handleUploadCsv` — `api.uploadBulkCddCsv(selectedFile)` → `POST .../bulk-cdd-upload` with `FormData` field `file` (`src/utils/api.js`); reads `data.batch_id`, then `getBulkCddUploadByBatchId(batchId)` to hydrate `items` (maps `company_name`, `company_id`, `startedAt`, `triggeredBy`). On success calls `onUploadSuccess` (parent switches to batch tab + toaster) and `onClose` (parent `loadBatches()`).
- **Modal — concurrency UX**: When `getBulkCddOngoingUploads()` returns non-empty list while modal is open, body shows “Ongoing CDD refresh” table and blocks new upload until batch finishes (message in UI).
- **API client** (`src/utils/api.js`): `getBulkCddOngoingUploads`, `getBulkCddUploadByBatchId`, `uploadBulkCddCsv`, plus related page calls `getPendingCddWorkflows`, `getBulkCddBatches`, `retryBatchFailedItems` on `/v2/sleek-workflow/customer-due-diligence/...`.
- **Navigation**: `src/components/new-admin-side-menu.js` — **CDD Workflows** href `/admin/cdd-workflows/` under workflows; permission `manage_workflows` ties sidebar keys including `cdd-workflows` (`src/utils/constants.js`).

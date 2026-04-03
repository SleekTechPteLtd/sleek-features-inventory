# Oversee bulk CDD batches

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Oversee bulk CDD batches |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance User (Sleek Admin user in the **Compliance** group; `manage_workflows` grants sidebar access to **CDD Workflows**) |
| **Business Outcome** | Compliance staff can see how bulk CSV–triggered Customer Due Diligence runs progress over time, inspect per-company outcomes and errors, and retry failed line items within limits so bulk CDD work completes reliably. |
| **Entry Point / Surface** | **Sleek Admin** → **Workflows** collapsible section (when CMS **`workflow_tab_enabled`** and **`collapsible_menu_enabled`**) → **CDD Workflows** (shown when **`cdd_refresh`** and **`cdd_batch_upload`** are enabled) at **`/admin/cdd-workflows/`** → **CDD Batch** tab (second tab). Row click opens **CDD Batch Details** modal. Requires **`manage_workflows`** for sidebar key `cdd-workflows`. |
| **Short Description** | Lists paginated bulk CDD batches with date range filter, live progress for in-flight batches (5s auto-refresh when any batch is `in_progress`), and per-batch retry of failed items (up to **3** retries per batch, enforced in UI via `retry_count`). Opens a detail modal with company-level status, errors, batch summary, and retry history. Backend calls go to **sleek-workflow** customer-due-diligence bulk APIs. |
| **Variants / Markets** | Unknown — no market field in this UI; Sleek commonly **SG, HK, UK, AU**. |
| **Dependencies / Related Flows** | **Upstream**: **Bulk trigger CDD** (`BulkTriggerCddModal`, `uploadBulkCddCsv` → `POST …/bulk-cdd-upload`) creates batches; success toast steers users to **CDD Batch** tab. **Related tab**: **CDD Refresh List** (pending CDD workflows, `getPendingCddWorkflows`). **HTTP (sleek-website `api.js`)**: `GET /v2/sleek-workflow/customer-due-diligence/bulk-batches` (query `from`, `to`, `page`, `limit`); `GET /v2/sleek-workflow/customer-due-diligence/bulk-upload/{batchId}`; `POST /v2/sleek-workflow/customer-due-diligence/bulk-batches/{batchId}/retry`. **Auth**: `api.isMember({ group_name: COMPLIANCE })` for retry and bulk trigger affordances. |
| **Service / Repository** | **sleek-website**: `src/views/admin/cdd-workflows/index.js`, `cdd-batch-tab/CddBatchTab.js`, `cdd-batch-detail-modal/CddBatchDetailModal.js`, `src/utils/api.js`. **Backend** (not in repo): sleek-workflow service implementing bulk batch and upload endpoints. |
| **DB - Collections** | Unknown — batch and item persistence live in backend services (not evidenced in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | MongoDB or other store for bulk batch documents; server-side enforcement of retry cap vs UI `MAX_RETRIES`; whether `getBulkCddUploadByBatchId` returns full item sets for very large batches (modal paginates client-side only). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/cdd-workflows/index.js` (`CddWorkflowsPage`)

- **Compliance gate**: `checkComplianceAccess` → `api.isMember({ query: { group_name: SLEEK_GROUP_NAMES.COMPLIANCE } })` → `hasComplianceAccess` gates **BulkTriggerCddModal** and is passed for batch retry UI.
- **Batch list**: `loadBatches` → `api.getBulkCddBatches({ page, limit, from, to })` → `batches`, `batchTotal`; initial load sets `batchLoading`.
- **Polling**: `setInterval` every **5000** ms on **CDD Batch** tab (`activeTab === 1`) when not `batchLoading` and any batch has `status === "in_progress"` → `loadBatches()`.
- **Retry**: `handleRetryBatch` → `api.retryBatchFailedItems(batchId)` → `loadBatches()`; tracks `retryingBatchId`.
- **Detail modal**: `selectedBatchId` from `handleBatchRowClick`; `CddBatchDetailModal` `onClose` refreshes batches after close.

### `src/views/admin/cdd-workflows/cdd-batch-tab/CddBatchTab.js`

- **Filters**: **From / To** date inputs + **Apply filter** → parent `onApplyDateFilter`.
- **Table columns**: Uploaded at, Triggered by, Total, Status (progress bar for `in_progress` with `totalCount`/`pendingCount`; else `StatusChip`), File name, Retry.
- **Retry column**: For `partial` or `failed` only; `Button` calls `onRetry(batch._id)`; disabled when `!hasComplianceAccess`, `retriesRemaining === 0` (`MAX_RETRIES - retry_count`, `MAX_RETRIES = 3`), or while retrying; tooltip when not compliance.
- **Pagination**: `material-ui-flat-pagination` with rows-per-page **10 / 20 / 50**.

### `src/views/admin/cdd-workflows/cdd-batch-detail-modal/CddBatchDetailModal.js`

- **Load**: `api.getBulkCddUploadByBatchId(batchId)` → `data.triggeredBy`, `data.batch.status`, `data.items` (mapped company name, UEN/id, `startedAt`, `errorMessage`), `data.retry_history` (`retriedBy`, `retriedAt`).
- **Item statuses** (tags): `pending`, `in_progress`, `completed`, `failed`, `skipped`.
- **Footer**: Batch status tag, triggered by, processed count / progress bar, **Retry history** list when present.
- **Pagination**: Client-side slice of `items` (page size **10 / 25 / 50**) — no server paging for items in this component.

### `src/utils/api.js`

- `getBulkCddBatches` → `GET ${base}/v2/sleek-workflow/customer-due-diligence/bulk-batches?…`
- `getBulkCddUploadByBatchId` → `GET ${base}/v2/sleek-workflow/customer-due-diligence/bulk-upload/{batchId}`
- `retryBatchFailedItems` → `POST ${base}/v2/sleek-workflow/customer-due-diligence/bulk-batches/{batchId}/retry`

### `src/components/new-admin-side-menu.js`

- **Navigation**: **CDD Workflows** → `href="/admin/cdd-workflows/"`, `key="cdd-workflows"`, nested under **Workflows** collapsible when `workflow_tab_enabled` and `collapsible_menu_enabled`; link rendered only if **`cdd_refresh.enabled && cdd_batch_upload.enabled`**.

### `src/utils/constants.js`

- **Permission**: `manage_workflows` → `sidebarMenuItemKeys` includes `"cdd-workflows"`.

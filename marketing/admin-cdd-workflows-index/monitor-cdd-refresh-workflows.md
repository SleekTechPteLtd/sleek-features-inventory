# Monitor CDD refresh workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Monitor CDD refresh workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance User (Sleek Admin — Compliance group); Operations User |
| **Business Outcome** | Compliance staff can see which companies are in active Customer Due Diligence refresh, how far reminders and workflows have progressed, and how admin KYC lines up—so outreach, validation, and Zendesk follow-up stay coordinated. |
| **Entry Point / Surface** | **Sleek Admin** → **CDD Workflows** (`sidebarActiveMenuItemKey="cdd-workflows"`, page title **CDD Workflows**). First tab **CDD Refresh List** (second tab is **CDD Batch** for bulk CSV uploads). |
| **Short Description** | Paginated table of pending CDD workflows with filters (company name, CDD workflow status, trigger source batch vs manual). Columns cover company, risk rating, CDD workflow status, trigger source (with batch detail when applicable), **Admin KYC Status** (derived per company owner via `getCompanyUsers`), **CDD Refresh State** and email-sent date from backend reminder/chaser history, and row actions: open Camunda **CDD workflow** task, **Resend Reminder**, **Open Zendesk** (CDD Refresh vs KYC Refresh) with ticket search, manual ticket selection, retry on failed automation, and **View KYC** deep link to company People & Entities. |
| **Variants / Markets** | Unknown (no market gate in these views; Sleek typically operates **SG, HK, UK, AU**). |
| **Dependencies / Related Flows** | **HTTP (`api.js`)**: `GET /v2/sleek-workflow/customer-due-diligence/list` — `getPendingCddWorkflows` (pagination, `company_name`, `cdd_form_status`, `is_from_bulk_upload`). `POST /v2/sleek-workflow/customer-due-diligence/:companyId/resend-cdd-refresh-email` — `resendCddRefreshReminder`. **Company users**: `GET /companies/:companyId/company-users` — `getCompanyUsers(companyId, { query: { lean: "true" } })` for owner KYC invitation/KYC status mapping. **Zendesk**: `GET /v2/zendesk/tickets/company/:companyId?subject=…`, `GET /v2/zendesk/ticket/:ticketId`, `POST /v2/zendesk/cdd/form-submitted/create-zendesk-ticket/:companyId`, `POST /v2/zendesk/kyc-refresh/submitted/create-zendesk-ticket/:companyUserId`, `POST /v2/zendesk/cdd/workflow/:workflowId/ticket/:ticketId/set-manual`, `POST /v2/zendesk/kyc-refresh/company-user/:companyUserId/ticket/:ticketId/set-manual`, `GET /v2/zendesk/logs/company-user/:companyUserId`, `GET /v2/zendesk/logs/reference/:workflowId`. **Navigation**: company overview `/admin/company-overview/?cid=…`; Camunda task `/admin/sleek-workflow/workflow-task/?processId=…&processInstanceId=…`. **Related**: CDD Batch tab + bulk upload (`index.js`), `marketing/admin-sleek-workflow-workflow-task/work-client-camunda-workflows-from-admin.md` for workflow task surface. |
| **Service / Repository** | **sleek-website**: `src/views/admin/cdd-workflows/index.js`, `src/views/admin/cdd-workflows/cdd-refresh-list-tab/CddRefreshListTab.js`, `src/views/admin/cdd-workflows/cdd-refresh-list-tab/ZendeskTicketDialog.js`, `src/utils/api.js`. **Backend** (sleek-workflow, Zendesk integration services): REST handlers behind the above paths—not defined in this repo. |
| **DB - Collections** | Unknown (workflow, Zendesk log, and company user data persisted on backend; not visible from sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC beyond Compliance group check for bulk trigger vs read-only list; whether all `cdd_refresh_state` values from backend are covered by `CDD_REFRESH_STATE_LABELS` in parent page. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/cdd-workflows/index.js` (`CddWorkflowsPage`)

- **Mount**: `getUser`, `checkComplianceAccess` — **`api.isMember({ group_name: SLEEK_GROUP_NAMES.COMPLIANCE })`** sets `hasComplianceAccess` (bulk trigger modal uses it).
- **CDD Refresh List data**: **`api.getPendingCddWorkflows`** with `page`, `limit`, optional `company_name`, `cdd_form_status`, `is_from_bulk_upload` — populates `workflows`, `total`.
- **Helpers passed to tab**: `getCddRefreshStateDisplay` / `getCddRefreshStateLabel` map backend states (`triggered`, `reminder-one-sent`, … `done`, `sla-breach`, etc.) and latest `sent_at` for display.
- **Tab 0**: renders **`CddRefreshListTab`** with filters, pagination handlers, `onOpenBatchDetail` for batch info icon from list rows.

### `src/views/admin/cdd-workflows/cdd-refresh-list-tab/CddRefreshListTab.js`

- **Table headers**: company name, risk rating, CDD workflow status, trigger source, Admin KYC Status, CDD Refresh State, Email Sent At, Actions.
- **Admin KYC**: `useEffect` loads **`api.getCompanyUsers`** per distinct `company_id`; **`getCompanyAdminKycStatusData`** maps owner `kyc_status` / `invitation_status` to `KYC_STATUS_KEYS` / `KYC_STATUSES_V2` chips.
- **KYC refresh result tooltip**: uses `row.kyc_refresh_result` (`triggered`, `reason`, risk, days since last KYC, etc.).
- **Actions menu**: **View CDD Workflow** → `workflowTaskUrl` from `business_key` + `processInstanceId`; **Resend Reminder** → **`api.resendCddRefreshReminder(companyId)`** (disabled when workflow completed/submitted/cancelled, or `enable_cdd_reminder_emails === false`); **Open Zendesk** submenu **CDD Refresh** / **KYC Refresh** → **`handleZendeskOptionClick`**: loads stored ticket via **`getZendeskLogByReferenceId(workflowId)`** or **`getZendeskLogByCompanyUserId`**, **`getCompanyZendeskTickets`**, **`getZendeskTicketById`**, create via **`createCDDFormSubmittedZendeskTicket`** / **`createKYCRefreshSubmittedZendeskTicket`**, manual set via **`setCDDWorkflowZendeskTicketManually`** / **`setKYCRefreshZendeskTicketManually`**; **`handleRetryCreateZendeskTicket`** for failed creation path.
- **View KYC**: opens `/admin/company-overview/?cid=…&currentPage=People & Entities`.

### `src/views/admin/cdd-workflows/cdd-refresh-list-tab/ZendeskTicketDialog.js`

- Presents Zendesk ticket table (ID, status, date, Open link); **Set Correct** for manual linkage when not read-only; **Retry Generate Zendesk** when `storedErrorMessage` is set; info banner when selecting from search results (`subject`).

### `src/utils/api.js`

- **`getPendingCddWorkflows`**: `GET ${base}/v2/sleek-workflow/customer-due-diligence/list?…`
- **`resendCddRefreshReminder`**: `POST …/customer-due-diligence/:companyId/resend-cdd-refresh-email`
- Zendesk and manual-ticket endpoints as listed in **Dependencies / Related Flows**.

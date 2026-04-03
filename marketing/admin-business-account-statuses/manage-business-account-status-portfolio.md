# Manage business account status portfolio

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage business account status portfolio |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal operations / admin users with `permissions.business_account` of `read`, `edit`, or `full` |
| **Business Outcome** | Staff can review the business-account portfolio, export it for reporting, change lifecycle status with a mandatory reason and audit history, and optionally notify customers after certain transitions. |
| **Entry Point / Surface** | **sleek-website** admin: **Business Accounts Status** — `/admin/business-account-statuses/` — `AdminLayout` with `sidebarActiveMenuItemKey="business-account-statuses"` (see `new-admin-side-menu`). |
| **Short Description** | Loads paginated business accounts via the bank admin API with filters (company, status, sort by days since last activity). The table shows company (link to company overview), status, available balance, latest activity (tooltip with lifecycle dates), days since last activity, restriction/closure date, status history, and a row action to change status. Status changes open a dialog requiring a free-text reason; closing is warned as irreversible. After a successful update, operators may **Inform User** for transitions to `active`, `restricted`, or `suspended` (mapped notification templates). Client-side TSV export of the current result set. Unverified users go to `/verify/`; users without business account permission go to `/admin`. |
| **Variants / Markets** | **Unknown** — no market dimension in this view; Sleek typically operates **SG, HK, UK, AU**; confirm with bank/SBA service if behaviour differs by tenant. |
| **Dependencies / Related Flows** | **`bankApi.getBusinessAccountStatuses`** → **`GET ${base}/sba/v2/admin/business-accounts/statuses`** (query: `fields`, `status`, `company_id`, `page`, `limit`, `order_by`, `order`). **`bankApi.updateBusinessAccount`** → **`PUT .../sba/v2/admin/business-accounts/:id`** with `status`, `reason_for_status_change`. **`bankApi.informBusinessAccountStatusChange`** → **`sendNotification`** → **`POST ${base}/notifications`** with `businessAccountId`, `templateId` (`business_account_being_restricted` \| `business_account_being_suspended` \| `business_account_being_reactivated`). **`api.getUser`** (session + permission gate). Deep link to **Company overview** business account tab: `/admin/company-overview/?cid={company_id}&currentPage=Business+Account#/`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/business-account-statuses/index.js`, `src/views/admin/business-account-statuses/components/BusinessAccountTable.js`, `src/views/admin/business-account-statuses/components/StatusChangeDialog.js`, `src/views/admin/business-account-statuses/components/StatusHistoryModal.js`, `src/utils/business-account-utils.js`, `src/utils/api-bank.js`. **Bank / SBA backend** (not in this repo): implements business account statuses list, updates, and persisted `status_history`. **Notifications service** (not in this repo): `POST /notifications`. |
| **DB - Collections** | **Unknown** — MongoDB or other stores for business accounts and status history live in the bank/SBA (and related) services; **sleek-website** is a client only. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `edit` vs `full` is required server-side for status changes (UI allows read, edit, full for the page); exact persistence of `status_history` fields (`admin_name`, `admin_email`, `reason`); whether notification delivery is synchronous with `POST /notifications`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/business-account-statuses/index.js` (`BusinessAccountsStatus`)

- **Mount**: `domready` → `#root`; page title area “Business Accounts Status”; **Export to TSV** builds `business_accounts_status.tsv` from the **current** `accounts` array (not necessarily full dataset beyond pagination).
- **Permission**: `api.getUser()` → `registered_at` or redirect `/verify/`; `permissions.business_account` ∈ `{ read, edit, full }` else `/admin`.
- **Data**: `bankApi.getBusinessAccountStatuses(filters)` on load and filter/pagination changes; default filters `order_by: "daysSinceLastActivity"`, `order: "desc"`.
- **Status update**: `updateBusinessAccount(accountId, { status, reason_for_status_change })`; optimistic row update on success; dialog states `confirm` → `success` \| `error`; optional `handleInform` → `informBusinessAccountStatusChange(accountId, newStatus)`.
- **History**: `StatusHistoryModal` receives `account.status_history` reversed for display.

### `src/views/admin/business-account-statuses/components/BusinessAccountTable.js`

- **Filters**: `CompanyFilter` → `company_id`; status filter `active` \| `suspended` \| `restricted` \| `closed`; sort control for `daysSinceLastActivity` only (client-side sort on `accounts` for that column; other `order_by` values pass through but table sort is only implemented for days-since-last-activity in the comparator).
- **Row status transitions**: `availableStatuses` enforces allowed targets; **`closed`** can only transition to `closed` (terminal in UI).
- **Links**: Company name → company overview with `currentPage=Business+Account`.

### `src/views/admin/business-account-statuses/components/StatusChangeDialog.js`

- **Confirm**: `reason` required (non-empty trim) before **Confirm**; warning copy when `newStatus === "closed"` (cannot revert).
- **Inform User**: Shown in `success` state when `newStatus` ∈ `active`, `restricted`, `suspended` (not for `closed` in this dialog).

### `src/views/admin/business-account-statuses/components/StatusHistoryModal.js`

- Columns: `updatedAt`, `status`, `reason`, `admin_name` / `admin_email` (timezone `Asia/Singapore`).

### `src/utils/business-account-utils.js`

- **`getBusinessAccountStatuses`**: wraps `apiBank.getBusinessAccountStatuses`.
- **`updateBusinessAccount`**: wraps `apiBank.updateBusinessAccount` (errors surfaced as `errorMessage` object).
- **`informBusinessAccountStatusChange`**: maps status to template id, then `apiBank.sendNotification`.

### `src/utils/api-bank.js`

- **`getBusinessAccountStatuses`**: `GET` `` `${getBaseUrl()}/sba/v2/admin/business-accounts/statuses` `` with query `fields: "company_name"` plus optional filter keys.
- **`updateBusinessAccount`**: `PUT` `` `${getBaseUrl()}/sba/v2/admin/business-accounts/${business_account_id}` ``.
- **`sendNotification`**: `POST` `` `${getBaseUrl()}/notifications` `` with `{ businessAccountId, templateId }`.

### `src/utils/constants.js`

- **`BUSINESS_ACCOUNT_PERMISSION`**: `FULL`, `EDIT`, `READ`.

### `src/components/new-admin-side-menu.js`

- Menu item **Business Accounts Status** → `/admin/business-account-statuses/`, key `business-account-statuses`.

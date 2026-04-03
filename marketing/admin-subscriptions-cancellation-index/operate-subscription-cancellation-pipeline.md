# Operate subscription cancellation pipeline

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Operate subscription cancellation pipeline |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Admin staff can work through subscriptions that are cancelling, narrow the queue by company and pipeline stage, and update cancellation status so offboarding is visible through completion. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > **Cancellation** (sidebar `sidebarActiveMenuSubItemKey="cancellation"`), built page `admin/subscriptions/cancellation/index` |
| **Short Description** | Loads company subscriptions that are in cancellation (`is_cancelling=true`), sorted by `overdue_at`, with optional filters for `cancellation_status` (`new` / `pending` / `done`) and company. Toolbar paginates via `skip` and fixed `perPage` (20). Each row shows company (link to customer dashboard), service, renewal duration, completion date when status is `done`, owner contact fields, and a status dropdown to move the subscription through New → In progress → Complete, with confirmation dialog and `PUT` to persist `cancellation_status`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **APIs:** `GET /admin/company-subscriptions` (query: `is_cancelling`, `sortBy`, `sortOrder`, `skip`, optional `cancellation_status`, optional `company`); `PUT /admin/company-subscriptions/:companySubscriptionId` with JSON body `{ cancellation_status }`. **Shared UI:** company search and pagination handlers from `views/admin/subscriptions/common.js` (`getCompanies` with `admin: true` for filter). **Upstream:** customer-side cancellation request flow (`cancelCompanySubscription` → `PUT …/company-subscriptions/:id/cancellation-request` in `api.js`) is related but not used on this screen. |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `maxPage` is passed to the toolbar but never set in `index.js` state, so “next page” may not disable when results end—confirm intended pagination contract with API (total count / hasMore). Backend validation and side effects of `cancellation_status` updates are not visible in this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Page shell / load**: `src/views/admin/subscriptions/cancellation/index.js` — `AdminCancelledSubscriptionsView` uses `AdminLayout` with `sidebarActiveMenuItemKey="subscriptions"`, `sidebarActiveMenuSubItemKey="cancellation"`, `hideDrawer={true}`. `componentDidMount` calls `getUser` (from `../../subscriptions/common`), `getCompanySubscriptions`, and reads CMS error copy for `GENERAL` alerts (`customer_support`).
- **List query**: `getCompanySubscriptions` sets `options.query` to `is_cancelling: "true"`, `sortBy: "overdue_at"`, `sortOrder: 1`, `skip: (page - 1) * perPage` (default `perPage` 20). Optional `cancellation_status` and `company` (selected company id) when set. Calls `api.getAdminCompanySubscriptions(options)` → `GET ${getBaseUrl()}/admin/company-subscriptions` (`src/utils/api.js`). Reads `response.data.companySubscriptions`. On HTTP 422, `renderAlert` shows CMS general error.
- **Status filter**: `selectStatusHandleChange` maps empty string to `null`, then refetches. Toolbar labels: Any; New Cancellation (`new`); Requests Created (`pending`); Cancelled (`done`) — `primary-toolbar-content.js`.
- **Update workflow**: `handleUpdateCancellationStatus` → `api.updateSubscriptionCancellationStatus(subscriptionId, { body: JSON.stringify({ cancellation_status }) })` → `PUT ${getBaseUrl()}/admin/company-subscriptions/${companySubscriptionId}` (`api.js`). Confirmed via `toggleDialog` + `dialogOnClickPrimaryButton`.
- **Status display mapping**: `showCancellationStatus` — `new` → “New Cancellation”, `pending` → “Cancellation in Process”, `done` → “Cancellation Complete”.
- **Table**: `table-content.js` — columns: index, Company, Subscription, Renewal, Cancellation Completed, Owner, Phone, Email, Status. `table-row.js` — company name links to `/dashboard/?cid={company._id}`; renewal shows `duration` months; “Cancellation Completed” shows `updatedAt` formatted when `cancellation_status === "done"`, else “-”.
- **Row actions**: `cancellation-dropdown.js` — Blueprint `Popover` + `Menu`; only offers transitions to statuses the subscription is not already in; each calls `toggleDialog` before update.
- **Shared handlers**: `src/views/admin/subscriptions/common.js` — `handleSelectCompany` / `handleSelectNoCompany`, `handleSearchCompany` + `fetchCompaniesList` (`api.getCompanies` with `query: { name }`, `admin: true`), pagination `handleChangePage` / `handleClickPrevPage` / `handleClickNextPage`, `getUser` with redirect to `/verify/` if email not verified.
- **Build**: `webpack/paths.js` entry `admin/subscriptions/cancellation/index`; `webpack.common.js` emits `admin/subscriptions/cancellation/index.html`.

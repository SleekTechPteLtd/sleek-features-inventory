# Manage Paid Company Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Paid Company Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Gives admins a single place to review, filter, correct, and remove paid subscription records across all companies, keeping the billing ledger accurate and traceable to invoices. |
| **Entry Point / Surface** | Sleek Admin > Subscriptions > Paid (`/admin/subscriptions/paid/`) |
| **Short Description** | Paginated list of paid company service records. Admins can filter by company (live search) and by subscription status (active / past), view linked invoices inline, navigate to the edit form for any record, or permanently delete a record via a confirmation dialog. Edit and remove actions are gated behind `permissions.company_services === "full"`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Edit Paid Company Subscription (`/admin/subscriptions/paid/edit/`); `GET /company-services` (list); `DELETE /company-services/:id` (remove); `GET /companies` (company search); invoice URLs linked from the list; shared pagination/company-select helpers in `views/admin/subscriptions/common.js` |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend repo serves `GET /DELETE /company-services`? What DB collections are touched server-side (likely `company_services`, `invoices`)? Are market variants (SG/HK/UK/AU) differentiated at the service-type or subscription level? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `views/admin/subscriptions/paid/index.js` — `AdminPaidSubscriptionsView` React component
- Admin layout sidebar key: `subscriptions` / `paid-subscriptions`
- Accessible at `/admin/subscriptions/paid/`

### API calls (via `src/utils/api.js`)
| Call | Endpoint | Purpose |
|---|---|---|
| `getCompanyServices({ admin: true, query: { skip, company, selected_only, is_active } })` | `GET /company-services` | Paginated list with active/past and company filters |
| `deleteCompanyServices(id, { admin: true })` | `DELETE /company-services/:id` | Permanently remove a subscription record |
| `getCompanies({ query: { name }, admin: true })` | `GET /companies` | Live-search company dropdown for filtering |

### List columns rendered
Company (link to dashboard), Subscription (service name), Duration (months), Start At, End At, Invoices (clickable invoice number links), Edit / Remove actions.

### Filters available
- **Status**: Any / Currently Active (`is_active=true`) / Past (`is_active=false`)
- **Company**: type-ahead select; "No Selection" clears the filter

### Pagination
20 records per page; prev/next buttons plus direct page-number input. Shared helpers from `views/admin/subscriptions/common.js` (`handleChangePage`, `handleClickPrevPage`, `handleClickNextPage`).

### Permission gate
Edit and Remove buttons are `disabled` unless `user.permissions.company_services === "full"`.

### Delete flow
Confirmation dialog: "Are you sure you want to remove this service? This action is not reversible." → calls `DELETE /company-services/:id` → refreshes list.

### Related module
`clm/admin-subscriptions-paid-edit/edit-paid-company-subscription.md` — covers the edit form reached via the Edit button on this screen.

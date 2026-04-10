# Monitor Company Subscription Renewals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Company Subscription Renewals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin, Customer Success (CSS) team members |
| **Business Outcome** | Gives the CSS and Admin teams a unified view of the subscription renewal pipeline so they can proactively action renewals before they lapse. |
| **Entry Point / Surface** | Sleek Admin App > Subscriptions (sidebar: paid-subscriptions) |
| **Short Description** | Displays a paginated, sortable list of all company subscriptions with renewal dates, payment status, subscription type, and assigned team members. Admins can filter by renewal date range, payment status, company status, subscription type/status, CSS in charge, and account manager to prioritise renewal outreach. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Company profile (`/admin/companies/edit`); subscription detail view (`/admin/subscriptions/new/details`); CSS and Accounting team member lookup (`/admin/company-subscriptions` + `getAdminsByGroup`); company comments/audit log (sleek-auditor service); Xero invoice link (displayed per row) |
| **Service / Repository** | sleek-website |
| **DB - Collections** | Unknown (data fetched via API — collection names not visible from frontend code) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service/repo owns `GET /admin/company-subscriptions`? What collections back company-subscriptions data? Are markets (SG/HK/UK/AU) filtered at API level or all shown together? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/views/admin/subscriptions/new/index.js` — `AdminSubscriptionsView` root component; orchestrates filter + table, calls `api.getAdminAllCompanySubscriptions()`, manages pagination and sort state. Default renewal window: now → +6 months (`overdue_at_to`).
- `src/views/admin/subscriptions/new/components/filter.js` — `Filter` component; advanced filter panel with: company name search, company status, payment status (PAID/UNPAID), CSS in charge (Customer Success group), account manager (Accounting group), subscription type, subscription status, renewal from/to date range. Filter state persisted to `localStorage` under key `subscriptions-advance-search-filter`.
- `src/views/admin/subscriptions/new/components/table.js` — `SubscriptionsTable` component; columns: Name, (comment icon), Subscription, Duration, Renewal date, Service Activated Date, Payment info, Owner, Invoice (Xero link), Subscription status. Supports column sorting. Payment info resolved as Manual Payment (popover with invoice details) or Credit Card. Inline company comments popover via sleek-auditor.

### API calls
- `GET /admin/company-subscriptions` — main data fetch (`api.getAdminAllCompanySubscriptions`); query params: `sortBy`, `sortOrder`, `skip`, `limit`, `company`, `company_status`, `payment_status`, `css_in_charge`, `accounting_in_charge`, `overdue_at_from`, `overdue_at_to`, `subscription_by`, `subscription_status`, `payment_info_by`.
- `GET /admin/admins?group_name=Customer+Success` — fetches CSS team members for filter dropdown (`api.getAdminsByGroup`).
- `GET /admin/admins?group_name=Accounting` — fetches Accounting team members for filter dropdown.
- `GET /v2/sleek-auditor/api/log/company/:companyId/comment/` — fetch company comments (`api-sleek-auditor.getCompanyComments`).
- `PUT /v2/sleek-auditor/api/log/company/:companyId/comment/` — post company comment (`api-sleek-auditor.postCompanyComment`).

### Config-driven data
- `COMPANY_STATUSES`, `SUBSCRIPTION_NAMES`, `SUBSCRIPTION_STATUSES` — loaded from platform CMS feature flags (`getPlatformConfig` + `getAppFeatureProp`).

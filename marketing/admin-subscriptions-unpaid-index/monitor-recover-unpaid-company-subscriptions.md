# Monitor and recover unpaid company subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Monitor and recover unpaid company subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Sleek internal staff with access to **Subscriptions** admin; unpaid nav item gated by CMS **`subscriptions.unpaid`** feature flag) |
| **Business Outcome** | Operations can see which company subscriptions are unpaid or approaching renewal without payment, prioritize by urgency and automatic renewal, use invoice and bank-transfer context, and drive collection or closure (remind, cancel auto-renewal, or mark paid). |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/subscriptions/unpaid/`** (webpack entry `admin/subscriptions/unpaid/index`). **`AdminLayout`** with `sidebarActiveMenuItemKey="subscriptions"`, `sidebarActiveMenuSubItemKey="unpaid-subscriptions"`. Sub-menu link shown when CMS **`subscriptions.unpaid`** is enabled (`admin-side-sub-menu.js`, `mobile-admin-user-menu.js`). |
| **Short Description** | Paginated table of active, non-cancelling company subscriptions sorted by renewal date (`overdue_at`). Filters: renewal urgency windows for **non-auto** (before 1 week / 2 weeks / 1 month), **automatic renewals only**, and optional company search. Rows show company (link to customer dashboard), service, duration, renewal with visual urgency icons, manual payment hint popover, owner, Xero invoice link when present, and **Actions**: resend reminder (non-auto), request cancellation (auto), move to paid. |
| **Variants / Markets** | **Unknown** (no market encoding in this view; Sleek tenants often SG/HK/UK/AU elsewhere). |
| **Dependencies / Related Flows** | Main API **company-subscriptions** admin routes; **`getCompanies`** (admin) for company picker. Related: **new subscriptions** admin (`admin/subscriptions/new`) reuses **`ManualPaymentInfo`** with **`getInvoiceInfo`**; **paid subscriptions** edit flows. Backend persists subscription/billing state — not in sleek-website. |
| **Service / Repository** | **sleek-website**: `src/views/admin/subscriptions/unpaid/index.js`, `src/views/admin/subscriptions/unpaid/manual-payment-info.js`, `src/views/admin/subscriptions/common.js`, `src/utils/api.js`. **Main API** (configured via **`API_BASE_URL`**, prod `https://api.sleek.sg`): subscription and billing handlers. |
| **DB - Collections** | **Unknown** (subscription and invoice data loaded via HTTP; persistence not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | **`ManualPaymentInfo`** in **`unpaid/index.js`** is rendered with only **`subscription`**; the component calls **`props.getInvoiceInfo(subscription, props.service)`** and is wired correctly in **`new/components/table.js`** and **`new/details/components/history.js`**. Confirm whether the unpaid page popover is broken at runtime or if an uncommitted fix passes **`getInvoiceInfo`** (e.g. deriving invoice from **`expected_external_payment_info.invoices`** like the table columns). Whether **`is_auto`** default **`"false"`** in **`selectStatusHandleChange`** is intended when clearing filters (vs omitting the param). Exact backend rules for **`GET /admin/company-subscriptions`** filter semantics. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/subscriptions/unpaid/index.js` (`AdminUnpaidSubscriptionsView`)

- **`componentDidMount`**: **`getCompanySubscriptions`**, **`getUser`** (from common).
- **List load**: **`api.getAdminCompanySubscriptions`** with query: **`is_subscribed: "true"`**, **`is_cancelling: "false"`**, **`sortBy: "overdue_at"`**, **`sortOrder: 1`**, **`skip`** for pagination; optional **`overdue_at`**, **`company`** (`selectedCompanyId`), **`is_auto`** when filtering automatic renewals.
- **Filters**: Dropdown maps to **`overdue_at`** as a formatted future date string (1 week / 2 weeks / 1 month for non-auto) or **`is_auto: "true"`** for automatic renewals; **`selectStatusHandleChange`**.
- **Company select**: Blueprint **`Select`** + **`fetchCompaniesList`** / **`handleSelectCompany`** / **`handleSearchCompany`** from **`common.js`** (same pattern as other subscription admin views).
- **Row data**: Company name + link to **`/dashboard/?cid=`**; **`text.titlelize(service)`**; duration; renewal **`moment(overdue_at)`** with emoji icons (**`renderEmojiForRenewalDate`**) for auto vs non-auto urgency bands and overdue; **`expected_external_payment_info.invoices.0`** for invoice number and Xero **`url`**; **`ManualPaymentInfo`** popover when **`expected_external_payment_info`** is present.
- **Actions menu**: **`api.sendSubscriptionReminderEmail(subscription._id)`** → **`POST`** **`/admin/company-subscriptions/:id/send-reminder`** (non-auto only); confirmation dialog then **`api.cancelCompanySubscription(subscription._id)`** → **`PUT`** **`/company-subscriptions/:id/cancellation-request`** (auto); **`api.moveSubscriptionToPaid(subscription._id)`** → **`/admin/company-subscriptions/:id/move-to-paid`**; 422 shows toast from response message.
- **Help popover**: Documents colour codes for automatic renewal vs non-auto urgency and overdue.

### `src/views/admin/subscriptions/unpaid/manual-payment-info.js` (`ManualPaymentInfo`)

- Renders **Manual Payment Info**: invoice number (link), tentative payment date from **`expected_pay_at`**, cheque number, using **`getInvoiceInfo(subscription, service)`** when provided by parent.

### `src/views/admin/subscriptions/common.js`

- **`fetchCompaniesList`**: **`api.getCompanies({ query: { name: selectCompanySearch }, admin: true })`** → **`data.companies`** for searchable company dropdown.
- **`getUser`**: **`api.getUser`**; unverified email redirects to **`/verify/`**; **`checkResponseIfAuthorized`** on error.
- Pagination helpers: **`handleChangePage`**, **`handleClickPrevPage`**, **`handleClickNextPage`**.

### `src/utils/api.js`

- **`getAdminCompanySubscriptions`**: **`GET ${getBaseUrl()}/admin/company-subscriptions`** with optional query via **`getResource`**.
- **`moveSubscriptionToPaid`**: **`/admin/company-subscriptions/:id/move-to-paid`**.
- **`sendSubscriptionReminderEmail`**: **`/admin/company-subscriptions/:id/send-reminder`**.
- **`cancelCompanySubscription`**: **`PUT`** **`/company-subscriptions/:id/cancellation-request`**.
- **`getCompanies`**: admin mode prefixes **`/admin`** on the main API base URL.

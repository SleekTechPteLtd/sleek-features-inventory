# Manage company subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff and billing admins (subscription list and read for broader admin users; destructive edits and subscription field patches gated on **Billing Super Admin** group membership) |
| **Business Outcome** | Staff can see a company’s Sleek Billings subscriptions in one place, assess renewal and delivery health, confirm payment readiness, and apply controlled changes so renewals and service delivery stay aligned with operations. |
| **Entry Point / Surface** | **sleek-website** admin: **Company Billing** standalone page `/admin/company-billing/?cid=<companyId>` (Subscriptions tab default), and the same **Company Billing** experience embedded under **Admin → Company overview** (`BillingBeta` / `PAGES.BILLING_BETA`). Optional deep link `?subscriptionId=<id>` opens subscription detail. |
| **Short Description** | Lists customer subscriptions from Sleek Billings with search, grouping (by service code / FY), filters for deactivated rows, and sortable columns for service FY, delivery status, dates, renewal status, and renewal due date. Row opens a detail view showing pricing, renewal controls (auto-renewal, amounts, dates, cancel), delivery lifecycle (offboard, reactivate, discontinue), editable subscription metadata where permitted, deliverables, audit log and renewal history — all backed by the Sleek Billings HTTP API. Payment method validity is checked for renewal readiness messaging. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Billings** service (`SLEEK_BILLINGS_API`): `customer-subscriptions`, `payment-methods`, `audit-logs`, renewal history. **sleek-website** `api.getCompany`, `api.getUser`, `api.isMember` (JumpCloud group `BILLING_SUPER_ADMIN` for edit permission). Same page bundle includes **Invoices & Credit Note** and **Credit Balance** tabs; **Payment Request** flows to invoice creation. Related: admin company overview, workflow tasks linking to Company Billing. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-billing/index.js`, `src/views/admin/company-billing/subscriptions-list.js`, `src/views/admin/company-billing/subscription-detail.js`, `src/utils/sleek-billings-api.js` (plus `constants.js`, `AuditLogDrawer.js`, `RenewalHistory.js`, `components/deliverables.sds.component.js` for detail behaviour). **Backend**: Sleek Billings service (not in this repo). |
| **DB - Collections** | Unknown — persistence is in the Sleek Billings backend; this app only calls REST endpoints. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non–billing-super-admin users rely on this view read-only in production for all markets; exact mapping of `SLEEK_BILLINGS_API` environments to regions. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-billing/index.js` (`AdminBillingConfigurationView`)

- **Mount**: Loads user (`api.getUser`), company (`api.getCompany` + `api.getCompanyProfile` from `cid` query), company users, services/tax rates for payment request, `sleekBillingsAPI.getCustomerSubscriptions(company._id)` into `companySubscriptions`, platform config, accounting service tags.
- **Tabs**: Subscriptions (0), Invoices & Credit Note (1), Credit Balance (2); `?tab=` can set active tab. Renders `SubscriptionsList` with `selectedSubscription` / `setSelectedSubscription`.
- **Routing context**: Webpack entry `admin/company-billing` → `src/views/admin/company-billing/index.js`.

### `src/views/admin/company-billing/subscriptions-list.js`

- **Load**: `getCustomerSubscriptions(company._id)`; `getCustomerPaymentMethods(company._id)` to set `hasValidPaymentMethod` (non-expired card or non-card method).
- **UX**: Search (name, FY, delivery/renewal labels), toggles for grouped expansion and deactivated/discontinued rows, column sort, `groupSubscriptions` using `service.subscriptionGroupingCriteria` (`same_item_code`, `same_fye`).
- **Detail navigation**: `?subscriptionId=` selects a subscription on load; back clears param and refetches.

### `src/views/admin/company-billing/subscription-detail.js`

- **Sleek Billings API usage**: `toggleAutoRenewal`, `cancelRenewal`, `updateCustomRenewalAmount`, `updateNextRenewalDate`, `updateFinancialYearEnd`, `offboardSubscription`, `reactivateSubscription`, `discontinueSubscription`, `updateCustomerSubscription` (`/patch-data` with `reasonForPatching` and linked-subscription resolution), `getAuditLogsByCompanyIdAndTags`.
- **Permission**: `checkEditPermission` → `isMember({ group_name: SLEEK_GROUP_NAMES.BILLING_SUPER_ADMIN })`.
- **Payment readiness**: Auto-renewal UI uses `hasValidPaymentMethod` prop (tooltip when missing).
- **Deliverables / audit**: `AuditLogDrawer` (see `AuditLogDrawer.js` + `getRenewalHistory` in `sleek-billings-api.js`).

### `src/utils/sleek-billings-api.js`

- **Base URL**: `getAppCustomEnv()` → `SLEEK_BILLINGS_API`.
- **Subscriptions**: `GET /customer-subscriptions?companyId=`, `PUT` routes for renewal, FY, custom amount, cancel, toggle renewal, offboard, reactivate, discontinue, `patch-data`; `GET /customer-subscriptions/:id/renewal-history`.
- **Payment methods**: `GET /payment-methods?companyId=`.
- **Helpers**: `mapSubscriptionFromSleekBillings` for cross-cutting subscription shape (used in `index.js` for accounting/tax checks).

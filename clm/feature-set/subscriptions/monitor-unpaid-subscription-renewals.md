# Monitor Unpaid Subscription Renewals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Monitor Unpaid Subscription Renewals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal billing operator) |
| **Business Outcome** | Gives operators a searchable, paginated view of all customer subscriptions with failed or pending auto-renewal charges so they can identify billing failures, inspect attempt history, and manually re-trigger payment — reducing revenue leakage from unresolved renewals. |
| **Entry Point / Surface** | Sleek Billings App > Subscriptions (page title: "Unpaid Subscriptions") |
| **Short Description** | Operators search across all customer subscriptions by name, service type, code, renewal status, or delivery status, then review up to two auto-renewal attempt timestamps and per-attempt failure reasons. A per-row action menu lets operators open the company's billing overview in Admin App or manually trigger an auto-charge re-attempt. |
| **Variants / Markets** | SG (currency formatted as SGD; other markets unconfirmed) |
| **Dependencies / Related Flows** | Subscription auto-renewal service (`/subscription-auto-renewal/trigger-manual-auto-renewal-charge`); Admin App company billing overview (`/admin/company-overview/?cid=…&currentPage=Billing+Beta`); `searchCustomerSubscriptions` and `triggerManualAutoCharge` API endpoints; related feature: Review and Retry Failed Subscription Renewals (`clm/unpaid-subscriptions/`) which pre-filters to due/overdue status |
| **Service / Repository** | sleek-billings-frontend; downstream billing API (subscription-auto-renewal service) |
| **DB - Collections** | Unknown (API-mediated; likely `customer-subscriptions` collection based on `/customer-subscriptions/search` endpoint) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Is this view restricted to SG or available across all markets? Does the manual auto-charge endpoint route to Stripe directly or through an internal queue? The `triggerManualAutoCharge` function passes `renewal._id` (subscription ID) as the body field named `companyId` — is this intentional or a naming bug? The UI shows only first and second renewal attempts; does the system support a third (manual) attempt as seen in the sibling UnpaidSubscriptionsList component? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Component
`src/pages/Subscriptions/SubscriptionsList.jsx`

### List query (`fetchRenewals`)
`src/pages/Subscriptions/SubscriptionsList.jsx:20–49`

Calls `GET /customer-subscriptions/search` (via `sleekBillingsApi.searchCustomerSubscriptions`) with pagination (100 items/page) and a MongoDB-style filter. No status pre-filter — the query matches whatever the operator types across:
- `serviceName` (regex, case-insensitive)
- `serviceType` (regex, case-insensitive)
- `serviceCode` (regex, case-insensitive)
- `subscriptionRenewalStatus` (regex, case-insensitive)
- `serviceDeliveryStatus` (regex, case-insensitive)

Search is debounced 500 ms; page resets to 1 on new search.

`src/services/api.js:179–188` — `searchCustomerSubscriptions`: `GET /customer-subscriptions/search?page=&limit=&filter=`

### Columns displayed per row
- Subscription Name (`renewal.service?.name`)
- Purpose of Purchase (`renewal.purposeOfPurchase`)
- Service Delivery Status badge: `delivered` (green) / `pending` (yellow) / `failed` (red) / other (grey)
- Renewal Status badge (`renewal.subscriptionRenewalStatus`): `active` (green) / `cancelled` (red) / other (yellow)
- Start Date (`renewal.subscriptionStartDate`)
- End Date (`renewal.subscriptionEndDate`)
- Renewal Due (`renewal.nextRenewalDate`)
- Renewal Attempts: first attempt date + `firstAutoRenewalAttemptedFailureReason`; second attempt date + `secondAutoRenewalAttemptedFailureReason`
- Amount (`renewal.service?.price`, formatted as SGD)

### Per-row action menu
`src/pages/Subscriptions/SubscriptionsList.jsx:268–312`

- **View Company** — opens Admin App at `${VITE_ADMIN_APP_URL}/admin/company-overview/?cid=${renewal.companyId}&currentPage=Billing+Beta` in a new tab
- **Manual Auto-Charge** — calls `sleekBillingsApi.triggerManualAutoCharge(renewal._id)` → `POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` with body `{ companyId: renewal._id }`; refreshes the list on success

`src/services/api.js:199–209` — `triggerManualAutoCharge`

### Auth surface
`src/services/api.js:6–19`

Bearer token (JWT) or raw token from `localStorage.auth`. `App-Origin` header set to `"admin"` or `"admin-sso"` depending on `alternate_login` flag. Internal admin tool; not customer-facing.

### Distinction from sibling feature
`clm/unpaid-subscriptions/review-and-retry-failed-subscription-renewals.md` documents `UnpaidSubscriptionsList.jsx`, which pre-filters to `subscriptionRenewalStatus: { $in: ["due", "overdue"] }` and requires at least one failed attempt. It also includes an eligible-renewals modal and surfaces a third (manual) attempt column. This `SubscriptionsList.jsx` component has no status pre-filter, no eligible-renewals modal, and shows only the first and second attempt.

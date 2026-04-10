# Recover Failed Subscription Renewal

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Recover Failed Subscription Renewal |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal admin) |
| **Business Outcome** | Operators can immediately retry a payment charge for a subscription whose auto-renewal failed, recovering revenue without waiting for the next scheduled retry cycle. |
| **Entry Point / Surface** | Sleek Billings Admin > Unpaid Subscriptions > row action menu (⋮) > "Manual Auto-Charge" |
| **Short Description** | From the Unpaid Subscriptions list, an operator opens the row action menu for any failed-renewal subscription and clicks "Manual Auto-Charge". The app posts to `/subscription-auto-renewal/trigger-manual-auto-renewal-charge` and refreshes the list on success. The table also surfaces prior attempt dates and failure reasons to help operators decide when to intervene. |
| **Variants / Markets** | SG (amounts displayed in SGD; other markets Unknown) |
| **Dependencies / Related Flows** | Subscription auto-renewal engine (backend), Unpaid Subscriptions list / search (`GET /customer-subscriptions/search`), subscription renewal attempt tracking (firstAutoRenewalAttemptedAt, secondAutoRenewalAttemptedAt fields) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-api (inferred backend) |
| **DB - Collections** | Unknown (frontend only; backend likely updates customer-subscriptions or subscription-auto-renewal collection) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. `triggerManualAutoCharge` passes the subscription `_id` as `companyId` in the POST body (`api.js:201`) — possible parameter naming mismatch between frontend and backend worth verifying. 2. Does a manual charge increment the attempt counter (`firstAutoRenewalAttemptedAt` / `secondAutoRenewalAttemptedAt`) or use a separate tracking field? 3. Is this tool available to operators in HK, UK, and AU markets, or SG-only? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

| File | Location | Detail |
|---|---|---|
| `src/pages/Subscriptions/SubscriptionsList.jsx` | `handleManualAutoCharge` (line 90–103) | Calls `sleekBillingsApi.triggerManualAutoCharge(subscriptionId)`, sets `processingCharge` loading state, then re-fetches the list. |
| `src/pages/Subscriptions/SubscriptionsList.jsx` | Row action menu (lines 270–311) | "Manual Auto-Charge" button rendered in a dropdown per row; disabled with spinner while `processingCharge === renewal._id`. |
| `src/pages/Subscriptions/SubscriptionsList.jsx` | `fetchRenewals` (lines 20–49) | Queries `GET /customer-subscriptions/search` with pagination and full-text filter across `serviceName`, `serviceType`, `serviceCode`, `subscriptionRenewalStatus`, `serviceDeliveryStatus`. |
| `src/pages/Subscriptions/SubscriptionsList.jsx` | Renewal attempts columns (lines 243–263) | Displays `firstAutoRenewalAttemptedAt`, `firstAutoRenewalAttemptedFailureReason`, `secondAutoRenewalAttemptedAt`, `secondAutoRenewalAttemptedFailureReason` — context for operator decision-making. |
| `src/services/api.js` | `triggerManualAutoCharge` (lines 199–209) | `POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` with body `{ companyId: subscriptionId }`. Auth via Bearer token; `App-Origin: admin` or `admin-sso` header. |
| `src/services/api.js` | `searchCustomerSubscriptions` (lines 179–188) | `GET /customer-subscriptions/search?page=&limit=&filter=` — paginated search backing the Unpaid Subscriptions list. |

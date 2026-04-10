# Trigger Subscription Renewal Charge

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Trigger Subscription Renewal Charge |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations Staff (BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin) |
| **Business Outcome** | Enables billing operators to manually recover failed or missed auto-renewal payments by triggering a charge attempt on demand, preventing revenue loss from subscriptions that did not renew automatically. |
| **Entry Point / Surface** | Sleek Billings Admin > Auto-Renewals |
| **Short Description** | Operators view all auto-renewal invoices, inspect prior charge attempt history (timestamp, actor, error message), and manually trigger a renewal charge for a specific company. The backend creates a renewal invoice, issues a payment token, and attempts payment through stored payment methods (card then direct debit). On failure it marks the invoice failed and sends a notification email; on success it timestamps the manual attempt on the subscription record. The "Manual Auto-Charge" action button exists in code but is currently commented out in the UI. |
| **Variants / Markets** | SG, HK, UK, AU (railway-env configs present for all four markets; currency display hard-coded to SGD in the UI) |
| **Dependencies / Related Flows** | Auto-renewal invoice list (`/invoices` with `invoiceOrigin: autoRenewal` filter); scheduled auto-renewal charge jobs (`triggerAutoRenewalCharge` via cron); payment method service; payment token service; email task (`renewal_auto_on_charge_failure_manualrequired`) |
| **Service / Repository** | sleek-billings-frontend, sleek-clm-monorepo/apps/sleek-billings-backend |
| **DB - Collections** | CustomerSubscription (fields: `isAutoRenewalEnabled`, `nextRenewalDate`, `subscriptionRenewalStatus`, `manualAutoRenewalAttemptedAt`, `manualAutoRenewalAttemptedFailedReason`), Invoice (fields: `invoiceOrigin`, `status`, `autoRenewalChargeAttemptedAt`, `autoRenewalChargeAttemptedBy`, `autoRenewalChargeError`, `autoRenewalChargeErrors`), PaymentToken (fields: `status`, `paymentError`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | 1. The "Manual Auto-Charge" button is commented out in `AutoRenewalsList.jsx` (lines 273–326) — is this intentionally disabled or pending a gate/permission rollout? 2. Parameter naming inconsistency: `handleManualAutoCharge` receives `renewal._id` (invoice ID) and passes it as `companyId` in the API body — the backend expects a `companyId`; clarify whether the call site is correct. 3. UI currency is hard-coded to SGD; confirm HK/UK/AU operators see the right currency. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `sleek-billings-frontend/src/pages/AutoRenewals/AutoRenewalsList.jsx` — UI listing auto-renewal invoices; `handleManualAutoCharge` (line 90) calls the API; the dropdown button that triggers it is commented out (lines 273–326)
- `sleek-billings-frontend/src/services/api.js:199` — `triggerManualAutoCharge`: POST `/subscription-auto-renewal/trigger-manual-auto-renewal-charge` with `{ companyId }`
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/customer-subscription/controllers/subscription-auto-renewal.controller.ts:32` — `POST trigger-manual-auto-renewal-charge`; guarded by `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)`; calls `triggerAutoRenewalCharge(companyId, isFirstCharge=true, bypassChargeAttempt=true, req.user)`
- `sleek-clm-monorepo/apps/sleek-billings-backend/src/customer-subscription/services/subscription-auto-renewal.service.ts:338` — `triggerAutoRenewalCharge`; when `bypassChargeAttempt=true` uses `manualAutoRenewalAttemptedAt` / `manualAutoRenewalAttemptedFailedReason` fields and extends the renewal window to 0–30 days ahead

### Key code paths

**Fetching auto-renewal invoices** (`AutoRenewalsList.jsx:26–41`)
```js
sleekBillingsApi.getInvoices({
  page,
  limit: 100,
  filter: JSON.stringify({
    $and: [
      { invoiceOrigin: "autoRenewal" },
      { $or: [{ number: { $regex: searchQuery } }, { title: { $regex: searchQuery } }] }
    ]
  })
})
```

**Triggering the manual charge** (`AutoRenewalsList.jsx:90–103`, `api.js:199–209`)
```js
// Component handler — passes renewal._id as subscriptionId
handleManualAutoCharge(subscriptionId) → sleekBillingsApi.triggerManualAutoCharge(subscriptionId)

// API call
POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge
Body: { companyId }   // ← value is renewal._id; naming mismatch
```

**Backend charge flow** (`subscription-auto-renewal.service.ts:338–578`)
1. Queries eligible subscriptions with `bypassChargeAttempt=true` (window: today → +30 days)
2. `InvoiceService.createRenewalInvoiceFromSubscriptionList()` creates invoice with `InvoiceOrigin.autoRenewal`
3. `PaymentTokenService.createPaymentToken()` issues a payment token
4. `payAutoRenewalInvoice()` loops payment methods (primary first), attempts `PaymentServiceV2.payWithPaymentMethod()` with `PaymentType.auto_renewal`
5. On success → updates `manualAutoRenewalAttemptedAt` on subscription
6. On failure → marks invoice `status: failed`, records `autoRenewalChargeAttemptedBy: user.email`, sends `renewal_auto_on_charge_failure_manualrequired` email task

**UI action — currently disabled** (`AutoRenewalsList.jsx:273–326`)
The dropdown menu containing "Manual Auto-Charge" is wrapped in a JSX comment block. Only "View Company" link (pointing to admin app `VITE_ADMIN_APP_URL`) is active.

**Charge attempt visibility** (`AutoRenewalsList.jsx:241–259`)
Each row shows prior charge attempt details:
- `autoRenewalChargeAttemptedAt` — timestamp of last attempt
- `autoRenewalChargeAttemptedBy` — actor who triggered it (`user.email` or `'SLEEK SYSTEM'`)
- `autoRenewalChargeError` — error message if attempt failed

**Auth surface**
Backend: JWT + group membership check (`BillingSuperAdmin`, `BillingOperationsAdmin`, `SalesAdmin`).
Frontend API client: Bearer token or raw token from `localStorage["auth"]`; `App-Origin: admin` or `admin-sso`.

**Related eligible-renewals endpoint** (`api.js:210–217`)
```
GET /subscription-auto-renewal/eligible/:companyId
```
Returns subscriptions with `isAutoRenewalEnabled=true`, `subscriptionRenewalStatus` in [notDue, due, overdue], `nextRenewalDate` within next 30 days.

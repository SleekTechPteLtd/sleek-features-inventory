# Review and Retry Failed Subscription Renewals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review and Retry Failed Subscription Renewals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal billing operator) |
| **Business Outcome** | Recover unpaid subscription revenue by surfacing all due/overdue subscriptions whose auto-renewal charge has failed, enabling operators to diagnose the failure and manually re-trigger payment before accounts lapse. |
| **Entry Point / Surface** | Sleek Billings App > Billing > Invoices > Failed Renewals (`/unpaid-subscriptions`) |
| **Short Description** | Displays a paginated, searchable list of customer subscriptions in `due` or `overdue` status that have at least one failed auto-renewal attempt. Operators can inspect per-attempt failure reasons, open an eligible-renewals modal per company, and fire a manual re-charge via the billing API. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscription auto-renewal scheduler (first/second/manual attempts); Admin App company overview (`/admin/company-overview/?cid=…&currentPage=Billing+Beta`); `searchCustomerSubscriptions` and `triggerManualAutoCharge` API endpoints; Stripe (via `PaymentServiceV2.payWithPaymentMethod`, `PaymentType.auto_renewal`); `CompanyService` offboarding gate (charges skipped if company is in offboarding status); `TaskService` email queue for charge-failure notifications (`renewal_auto_on_charge_failure_manualrequired` template); `InvoiceService.createRenewalInvoiceFromSubscriptionList`; `PaymentTokenService` |
| **Service / Repository** | sleek-clm-monorepo (apps/sleek-billings-frontend); sleek-billings-backend (subscription-auto-renewal controller + service) |
| **DB - Collections** | `customersubscriptions`, `invoices`, `paymenttokens` (all MongoDB via Mongoose in sleek-billings-backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which market(s) are affected (SG/HK/UK/AU)? What triggers the automated first/second attempts (cron job, event)? The `getEligibleRenewals` call has a TODO comment in the frontend suggesting it may not reflect final implementation. Duplicate-service-code guard logs an error and records a failure reason but does not notify the operator in the UI — is that intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- Route: `src/App.jsx:163` — `<Route path="unpaid-subscriptions" element={<UnpaidSubscriptionsList />} />`
- Nav label: `src/data/nav-rail-items.js:41` — `"Failed Renewals"` under **Billing > Invoices**
- Home card: `src/pages/Home.jsx:34` — `"Track failed subscription renewals"`

### List query (fetchRenewals)
`src/pages/UnpaidSubscriptions/UnpaidSubscriptionsList.jsx:27–86`

Calls `GET /customer-subscriptions/search` with a MongoDB-style filter:
```json
{
  "subscriptionRenewalStatus": { "$in": ["due", "overdue"] },
  "$or": [
    { "firstAutoRenewalAttemptedAt": { "$exists": true }, "firstAutoRenewalAttemptedFailedReason": { "$ne": null } },
    { "secondAutoRenewalAttemptedAt": { "$exists": true }, "secondAutoRenewalAttemptedFailedReason": { "$ne": null } },
    { "manualAutoRenewalAttemptedAt": { "$exists": true }, "manualAutoRenewalAttemptedFailedReason": { "$ne": null } }
  ]
}
```
Pagination: 100 items/page. Search by `serviceName`, `serviceType`, `serviceCode`, `subscriptionRenewalStatus`, `serviceDeliveryStatus`.

### Columns displayed per subscription
- Company Name (extracted from `invoice.title` or `migrateOnlyCompanyCompanyName`)
- Subscription Name (`service.name`)
- Purpose of Purchase (`purposeOfPurchase`)
- Service Delivery Status: `delivered` / `pending` / `failed`
- Renewal Status: `active` / `cancelled` / `due` / `overdue`
- Subscription Start / End Date, Next Renewal Due Date
- Renewal Attempts (date + failure reason per attempt): `firstAutoRenewalAttemptedAt/FailedReason`, `secondAutoRenewalAttemptedAt/FailedReason`, `manualAutoRenewalAttemptedAt/FailedReason`
- Amount (`service.price`)

### Manual re-charge (per-subscription)
`src/pages/UnpaidSubscriptions/UnpaidSubscriptionsList.jsx:139–152`
`src/services/api.js:199–209`

`POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` with `{ companyId }`.  
After success, list is refreshed.

Backend guard: `@GroupAuth(Group.BillingSuperAdmin, Group.BillingOperationsAdmin, Group.SalesAdmin)` — restricted to billing/sales admins only (`sleek-billings-backend/src/customer-subscription/controllers/subscription-auto-renewal.controller.ts:34`).

### Eligible renewals modal
`src/pages/UnpaidSubscriptions/UnpaidSubscriptionsList.jsx:170–200, 202–280`
`src/services/api.js:210–216`

"Renew" button → `GET /subscription-auto-renewal/eligible/:companyId` → modal shows all eligible subscriptions with service name, price, and next renewal date → "Renew All" fires `triggerManualAutoCharge(companyId)` for the whole company.

### Admin cross-link
Action column links to Admin App company billing overview:  
`${VITE_ADMIN_APP_URL}/admin/company-overview/?cid=${renewal.companyId}&currentPage=Billing+Beta`

### Backend charge flow (`SubscriptionAutoRenewalService.triggerAutoRenewalCharge`)
`sleek-billings-backend/src/customer-subscription/services/subscription-auto-renewal.service.ts`

When `bypassChargeAttempt=true` (manual trigger):
- Attempt date field: `manualAutoRenewalAttemptedAt` / `manualAutoRenewalAttemptedFailedReason`
- Renewal window: today → +30 days (broader than scheduled auto-renewal)
- Offboarding gate: `CompanyService.getCompanyDetails` → skips charge if company in offboarding status
- Creates a renewal invoice: `InvoiceService.createRenewalInvoiceFromSubscriptionList` (`InvoiceOrigin.autoRenewal`)
- Creates payment token: `PaymentTokenService.createPaymentToken`
- Charges via `PaymentServiceV2.payWithPaymentMethod` (type: `auto_renewal`), iterating payment methods (primary first); skips expired cards
- DD in-progress path: records attempt date, clears failure reason, waits for gateway callback
- On success: clears `manualAutoRenewalAttemptedFailedReason`, stamps `manualAutoRenewalAttemptedAt`
- On failure: sets `InvoiceStatus.failed`, stamps `autoRenewalChargeAttemptedBy` (operator email or "SLEEK SYSTEM"), sets `PaymentTokenStatus.FAILED`, stores error reason on subscription; sends `renewal_auto_on_charge_failure_manualrequired` email via `TaskService`
- Duplicate-service-code guard: logs error and records failure reason without charging
- 10-second sleep between companies to avoid gateway rate limits

### `getEligibleRenewals`
`sleek-billings-backend/src/customer-subscription/services/subscription-auto-renewal.service.ts:706–725`

Returns auto-renewal-enabled subscriptions for a company with `nextRenewalDate` within the next 30 days and status in `[notDue, due, overdue]`. Populates `service` relation.

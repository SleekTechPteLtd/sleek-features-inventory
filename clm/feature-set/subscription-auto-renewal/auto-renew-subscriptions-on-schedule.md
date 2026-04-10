# Auto-renew subscriptions on schedule

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Auto-renew subscriptions on schedule |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Ensures recurring subscription revenue is collected automatically on renewal dates without requiring manual intervention, reducing churn from missed renewals. |
| **Entry Point / Surface** | Scheduled cron job (daily at 6AM for reminders, 7AM for charges); manual trigger via internal API `POST /subscription-auto-renewal/trigger-manual-auto-renewal-charge` (BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin only) |
| **Short Description** | A daily scheduler identifies subscriptions due for renewal and either sends pre-renewal reminder emails (at T-45 early and T-30/T-11 charge reminders) or initiates up to two automatic charge attempts by creating a renewal invoice and processing payment via stored payment methods. Failed charges mark the invoice as failed and notify the customer to renew manually. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | InvoiceService (create renewal invoices, `InvoiceOrigin.autoRenewal`), PaymentServiceV2 (Stripe card / direct debit), PaymentMethodService (stored payment methods), PaymentTokenService (payment token lifecycle), TaskService → sendEmail (reminder and failure emails), CompanyService (offboarding guard — skips companies in offboarding status), CreditCardService (card expiry check), subscription-config (ServiceStatus, ClientType) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions`, `invoices`, `paymenttokens`, `emaillogs` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/jurisdictions does auto-renewal apply to? The code has no market filter. 2. What is the UTC_OFFSET configured to in production (affects when 6AM/7AM cron fires)? 3. Is the `SWITCH_TO_SLEEK_BILLINGS` feature flag enabled in all envs or only some? 4. Second charge for monthly subscriptions: code only runs a second charge attempt for yearly (line 377 shows monthly is first-attempt only) — intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry points

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `POST` | `/subscription-auto-renewal/trigger-reminders-auto-renewal-early-reminder` | `@Auth()` | Manually trigger T-45 early reminder run |
| `POST` | `/subscription-auto-renewal/trigger-reminders-auto-renewal-charge-reminder` | `@Auth()` | Manually trigger charge reminder run |
| `POST` | `/subscription-auto-renewal/trigger-auto-renewal-charge` | `@Auth()` | Manually trigger 1st + 2nd charge attempt |
| `POST` | `/subscription-auto-renewal/trigger-manual-auto-renewal-charge` | `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)` | Admin-initiated forced charge (bypasses attempt date filter) |
| `GET` | `/subscription-auto-renewal/eligible/:companyId` | `@Auth()` | Preview subscriptions eligible for renewal in the next 30 days |

### Scheduler (`subscription-auto-renewal-scheduler.service.ts`)

- **6AM cron** (`EVERY_DAY_AT_6AM`, UTC offset from env): calls `triggerAutoRenewalEarlyReminders()` then `triggerAutoRenewalChargeReminders()`
- **7AM cron** (`EVERY_DAY_AT_7AM`): calls `triggerAutoRenewalCharge(undefined, true)` (1st attempt) then `triggerAutoRenewalCharge(undefined, false)` (2nd attempt)
- Both crons are gated on `SWITCH_TO_SLEEK_BILLINGS === 'enabled'`

### Renewal timing windows (from `shared/consts/common.ts`)

| Phase | Service type | Days before renewal date |
|---|---|---|
| Early reminder (T-45) | Yearly only | 45 days |
| Charge reminder | Yearly | 30 days |
| Charge reminder | Monthly | 11 days |
| 1st charge attempt | Yearly | 27 days |
| 1st charge attempt | Monthly | 4 days |
| 2nd charge attempt | Yearly | 20 days |

### Eligibility filter (`getSubscriptionsForAutoRenewal`)

- `isAutoRenewalEnabled: true`
- `nextRenewalDate` within the computed window
- `subscriptionRenewalStatus` in `[notDue, due, overdue]`
- Service must be `recurring`, `status === active`, `clientType !== manageService`
- Skips subscriptions already covered by an in-progress direct-debit invoice (`InvoiceStatus.ddInProgress`)
- Skips companies in offboarding status

### Charge flow (`triggerAutoRenewalCharge` + `payAutoRenewalInvoice`)

1. `invoiceService.createRenewalInvoiceFromSubscriptionList(companyId, subscriptions, InvoiceOrigin.autoRenewal)`
2. `paymentTokenService.createPaymentToken({ companyId, invoice })`
3. For invoices with zero total after discounts: `paymentServiceV2.resolveZeroAmountPayment()`
4. Otherwise iterate payment methods (primary first); attempt `paymentServiceV2.payWithPaymentMethod()` with `PaymentType.auto_renewal`
5. Success → update `firstAutoRenewalAttemptedAt` / `secondAutoRenewalAttemptedAt`; DD in progress → same update
6. Failure → set invoice status to `failed`, update payment token to `FAILED`, send `renewal_auto_on_charge_failure_manualrequired` email via TaskService
7. Same-user rate limiting: 60-second sleep between companies sharing a company admin user (Stripe rate limit guard)

### Email templates used

| Template | Trigger |
|---|---|
| `renewal_auto_on_early_reminder_grouped` | T-45 early reminder, card on file and not expired |
| `renewal_auto_on_charge_reminder_grouped` | Charge reminder, valid payment method exists |
| `renewal_auto_on_cardexpiry_reminder_grouped` | Charge reminder, only card PM and card expires before charge date |
| `reminder_to_do_manual_renewal` | Charge reminder, no payment method on file |
| `renewal_auto_on_charge_failure_manualrequired` | Charge attempt failed |

### Key schema fields (`CustomerSubscription`)

- `isAutoRenewalEnabled`, `nextRenewalDate`, `subscriptionRenewalStatus`
- `firstAutoRenewalAttemptedAt`, `firstAutoRenewalAttemptedFailedReason`
- `secondAutoRenewalAttemptedAt`, `secondAutoRenewalAttemptedFailedReason`
- `manualAutoRenewalAttemptedAt`, `manualAutoRenewalAttemptedFailedReason`
- `chargeAttemptReminderSentAt`, `chargeAttemptEarlyReminderSentAt`

### File paths

- `src/customer-subscription/controllers/subscription-auto-renewal.controller.ts`
- `src/customer-subscription/services/subscription-auto-renewal.service.ts`
- `src/customer-subscription/services/subscription-auto-renewal-scheduler.service.ts`
- `src/customer-subscription/subscription-auto-renewal-scheduler.module.ts`
- `src/customer-subscription/models/customer-subscription.schema.ts`
- `src/shared/consts/common.ts` (timing constants)

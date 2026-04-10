# Auto-charge Subscription Upgrade Invoice

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Auto-charge Subscription Upgrade Invoice |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Eliminates manual billing steps on plan upgrades by automatically charging the pending upgrade invoice via the company's stored payment method, ensuring revenue is captured without ops intervention |
| **Entry Point / Surface** | Scheduled cron (daily at 6 AM local time via `SubscriptionAutoUpgradeSchedulerService`); also manually triggerable via `POST /v2/payment/auto-charge-invoice-upgrade` (authenticated) |
| **Short Description** | Queries all `autoUpgrade`-origin invoices in `authorised` status due by the end-of-day cutoff, then charges each via the company's stored payment method. On success marks the subscription `autoUpgraded` (or `directDebitInprogress` for Direct Debit); on failure records the charge error and dispatches a payment-failure email containing a recovery payment link. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `PaymentServiceV2.chargePaymentMethod` (Stripe charge execution); `InvoiceService.cancelAutoUpgrade` (duplicate or already-upgraded path); `InvoiceService.generatePaymentToken` (failure recovery link); `TaskService` → `EmailTemplate.auto_upgrade_payment_failed` (failure notification email); `SWITCH_TO_SLEEK_BILLINGS` feature flag (scheduler gate) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | invoices, customersubscriptions, paymenttokens, tasks |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) `SWITCH_TO_SLEEK_BILLINGS` flag gates the scheduler — unclear what proportion of customers are on SleekBillings vs legacy billing; (2) No market-specific branching found — unclear if all markets (SG, HK, AU, UK) are in scope; (3) The manual trigger endpoint has only `@Auth()` with no role guard — unclear whether force-charge is restricted to internal/ops users |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry points

| Surface | Detail |
|---|---|
| Cron scheduler | `SubscriptionAutoUpgradeSchedulerService` — `@Cron(EVERY_DAY_AT_6AM, { utcOffset: UTC_OFFSET })` — gated by `SWITCH_TO_SLEEK_BILLINGS === 'enabled'` |
| REST endpoint | `POST /v2/payment/auto-charge-invoice-upgrade` — `@Auth()` guard, no role restriction — accepts optional `companyId` (per-company run) and `isForceCharge` (bypass date cutoff) |

### Key service logic (`subscription-auto-upgrade.service.ts`)

- `triggerAutoChargeInvoiceAutoUpgrade(companyId?, isForceCharge = false)`:
  1. Resolves end-of-day cutoff (`23:59`) adjusted by `UTC_OFFSET` env var
  2. Queries `invoiceRepository.find({ invoiceOrigin: InvoiceOrigin.autoUpgrade, status: InvoiceStatus.authorised, autoChargeDate: { $lte: cutoff } })` — `autoChargeDate` filter skipped when `isForceCharge = true`
  3. For each invoice: locates company admin, finds subscription by `upgradeInvoiceId`, validates `upgradeStatus === UpgradeStatus.pendingCharge`
  4. Skips if subscription already in `SubscriptionRenewalStatus.upgraded` → calls `invoiceService.cancelAutoUpgrade`
  5. Calls `paymentServiceV2.chargePaymentMethod({ companyId, invoiceId }, masterUser)` inside a CLS context
  6. **Success path**: sets `upgradeStatus = autoUpgraded`; if payment token is `DD_IN_PROGRESS`, sets `directDebitInprogress` instead
  7. **Duplicate invoice path**: calls `invoiceService.cancelAutoUpgrade`, throws `DUPLICATE_INVOICE` (caught, skips to next)
  8. **Failure path**: sets `upgradeStatus = failedCharge`, stores `chargeError` on invoice, generates a payment token, enqueues `auto_upgrade_payment_failed` email task
  9. 10-second sleep between invoices (`sleep(10 * 1000)`)

### DTO (`auto-charge-invoice-upgrade.request.dto.ts`)

```ts
companyId?: string      // optional — omit to run for all companies
isForceCharge?: boolean // default false — bypasses autoChargeDate filter
```

### Collections touched

| Collection | Access pattern |
|---|---|
| `invoices` | Query by `invoiceOrigin`, `status`, `autoChargeDate`; update `autoRenewalChargeErrors`, `chargeError` |
| `customersubscriptions` | Find by `upgradeInvoiceId`; update `upgradeStatus` |
| `paymenttokens` | Read by `invoice.paymentTokenId` to detect Direct Debit status |
| `tasks` | Write (via `TaskService.createTask`) to enqueue failure email |

### External services

- **Stripe** — charge execution via `PaymentServiceV2.chargePaymentMethod`
- **Email system** — `EmailTemplate.auto_upgrade_payment_failed` dispatched through task queue on charge failure

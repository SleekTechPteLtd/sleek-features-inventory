# Manage Accounting Upgrades

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Accounting Upgrades |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal billing ops / CLM team) |
| **Business Outcome** | Enables operators to identify accounting subscriptions eligible for tier upgrades, monitor outstanding charge amounts, and surface the right upsell plan — reducing manual effort and ensuring revenue is captured when clients exceed their plan limits. |
| **Entry Point / Surface** | CLM Billing Admin > Subscriptions > Accounting Upgrades |
| **Short Description** | Operators search and filter accounting subscriptions by upgrade status, expense/transaction limit breaches, or free-text; view the total pending charge amount across all pending upgrades; and retrieve suggested higher-tier plans based on a client's current usage. An automated nightly job charges pending upgrade invoices via the stored payment method and notifies clients if payment fails. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Upstream: accounting subscription creation, FYE date management, invoice auto-upgrade creation (`InvoiceService.cancelAutoUpgrade`); Downstream: `PaymentServiceV2.chargePaymentMethod` (card/DD charging), `TaskService` email task (`auto_upgrade_payment_failed` template), `SubscriptionConfigService.getSuggestedServiceMinimum` (tier recommendation) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions, invoices, services, companies, syncaccountingexpensesfyes, paymenttokens |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. What triggers the nightly `triggerAutoChargeInvoiceAutoUpgrade` call — a scheduler job or an external cron? The scheduler service is injected but the trigger entrypoint is not in the scoped files. 2. Are there markets beyond SG/HK where accounting upgrades are offered (AU, UK)? 3. Who has access to the `BillingSuperAdmin` group vs standard `@Auth()` — relevant for patch/mass-patch actions that sit adjacent to this flow. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `customer-subscription/controllers/customer-subscription.controller.ts`

| Endpoint | Method | Auth | Purpose |
|---|---|---|---|
| `GET /customer-subscriptions/search/accounting-upgrades` | `searchAccountingUpgrades` | `@Auth()` | Search/filter accounting upgrade subscriptions by companyId, serviceId, searchTerm, searchFilter (`exceeded-expense-limit`, `exceeded-transaction-limit`) |
| `GET /customer-subscriptions/accounting-upgrades/analytics/pending-charge` | `getTotalPendingUpgradesChargeAmount` | `@Auth()` | Returns sum of `upgradeInvoice.totalAmount` for all subscriptions in `upgradeStatus: pendingCharge` |
| `GET /customer-subscriptions/suggested-subscriptions` | `getSuggestedSubscriptions` | `@Auth()` | Returns the recommended higher-tier service for a given subscription + current usage count (`metaNumber`) |

### Service — `customer-subscription/services/customer-subscription.service.ts`

**`searchAccountingUpgrades` (line 1205)**
- Aggregation pipeline: matches `customersubscriptions`, joins `services` (filters `type: 'accounting'`, `tier != NonUpgradeable`), joins `invoices` (upgradeInvoice), joins `companies`, joins `syncaccountingexpensesfyes` (expense/transaction counts vs plan limits)
- `financialYearEnd` range: last 3 years → next 18 months (when no upgradeStatus filter present)
- Excludes companies in `EXCLUDED_COMPANY_STATUSES_AUTO_UPGRADES`
- Optional filter `exceeded-expense-limit`: `accountingExpenses.total_expense_currency_converted > service.metaNumber`
- Optional filter `exceeded-transaction-limit`: `accountingExpenses.transaction_count > service.metaNumber`

**`getSuggestedSubscriptions` (line 1385)**
- Looks up subscription → delegates to `subscriptionConfigService.getSuggestedServiceMinimum(serviceId, metaNumber)` to find the lowest tier that covers the client's current usage

**`getTotalPendingUpgradesChargeAmount` (line 1775)**
- Aggregation: match `upgradeStatus: pendingCharge` (excluding `upgraded`/`downgraded`), join invoices, `$sum` of `upgradeInvoice.totalAmount`

### Service — `customer-subscription/services/subscription-auto-upgrade.service.ts`

**`triggerAutoChargeInvoiceAutoUpgrade` (line 42)**
- Finds `invoices` where `invoiceOrigin: autoUpgrade`, `status: authorised`, `autoChargeDate <= today-cutoff` (UTC-offset aware, cutoff 23:59)
- Per invoice: fetches company admin via `CompanyUserService`; finds linked subscription via `upgradeInvoiceId`; skips if not `upgradeStatus: pendingCharge` or already `subscriptionRenewalStatus: upgraded`
- Calls `PaymentServiceV2.chargePaymentMethod`
- On success: sets `upgradeStatus = autoUpgraded` (or `directDebitInprogress` if DD token)
- On failure: sets `upgradeStatus = failedCharge`, generates payment token, queues `auto_upgrade_payment_failed` email via `TaskService`
- On duplicate invoice: calls `InvoiceService.cancelAutoUpgrade`, skips

### Schema — `customer-subscription/models/customer-subscription.schema.ts`

**`UpgradeStatus` enum (line 42):** `pendingCharge | failedCharge | cancelledCharge | noPaymentMethod | autoUpgraded | manualUpgraded | directDebitInprogress | cancelledVoided`

Key indexed fields: `upgradeStatus`, `upgradeInvoiceId`, `financialYearEnd`

### DTOs

- `SearchAccountingUpgradesDto` — extends `BaseGetListRequestDto`; fields: `companyId`, `serviceId`, `searchTerm`, `searchFilter`
- `GetSuggestedSubscriptionsRequestDto` — fields: `subscriptionId` (string), `metaNumber` (number)

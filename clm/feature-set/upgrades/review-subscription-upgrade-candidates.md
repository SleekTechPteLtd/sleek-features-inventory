# Review Subscription Upgrade Candidates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review subscription upgrade candidates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables operators to identify accounting clients whose expense or transaction volumes have exceeded their current plan limits, initiate tiered upgrades with automatic payment collection, and track each upgrade from creation through charge completion. |
| **Entry Point / Surface** | Sleek Billings Admin > Upgrades Dashboard (`/upgrades` and `/upgrades-initiated`) |
| **Short Description** | Operators view paginated lists of active client subscriptions filterable by upgrade eligibility or upgrade lifecycle status, initiate upgrades to higher-tier plans (auto-charging the client in 5 days), cancel pending upgrades, and export the full dataset to CSV. A separate view (`/upgrades-initiated`) tracks in-progress and completed upgrades with aggregate pending charge totals. |
| **Variants / Markets** | SG, HK, AU |
| **Dependencies / Related Flows** | Subscription Config (plan catalogue, pricing tiers); Invoice Service (`/invoices/auto-upgrade`); Payment Auto-Charge (`/v2/payment/auto-charge-invoice-upgrade`); Admin App company overview (deep-link per company); Accounting Expenses sync (`syncaccountingexpensesfyes` — expense/transaction counts used to detect limit breaches) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend |
| **DB - Collections** | `customersubscriptions` (upgradeStatus, upgradeInvoiceId, subscriptionRenewalStatus, serviceDeliveryStatus, financialYearEnd, nextRenewalDate, subscriptionEndDate); `syncaccountingexpensesfyes` (total_expense_currency_converted, total_revenue_currency_converted, transaction_count — joined by companyId + financialYearEnd month); `services` (tier, type, price, metaNumber — upgrade threshold); `invoices` (upgrade invoice, autoChargeDate, items, chargeError, cancelledUpgradeReason); `companies` (name, status — excluded statuses filter applied) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UK market support unclear — `SubscriptionPriorityLabel` in service-delivery-api only defines SG/HK/AU labels; `directDebitInprogress` status exists in the enum and is handled in the UI badge but has no dedicated filter — is direct debit initiated externally?; `UpgradesPending.jsx` exists but is not wired into the current router — is it dead code?; `service.metaNumber` is the expense/transaction threshold — is it documented or visible to operators anywhere? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry points (routes — `src/App.jsx:188-189`)
- `GET /upgrades` → `<UpgradesList />` — candidate review mode (default filter: `all-active-and-upgradeable`)
- `GET /upgrades-initiated` → `<UpgradesList mode="upgrades-initiated" />` — lifecycle tracking mode (default filter: `all-statuses`)

### Main list component (`src/pages/Upgrades/UpgradesList.jsx`)
- Calls `sleekBillingsApi.searchAccountingUpgrades({ page, limit, filter, searchTerm, searchFilter })` → `GET /customer-subscriptions/search/accounting-upgrades`
- Calls `sleekBillingsApi.getAllSubscriptionConfig()` → fetches plan catalogue for upgrade-target selection
- Calls `sleekBillingsApi.getTotalPendingUpgradesChargeAmount()` → `GET /customer-subscriptions/accounting-upgrades/analytics/pending-charge` (upgrades-initiated mode only)
- Filter modes:
  - `all-active-and-upgradeable` — active subscriptions with no existing upgradeStatus
  - `expenses-limit-exceeded` — searchFilter `exceeded-expense-limit`
  - `transaction-limit-exceeded` — searchFilter `exceeded-transaction-limit`
  - `all-statuses` — any subscription with a non-null upgradeStatus
  - `in-progress` — upgradeStatus in `[pendingCharge, failedCharge, cancelledCharge, noPaymentMethod, cancelledVoided]`
  - `pending-charge` — upgradeStatus `pendingCharge`
  - `completed` — subscriptionRenewalStatus in `[upgraded, downgraded]`, upgradeStatus in `[autoUpgraded, manualUpgraded]`
- Columns displayed: Company Name (deep-linked to Admin app), Current Subscription, Total Expense, Total Revenue, Total Transactions, Service FY, Renewal Status, Subscription End Date, Renewal Due, Upgrade Status, Charge Date, Upgrade Subscription, Top-up Amount
- CSV export: batches 200 rows per request until all pages exhausted; downloads `upgrades-export-<date>.csv`

### Upgrade action (`src/pages/Upgrades/UpgradeAction.jsx`)
- Operator selects target higher-tier plan (same type, longer or equal duration, higher price, must have `paymentRequest` in `display`)
- Guard: blocks upgrade if renewal is due within 8 days to avoid subscription conflicts
- Calls `sleekBillingsApi.createAutoUpgradeInvoice({ subscriptionId, upgradeToServiceId })` → `POST /invoices/auto-upgrade`
- Success path: invoice has `autoChargeDate` — customer's saved card is charged in 5 days
- No-payment-method path: payment link sent to customer automatically
- Top-up amount = selected plan price − current plan price

### Upgrade cancellation (`src/pages/Upgrades/UpgradeCancellation.jsx`)
- Available only when upgradeStatus = `pendingCharge`
- Calls `sleekBillingsApi.cancelAutoUpgrade({ subscriptionId })` → `POST /invoices/auto-upgrade/{subscriptionId}/cancel`

### Force charge (`src/pages/Upgrades/ForceChargeButton.jsx`)
- Non-production environments only (`localStorage.getItem('environment') !== 'production'`)
- Calls `sleekBillingsApi.forceChargeInvoiceUpgrade({ companyId, isForceCharge: true })` → `POST /v2/payment/auto-charge-invoice-upgrade`

### Constants (`src/lib/constants.jsx:310-317`)
```
UPGRADE_STATUS = {
  pendingCharge, failedCharge, cancelledCharge,
  noPaymentMethod, autoUpgraded, manualUpgraded
}
```
Additional statuses observed in UI: `cancelledVoided`, `directDebitInprogress`

### Accounting data fields used for limit detection
- `accountingExpenses.total_expense_currency_converted`
- `accountingExpenses.total_revenue_currency_converted`
- `accountingExpenses.transaction_count`

### Backend service (`sleek-billings-backend`)

**Controller** — `src/customer-subscription/controllers/customer-subscription.controller.ts`
- `GET /customer-subscriptions/search/accounting-upgrades` — `@Auth()` guard; query params via `SearchAccountingUpgradesDto`
- `GET /customer-subscriptions/accounting-upgrades/analytics/pending-charge` — `@Auth()` guard; returns aggregate total of pending charge amounts

**Service** — `src/customer-subscription/services/customer-subscription.service.ts` (method `searchAccountingUpgrades`, ~lines 1205–1380)
- MongoDB aggregation across `customersubscriptions` → `services` → `invoices` → `companies` → `syncaccountingexpensesfyes`
- Base candidate filter: `financialYearEnd` between 3 years ago and 18 months ahead; `service.type === 'accounting'`; `service.tier != NonUpgradeable`
- Excluded company statuses applied via `EXCLUDED_COMPANY_STATUSES_AUTO_UPGRADES` constant
- `exceeded-expense-limit` filter: `accountingExpenses.total_expense_currency_converted > service.metaNumber` (service name must not match `/trxn/i`)
- `exceeded-transaction-limit` filter: `accountingExpenses.transaction_count > service.metaNumber` (service name must match `/trxn/i`)
- Default sort: `subscriptionEndDate: 1`

**Schema** — `src/customer-subscription/models/customer-subscription.schema.ts`
- `UpgradeStatus` enum: `pendingCharge`, `failedCharge`, `cancelledCharge`, `noPaymentMethod`, `autoUpgraded`, `manualUpgraded`, `directDebitInprogress`, `cancelledVoided`
- `SubscriptionRenewalStatus` enum: `none`, `notDue`, `due`, `overdue`, `renewed`, `upgraded`, `downgraded`, `cancelled`
- Compound indexes on `(subscriptionRenewalStatus, nextRenewalDate)`, `(subscriptionRenewalStatus, upgradeStatus)`, and `(financialYearEnd, upgradeStatus)` serve this query

**Schema** — `src/accounting-upgrades/models/sync-accounting-expenses-fye.schema.ts`
- Collection: `syncaccountingexpensesfyes`
- Joined by `companyId` + `financialYearEnd` month match (`%Y-%m` format)
- Compound index: `(companyid, entity_code)` and `(companyid, company_financial_year_end)`

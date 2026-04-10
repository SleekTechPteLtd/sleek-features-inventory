# Manage Financial Year End

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Financial Year End |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Ensures accounting subscription periods align with a company's financial year end so that billing cycles and deliverable windows reflect the correct accounting period. |
| **Entry Point / Surface** | Internal Ops Tool > Customer Subscriptions > subscription detail — update FYE date or trigger bulk FYE recalculation |
| **Short Description** | Operators can update the financial year end (FYE) date on an individual subscription, or trigger a bulk recalculation that back-fills FYE, subscription start/end dates, and next renewal date for all active accounting subscriptions under a company. Both actions write an audit log entry. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Company profile (source of `current_fye` and `incorporation_date`); `SubscriptionDateCalculator` utility (derives start/end/renewal dates from FYE); `sleek-service-delivery-api` change-stream listener (auto-creates deliverables when subscription dates change); Audit Logs service |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customer-subscriptions |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which UI surfaces expose the FYE update controls (internal ops tool, admin panel, or both)? 2. Is `triggerFyeUpdates` called automatically when a company FYE changes in the company profile, or exclusively on-demand by operators? 3. Are there notification/email flows triggered after an FYE update? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Endpoints

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `PUT` | `/customer-subscriptions/:id/financial-year-end` | `@Auth()` | Update FYE date on a single subscription |
| `POST` | `/customer-subscriptions/trigger-fye-updates` | `@Auth()` | Bulk-recalculate FYE and subscription dates for all eligible subscriptions under a company |

**Files:**
- `customer-subscription/controllers/customer-subscription.controller.ts` — lines 111–118 (`updateFinancialYearEnd`), lines 85–88 (`triggerFyeUpdates`)

### `updateFinancialYearEnd` (CustomerSubscriptionService)

- Accepts `financialYearEnd` (year string) and `financialYearEndUpdateReason`.
- Adjusts the year component of the stored FYE date, writes `selectedFinancialYear`, `financialYearEnd`, and `financialYearEndUpdateReason` back to the subscription document.
- Creates an audit log: `"updated the Service FYE from <old> to <new> (Reason: ...)"`.
- File: `customer-subscription/services/customer-subscription.service.ts` — lines 841–882

### `triggerFyeUpdates` (FyeUpdateService)

- Accepts `companyId` and optional `fye` override; falls back to `company.current_fye`.
- Fetches all company subscriptions; filters to:
  - Accounting-type subscriptions missing `financialYearEnd` or `subscriptionStartDate` (not inactive).
  - Subscriptions tagged `"Start date = Incorp date"` with `calendar_year` billing and missing `subscriptionStartDate`.
- For each eligible subscription: derives `subscriptionStartDate`, `financialYearEnd`, `subscriptionEndDate`, `nextRenewalDate`, and `serviceDeliveryStatus` via `SubscriptionDateCalculator`.
- Handles linked subscriptions (renewals, same-period upgrades, retroactive upgrades) by updating their `subscriptionRenewalStatus` / `serviceDeliveryStatus`.
- Persists changes via `customerSubscriptionRepository.updateById`.
- Downstream deliverable creation is handled automatically by the `sleek-service-delivery-api` change-stream listener.
- File: `customer-subscription/services/fye-update.service.ts`

### DTOs

- `UpdateFinancialYearEndDto` — `financialYearEnd: string`, `financialYearEndUpdateReason?: string`
- `TriggerFyeUpdatesDto` — `companyId: MongoId`, `fye?: ISO8601 string`

### Schema fields (customer-subscriptions collection)

- `financialYearEnd: Date`
- `financialYearEndUpdateReason: string`
- `selectedFinancialYear: number`
- `subscriptionStartDate`, `subscriptionEndDate`, `nextRenewalDate` — recalculated during bulk trigger
- Indexes: `financialYearEnd` (single), compound with `upgradeStatus`, compound with `serviceId`

# Manage Upgrade Pipeline

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Upgrade Pipeline |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives billing operators a single dashboard to monitor every accounting subscription upgrade in flight — seeing what is pending charge, failed, or completed — so they can act on exceptions, cancel erroneous upgrades, and report on pipeline health before revenue is collected. |
| **Entry Point / Surface** | Sleek Billings App > Upgrades Dashboard (two modes: "upgrades-initiated" for in-flight upgrades; default mode for active/upgradeable subscriptions) |
| **Short Description** | Operators search, filter, and paginate through accounting subscription upgrades across all status states (pendingCharge, failedCharge, cancelledCharge, noPaymentMethod, cancelledVoided, autoUpgraded, manualUpgraded, directDebitInprogress). The dashboard surfaces a real-time aggregate of total pending charge amounts, allows operators to cancel a scheduled upgrade or force-charge a pending upgrade invoice, and exports the full filtered dataset as a CSV. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Initiate Upgrade (UpgradeAction component); Subscription Config (getAllSubscriptionConfig used to calculate top-up amounts); sleek-billings-backend (all API calls); Sleek Admin App (company-overview deep-link per row) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend |
| **DB - Collections** | Unknown (backend not read; frontend queries customer-subscriptions collection via API) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Force-charge button is suppressed in production (`localStorage.getItem('environment') !== 'production'`) — is this intentional or a temporary guard? 2. Which markets/countries does accounting upgrades cover? 3. What backend service owns the `/v2/payment/auto-charge-invoice-upgrade` endpoint — is it a separate payments service? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files read
- `src/pages/Upgrades/UpgradesList.jsx` — main dashboard component
- `src/pages/Upgrades/UpgradeCancellation.jsx` — cancel-upgrade dialog
- `src/pages/Upgrades/ForceChargeButton.jsx` — force-charge dialog (non-production only)
- `src/services/api.js` (lines 189–318) — API wrappers

### API calls
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/customer-subscriptions/search/accounting-upgrades` | Paginated, filterable list of upgrades (30 per page; CSV export batches 200 at a time) |
| GET | `/customer-subscriptions/accounting-upgrades/analytics/pending-charge` | Aggregate total of all pending charge amounts (shown as KPI in upgrades-initiated mode) |
| POST | `/invoices/auto-upgrade/{subscriptionId}/cancel` | Cancel a scheduled upgrade (only available when `upgradeStatus === pendingCharge`) |
| POST | `/v2/payment/auto-charge-invoice-upgrade` | Immediately charge the upgrade invoice (non-production only; passes `companyId` + `isForceCharge: true`) |
| GET | `/subscription-config` (getAllSubscriptionConfig) | Fetch all subscription tiers to calculate next-tier top-up price when no invoice yet exists |

### Upgrade statuses tracked
`pendingCharge`, `failedCharge`, `cancelledCharge`, `noPaymentMethod`, `cancelledVoided`, `autoUpgraded`, `manualUpgraded`, `directDebitInprogress`

### Filter modes
- **Default mode** (active/upgradeable): filters by `subscriptionEndDate != null`, `subscriptionRenewalStatus` in [due, overdue, renewed, notDue, cancelled], `serviceDeliveryStatus` in [active, toBeStarted, delivered]; optional sub-filters for expenses-limit-exceeded and transaction-limit-exceeded
- **upgrades-initiated mode**: filters by `upgradeStatus != null`; sub-filters for in-progress, pending-charge, completed

### CSV export columns
Company Name, Current Subscription Name, Total Expense, Total Revenue, Total Transactions, Service FY, Renewal Status, Subscription End Date, Renewal Due, Upgrade Status, Charge Date, Top-up Amount

### Key UI behaviours
- URL `?filter=<value>` persists the selected filter across navigation
- Company Name cell links to `VITE_ADMIN_APP_URL/admin/company-overview/?cid=…&currentPage=Billing+Beta`
- Top-up amount falls back to `nextHigherService.price - currentService.price` if no upgrade invoice exists yet
- Force-charge button hidden in production (`localStorage.getItem('environment') !== 'production'`)

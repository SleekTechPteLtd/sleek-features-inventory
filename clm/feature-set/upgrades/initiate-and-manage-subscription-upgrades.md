# Initiate and Manage Subscription Upgrades

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Initiate and Manage Subscription Upgrades |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (internal billing/ops staff) |
| **Business Outcome** | Enables ops staff to proactively upgrade accounting clients to a higher subscription tier by scheduling an auto-charge invoice 5 days out, and to cancel that pending charge before it processes if needed — capturing additional revenue when client usage exceeds plan limits while preserving operator control over timing. |
| **Entry Point / Surface** | Sleek Billings App > Upgrades Dashboard (`/upgrades` — eligible subscriptions view; `/upgrades-initiated` — in-flight upgrades view) |
| **Short Description** | Operators view a paginated dashboard of active accounting subscriptions filterable by upgrade eligibility or lifecycle status. For any eligible client, they select a higher-tier plan to create an upgrade invoice that auto-charges the saved payment method in 5 days (or sends a payment link if no card is saved). A pending charge can be cancelled at any point before it is processed. The dashboard also surfaces aggregate pending charge totals and supports full CSV export. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Subscription Config catalogue (`GET /subscription-config`); Invoice Service (`POST /invoices/auto-upgrade`); Payment auto-charge scheduler (backend job that fires 5 days after invoice creation); Accounting Expenses data (expense/transaction counts used to surface limit breaches); Sleek Admin App company-overview deep-links; Force Charge (non-production debug tool, `ForceChargeButton`) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend (inferred) |
| **DB - Collections** | Unknown (frontend only; backend collections not visible — API queries `customer-subscriptions` collection via `/customer-subscriptions/search/accounting-upgrades`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/countries does accounting upgrades cover (SG, HK, AU, UK, or subset)? Which backend service owns `POST /invoices/auto-upgrade` and what MongoDB collections are written? What scheduler/job triggers the actual charge after 5 days? What system sends the customer upgrade notification email? Is the `directDebitInprogress` status handled by a distinct code path not yet visible in the frontend? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Upgrades/UpgradesList.jsx` — Main dashboard component. Paginated table (30/page) of accounting subscriptions with two modes (`default` for eligible/upgradeable; `upgrades-initiated` for in-flight upgrades). Filter dropdown, debounced search, CSV batch export (200/page), total pending charges KPI.
- `src/pages/Upgrades/UpgradeAction.jsx` — Upgrade initiation dialog. Operator selects a higher-tier plan (same type & duration, higher price, must carry `paymentRequest` in `display` config). Shows top-up amount preview. Blocks upgrade if renewal due within 8 days. Submits to `createAutoUpgradeInvoice`. Branches to success ("Notification sent") or no-payment-method warning dialogs based on `autoChargeDate` presence in the response.
- `src/pages/Upgrades/UpgradeCancellation.jsx` — Cancel upgrade dialog. Only rendered when `upgradeStatus === pendingCharge`. Operator confirms cancellation; calls `cancelAutoUpgrade`. Customer is not charged; operator is advised to send cancellation confirmation manually.

### API calls (via `src/services/api.js`)

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/invoices/auto-upgrade` | Create upgrade invoice; returns `autoChargeDate` when saved payment method exists |
| `POST` | `/invoices/auto-upgrade/{subscriptionId}/cancel` | Cancel a pending upgrade charge |
| `GET` | `/customer-subscriptions/search/accounting-upgrades` | Paginated, filterable list of subscriptions (supports `filter`, `searchTerm`, `searchFilter`) |
| `GET` | `/customer-subscriptions/accounting-upgrades/analytics/pending-charge` | Aggregate total of all pending upgrade charges (KPI in upgrades-initiated mode) |
| `GET` | `/subscription-config` (via `getAllSubscriptionConfig`) | Full plan catalogue for tier-selection dropdown and top-up calculation |
| `POST` | `/v2/payment/auto-charge-invoice-upgrade` | Force-charge an upgrade invoice immediately (non-production only; `isForceCharge: true`) |

### Upgrade status lifecycle
`pendingCharge` → `autoUpgraded` | `manualUpgraded` | `failedCharge` | `cancelledCharge` | `cancelledVoided` | `noPaymentMethod` | `directDebitInprogress`

### Filter modes
**Default mode** (eligible/upgradeable):
- `all-active-and-upgradeable` — active subscriptions with no existing `upgradeStatus`, `subscriptionEndDate` set, renewal/delivery statuses in expected active ranges
- `expenses-limit-exceeded` — applies `searchFilter=exceeded-expense-limit`
- `transaction-limit-exceeded` — applies `searchFilter=exceeded-transaction-limit`

**Upgrades-initiated mode** (in-flight):
- `all-statuses` — any subscription with a non-null `upgradeStatus`
- `in-progress` — `upgradeStatus` in `[pendingCharge, failedCharge, cancelledCharge, noPaymentMethod, cancelledVoided]`
- `pending-charge` — `upgradeStatus = pendingCharge`
- `completed` — `subscriptionRenewalStatus` in `[upgraded, downgraded]`, `upgradeStatus` in `[autoUpgraded, manualUpgraded]`

### Key business logic
- **Top-up amount**: `targetService.price − currentService.price`; customer credits applied automatically by backend
- **Renewal conflict guard**: upgrade blocked (modal shown) if `nextRenewalDate` falls within 8 days to prevent overlapping charges
- **No payment method path**: invoice still created; `autoChargeDate` absent; customer receives a payment link via notification
- **URL persistence**: `?filter=<value>` param persists the selected filter across navigation
- **CSV export columns**: Company Name, Current Subscription Name, Total Expense, Total Revenue, Total Transactions, Service FY, Renewal Status, Subscription End Date, Renewal Due, Upgrade Status, Charge Date, Top-up Amount

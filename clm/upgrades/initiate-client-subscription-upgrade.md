# Initiate Client Subscription Upgrade

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Initiate Client Subscription Upgrade |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations (internal ops/billing staff) |
| **Business Outcome** | Enables ops staff to upgrade accounting clients to a higher subscription tier by scheduling a deferred top-up charge, capturing additional revenue when client usage exceeds current plan limits. |
| **Entry Point / Surface** | Sleek Billings App > Upgrades Dashboard > "Upgrade" button per client row |
| **Short Description** | Operator selects a higher-tier subscription for a client and submits. The system creates an upgrade invoice with an auto-charge date 5 days from today and sends the customer a notification. If no saved payment method exists, a payment link is sent instead. Any available customer credits are applied to the amount due. Upgrade is blocked if a renewal charge is already due within 8 days. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upgrade Cancellation flow (`UpgradeCancellation`), Force Charge (non-prod only, `ForceChargeButton`), Subscription Config list (`getAllSubscriptionConfig`), Customer notification system (triggered on invoice creation), Auto-renewal / scheduled charge job (backend) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-api (backend) |
| **DB - Collections** | Unknown (frontend only; backend collections not visible in this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns `POST /invoices/auto-upgrade` and which MongoDB collections are written? What job/scheduler triggers the actual charge after 5 days? What system sends the customer upgrade notification email? Are all markets (SG, HK, AU, UK) supported or is this accounting-only for specific markets? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Upgrades/UpgradesList.jsx` — Upgrades Dashboard: paginated table of accounting client subscriptions with filter by status (all-active-and-upgradeable, expenses-limit-exceeded, transaction-limit-exceeded, in-progress, pending-charge, completed) and CSV export. Embeds `UpgradeAction` per row.
- `src/pages/Upgrades/UpgradeAction.jsx` — Upgrade initiation dialog: tier selection, top-up amount preview, submission. Shows success ("Notification sent") or no-payment-method warning dialogs.

### API calls (via `src/services/api.js`)
| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/invoices/auto-upgrade` | Creates upgrade invoice; returns `autoChargeDate` if payment method exists |
| `GET` | `/customer-subscriptions/search/accounting-upgrades` | Paginated search of subscriptions eligible for or undergoing upgrade |
| `GET` | `/customer-subscriptions/accounting-upgrades/analytics/pending-charge` | Aggregate total of pending upgrade charges shown in dashboard header |
| `POST` | `/invoices/auto-upgrade/:subscriptionId/cancel` | Cancel a pending upgrade (used by UpgradeCancellation) |
| `POST` | `/v2/payment/auto-charge-invoice-upgrade` | Force-charge an upgrade invoice (non-production environments only) |

### Business logic
- **Tier filtering**: eligible upgrade targets must be of the same type and duration as the current service, carry a higher price, and appear in the `paymentRequest` display list.
- **Top-up amount**: `targetService.price − currentService.price`; credits applied automatically by backend.
- **Renewal conflict guard**: upgrade blocked (modal shown) if `nextRenewalDate` falls within 8 days to prevent overlapping charge attempts.
- **Upgrade status lifecycle**: `pendingCharge` → `autoUpgraded` | `manualUpgraded` | `failedCharge` | `cancelledCharge` | `noPaymentMethod` | `cancelledVoided` | `directDebitInprogress`
- **No payment method path**: invoice still created but `autoChargeDate` is absent; customer receives a payment link via notification.

### Constants
- `src/lib/constants.jsx:310` — `UPGRADE_STATUS` enum defining all possible upgrade lifecycle states.

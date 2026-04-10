# Manage Subscription Renewal

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Subscription Renewal |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Billing Operator) |
| **Business Outcome** | Operators control whether a subscription auto-renews, override the charge amount and next renewal date, cancel or reactivate renewals, and audit the full renewal history — ensuring subscriptions charge correctly and on time. |
| **Entry Point / Surface** | Sleek App > CLM > Subscriptions > Subscription Detail |
| **Short Description** | Operators can toggle auto-renewal on/off, set a custom renewal amount, update the next renewal date, cancel a renewal, and reactivate a cancelled subscription. The system automatically charges customers via Stripe or Direct Debit on the renewal date and dispatches reminder and failure emails. Renewal lineage (ancestors, siblings, descendants) is retrievable as auditable history. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Invoice creation (createRenewalInvoiceFromSubscriptionList), Payment V2 (Stripe / Direct Debit), Payment Method service, Payment Token service, Email task queue (charge reminders, failure alerts), Audit Log service, Service Delivery API, Subscription Scheduler (auto-toggle off for companies with no payment method) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | customersubscriptions, invoices, servicedeliveries, emaillogs, paymenttokens |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Markets: SG and HK confirmed from service clientType/market guards — AU and UK scope unclear. 2. `reactivate` endpoint restores `serviceDeliveryStatus` (not `subscriptionRenewalStatus`) — confirm whether this is intentional separation or an artefact of naming. 3. Master auth key bypass on cancel-renewal (`SLEEK_MASTER_AUTHORIZATION_KEY`) — is this used by another internal system or a scheduled job? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller endpoints (`customer-subscription.controller.ts`)

| Method | Route | Purpose |
|---|---|---|
| `PUT` | `/:id/toggle-renewal` | Enable or disable auto-renewal (`isAutoRenewalEnabled`) |
| `PUT` | `/:id/cancel-renewal` | Cancel renewal — sets status to `cancelled`, disables auto-renewal; supports master auth key for system-initiated cancellations |
| `PUT` | `/:id/reactivate` | Reactivate subscription — restores `serviceDeliveryStatus` to `active` or `delivered` |
| `PUT` | `/:id/custom-renewal-amount` | Override the renewal charge amount (`customRenewalAmount`) |
| `PUT` | `/:id/next-renewal-date` | Update next renewal date; auto-resets `subscriptionRenewalStatus` to `notDue` when the new date is far enough out |
| `GET` | `/:subscriptionId/renewal-history` | Return full renewal chain (ancestors → root → siblings → descendants via `existingSubscription` linkage) |
| `GET` | `/update-auto-renewal-toggle-off` | Scheduler-accessible endpoint to disable auto-renewal for companies with no payment method |

All endpoints are guarded by `@Auth()`.

### Service methods (`customer-subscription.service.ts`)

- `toggleRenewal` (L948) — writes `isAutoRenewalEnabled` + reason; emits audit log.
- `cancelRenewal` (L976) — writes `subscriptionRenewalStatus = cancelled`, `isAutoRenewalEnabled = false`, cancellation date/reason; system path bypasses user attribution via master auth header.
- `reactivateSubscription` (L1013) — sets `serviceDeliveryStatus` back to `active` (or `delivered` if all deliverables already done); emits audit log.
- `updateCustomRenewalAmount` (L814) — stores override amount + reason with operator email; emits audit log.
- `updateNextRenewalDate` (L884) — recalculates `subscriptionRenewalStatus` based on diff threshold (30 days yearly / 11 days monthly); also clears cancellation fields when moving away from cancelled state.
- `getRenewalHistory` (L1648) — delegates to `RenewalChainBuilder`, then populates service names via `serviceRepository`.

### Auto-renewal system (`subscription-auto-renewal.service.ts`)

- `getSubscriptionsForAutoRenewal` — queries for subscriptions matching `isAutoRenewalEnabled=true`, `nextRenewalDate` in window, and status in `[notDue, due, overdue]`.
- `triggerAutoRenewalEarlyReminders` — T-45 early reminder email for yearly subscriptions with a valid, non-expired card on file (`EmailTemplate.renewal_auto_on_early_reminder_grouped`).
- `triggerAutoRenewalChargeReminders` — Pre-charge reminder emails grouped per company; selects template based on payment method state: no method → `reminder_to_do_manual_renewal`, expired card → `renewal_auto_on_cardexpiry_reminder_grouped`, valid card → `renewal_auto_on_charge_reminder_grouped`.
- `triggerAutoRenewalCharge` — Creates renewal invoice → payment token → attempts charge through all payment methods (Stripe card, Direct Debit) in primary-first order. Supports 1st and 2nd charge attempts plus manual bypass (`bypassChargeAttempt`). On failure sends `renewal_auto_on_charge_failure_manualrequired` email and marks invoice/token as failed. Staggering logic (60 s sleep) prevents hammering Stripe for the same user across multiple companies.
- `payAutoRenewalInvoice` — Handles zero-amount invoices via `resolveZeroAmountPayment`; guards against $0 line items; tries each payment method and breaks on first success or DD-in-progress.

### Renewal chain (`renewal-chain.builder.ts`)

`RenewalChainBuilder.buildChain()` constructs the complete subscription lineage by traversing:
1. Ancestors — walks `existingSubscription` pointer upward
2. Siblings — subscriptions sharing the same `existingSubscription` parent
3. Descendants — BFS walk downward through children

Result is sorted by `subscriptionStartDate` descending, then `createdAt` descending. Deactivated subscriptions (`serviceDeliveryStatus = deactivated`) are excluded from the chain.

### MongoDB collections touched

| Collection | Access pattern |
|---|---|
| `customersubscriptions` | Read, update by ID; bulk `updateMany` on auto-renewal attempt timestamps |
| `invoices` | Create renewal invoice; update status/error fields on charge failure |
| `servicedeliveries` | Read delivery items to determine reactivation target status |
| `emaillogs` | Written via `EmailLogsRepository` to track sent reminders |
| `paymenttokens` | Created per auto-renewal attempt; marked FAILED on charge error |

### Audit trail

Every operator action (toggle, cancel, reactivate, amount update, date update) emits an `AuditLogsService.addAuditLog` entry tagged `['subscription', 'subscription-{id}']` with actor email and reason text.

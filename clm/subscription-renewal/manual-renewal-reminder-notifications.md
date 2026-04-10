# Manual Renewal Reminder Notifications

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manual Renewal Reminder Notifications |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Reduces subscription churn and missed renewals by sending a timed sequence of email nudges to customers who have auto-renewal disabled, prompting them to enable auto-renewal or renew manually before (and shortly after) their subscription lapses. |
| **Entry Point / Surface** | System cron jobs — four daily jobs at 6AM (UTC-offset configurable); manual trigger via `POST /subscription-renewal/trigger-reminders-if-auto-renewal-off` and `POST /subscription-renewal/trigger-reminders-to-threaten-offboarding` (admin use, `@Auth()` guard) |
| **Short Description** | Four scheduled email reminders target customers whose subscriptions have auto-renewal disabled: a "turn on auto-renewal" nudge (sent only when no payment method exists), two progressively-urgent "renew manually" reminders, and a post-lapse offboarding threat sent 30 days after the renewal date passes unpaid. Emails are batched per company and de-duplicated within each reminder's grouping window. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Payment method / credit card checks (`PaymentMethodService`, `CreditCardService`) — "turn on auto-renewal" reminder is suppressed when a card exists; email task queue (`TaskService` → async email worker); subscription config (service duration, `clientType` filtering excludes managed-service plans); `SWITCH_TO_SLEEK_BILLINGS` feature flag must be `enabled`; auto-renewal charge flow (downstream if customer re-enables auto-renewal or pays manually) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions` (eligibility query on `isAutoRenewalEnabled`, `nextRenewalDate`, `subscriptionRenewalStatus`; reminder-sent timestamps updated: `reminderToTurnOnAutoRenewalSentAt`, `reminderToDoManualRenewalSentAt`, `reminderToDoManualRenewal2ndTimeSentAt`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets (SG/HK/AU/UK) receive these reminders — is there any country-specific gating? What is the UTC offset configured in production? Is there alerting when the offboarding-threat batch finds zero eligible subscriptions? Does the manual-renewal email template vary by yearly vs. monthly plan? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/customer-subscription/controllers/subscription-renewal.controller.ts`

| Endpoint | Guard | Purpose |
|---|---|---|
| `POST /subscription-renewal/trigger-reminders-if-auto-renewal-off` | `@Auth()` | Manually triggers all three pre-renewal reminders (turn-on-auto-renewal + 1st and 2nd manual-renewal nudges), optionally scoped to one `companyId` |
| `POST /subscription-renewal/trigger-reminders-to-threaten-offboarding` | `@Auth()` | Manually triggers the post-lapse offboarding threat email |

### Scheduler
`src/customer-subscription/services/subscription-renewal-scheduler.service.ts`

Four cron methods, all running `EVERY_DAY_AT_6AM` (UTC offset from `UTC_OFFSET` env var), all gated by `SWITCH_TO_SLEEK_BILLINGS === 'enabled'`:

| Cron method | Service method called |
|---|---|
| `triggerRemindersToTurnOnAutoRenewal` | `subscriptionRenewalService.triggerRemindersToTurnOnAutoRenewal()` |
| `triggerRemindersToDoManualRenewal` | `subscriptionRenewalService.triggerRemindersToDoManualRenewal()` |
| `triggerRemindersToDoManualRenewal2ndTime` | `subscriptionRenewalService.triggerRemindersToDoManualRenewal(undefined, true)` |
| `triggerRemindersToThreatenOffboarding` | `subscriptionRenewalService.triggerRemindersToThreatenOffboarding()` |

### Service
`src/customer-subscription/services/subscription-renewal.service.ts`

**Eligibility query (`getSubscriptionsForReminders`)** — shared by all four reminder types:
- `isAutoRenewalEnabled: { $ne: true }` — only auto-renewal-OFF subscriptions
- `nextRenewalDate` within target date window (start/end computed from `daysBeforeRenewalDate` and `daysToCombineReminders`)
- `subscriptionRenewalStatus: { $in: [notDue, due, overdue] }`
- Deduplication: `lastReminderField` timestamp must be null or older than the grouping window
- Post-query filter: service must be `active`, `recurring`, correct duration tier (`>= 12 months` for yearly, `< 12` for monthly), and `clientType !== manageService`

**`triggerRemindersToTurnOnAutoRenewal()`**
- Window: yearly T-50 (combine 20 days), monthly T-15 (combine 10 days)
- **Skips companies that already have a payment method (Stripe card or legacy credit card)**
- Batches all subscriptions per company into one email task
- Template: `EmailTemplate.reminder_to_turn_on_auto_renewal`
- Tracks delivery via `reminderToTurnOnAutoRenewalSentAt`

**`triggerRemindersToDoManualRenewal(is2ndTime = false)`**
- 1st reminder window: yearly T-30 (combine 20 days), monthly T-11 (combine 10 days)
- 2nd reminder window: yearly T-5 (combine 20 days), monthly T-5 (combine 10 days)
- No payment-method check — sent regardless of card status
- Template: `EmailTemplate.reminder_to_do_manual_renewal` (carries `is2ndTime` flag in `emailData`)
- Tracks delivery via `reminderToDoManualRenewalSentAt` / `reminderToDoManualRenewal2ndTimeSentAt`

**`triggerRemindersToThreatenOffboarding()`**
- Window: subscriptions whose `nextRenewalDate` fell exactly 30 days ago (`REMINDER_TO_THREATEN_OFFBOARDING.daysAfterRenewalDate = 30`)
- No service-type or payment-method filtering — targets all unpaid statuses
- Template: `EmailTemplate.reminder_to_threaten_offboarding`

### Constants
`src/shared/consts/common.ts` (lines 95–159)

```
REMINDER_TO_TURN_ON_AUTO_RENEWAL.YEARLY  = { daysBeforeRenewalDate: 50, daysToCombineReminders: 20 }
REMINDER_TO_TURN_ON_AUTO_RENEWAL.MONTHLY = { daysBeforeRenewalDate: 15, daysToCombineReminders: 10 }

REMINDER_TO_DO_MANUAL_RENEWAL.YEARLY     = { daysBeforeRenewalDate: 30, daysToCombineReminders: 20 }
REMINDER_TO_DO_MANUAL_RENEWAL.MONTHLY    = { daysBeforeRenewalDate: 11, daysToCombineReminders: 10 }

REMINDER_TO_DO_MANUAL_RENEWAL_2ND_TIME.YEARLY  = { daysBeforeRenewalDate: 5, daysToCombineReminders: 20 }
REMINDER_TO_DO_MANUAL_RENEWAL_2ND_TIME.MONTHLY = { daysBeforeRenewalDate: 5, daysToCombineReminders: 10 }

REMINDER_TO_THREATEN_OFFBOARDING = { daysAfterRenewalDate: 30 }
```

### Schema
`src/customer-subscription/models/customer-subscription.schema.ts`

Relevant fields on `CustomerSubscription`:
- `isAutoRenewalEnabled: boolean` — eligibility gate
- `nextRenewalDate: Date` — renewal window anchor
- `subscriptionRenewalStatus: SubscriptionRenewalStatus` — `notDue | due | overdue` are eligible
- `reminderToTurnOnAutoRenewalSentAt: Date` — deduplication timestamp
- `reminderToDoManualRenewalSentAt: Date` — deduplication timestamp
- `reminderToDoManualRenewal2ndTimeSentAt: Date` — deduplication timestamp

Collection name: `customersubscriptions`

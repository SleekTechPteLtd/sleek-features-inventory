# Auto-renewal Reminder Notifications

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Auto-renewal Reminder Notifications |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Proactively notifies customers before their subscription auto-renews so they can resolve expired or missing payment methods before the charge runs, reducing failed payments and manual intervention. |
| **Entry Point / Surface** | System cron job — `POST /subscription-auto-renewal/trigger-reminders-auto-renewal-early-reminder` (T-45 early reminder) and `POST /subscription-auto-renewal/trigger-reminders-auto-renewal-charge-reminder` (pre-charge reminder); admin manual trigger available to BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin |
| **Short Description** | Two automated email reminders are sent ahead of renewal: a T-45 early notice (yearly plans with a valid card on file) and a pre-charge reminder (T-30 for yearly, T-11 for monthly). The pre-charge email selects from three templates depending on payment method status — valid card, expiring card, or no payment method — prompting the customer to act before the charge runs. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Auto-renewal charge execution (`triggerAutoRenewalCharge`); payment method management; email task queue (`TaskService` → async email worker); subscription config (service duration, clientType filtering to exclude managed-service plans); Stripe (via `PaymentServiceV2`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions` (eligibility query + reminder-sent timestamp updates: `chargeAttemptEarlyReminderSentAt`, `chargeAttemptReminderSentAt`), `emaillogs` (email audit log via `EmailLogsRepository`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | What cron schedules trigger the two reminder jobs in production? Are reminders sent across all markets (SG, HK, HK, AU, UK) or market-gated? Is there alerting when the reminder batch finds zero eligible subscriptions? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller
`src/customer-subscription/controllers/subscription-auto-renewal.controller.ts`

| Endpoint | Guard | Purpose |
|---|---|---|
| `POST /trigger-reminders-auto-renewal-early-reminder` | `@Auth()` | Triggers T-45 early reminder batch (optionally scoped to one company) |
| `POST /trigger-reminders-auto-renewal-charge-reminder` | `@Auth()` | Triggers pre-charge reminder batch |
| `POST /trigger-auto-renewal-charge` | `@Auth()` | Triggers 1st + 2nd charge attempt (not a reminder, included here for flow completeness) |
| `POST /trigger-manual-auto-renewal-charge` | `@Auth()` + `@GroupAuth(BillingSuperAdmin, BillingOperationsAdmin, SalesAdmin)` | Admin-initiated manual charge trigger |
| `GET /eligible/:companyId` | `@Auth()` | Returns subscriptions eligible for auto-renewal in the next 30 days |

### Service
`src/customer-subscription/services/subscription-auto-renewal.service.ts`

**`triggerAutoRenewalEarlyReminders()`**
- Queries subscriptions with `nextRenewalDate` in T-45 window (`REMINDER_AUTO_RENEWAL_EARLY.YEARLY.daysBeforeRenewalDate = 45`), yearly plans only
- Skips companies with no payment method or an expired card (early reminder is only meaningful when a charge is expected to succeed)
- Creates a `sendEmail` task with template `renewal_auto_on_early_reminder_grouped`
- Tracks delivery via `chargeAttemptEarlyReminderSentAt`

**`triggerAutoRenewalChargeReminders()`**
- Queries yearly subscriptions at T-30 (`REMINDER_AUTO_RENEWAL_CHARGE.YEARLY.daysBeforeRenewalDate = 30`, group window 20 days) and monthly subscriptions at T-11 (`REMINDER_AUTO_RENEWAL_CHARGE.MONTHLY.daysBeforeRenewalDate = 11`, group window 10 days)
- Checks payment method status per company to select email template:
  - No payment method → `reminder_to_do_manual_renewal` (`renewal_autooff_manual_reminder_grouped`)
  - Card-only and card expires before charge date → `renewal_auto_on_cardexpiry_reminder_grouped`
  - Valid payment method → `renewal_auto_on_charge_reminder_grouped`
- Tracks delivery via `chargeAttemptReminderSentAt`

**Eligibility filter (`getSubscriptionsForAutoRenewal`)** — common query shared by reminders and charge jobs:
- `isAutoRenewalEnabled: true`
- `subscriptionRenewalStatus: {$in: [notDue, due, overdue]}`
- `nextRenewalDate` within the target date window
- Excludes managed-service plans (`clientType !== ClientType.manageService`)
- Excludes inactive services (`service.status === ServiceStatus.active`)
- Deduplication guard: only processes subscriptions not already reminded within the grouping window

### Constants
`src/shared/consts/common.ts` (lines 128–155)
```
REMINDER_AUTO_RENEWAL_EARLY.YEARLY  = { daysBeforeRenewalDate: 45, daysToCombineReminders: 20 }
REMINDER_AUTO_RENEWAL_CHARGE.YEARLY = { daysBeforeRenewalDate: 30, daysToCombineReminders: 20 }
REMINDER_AUTO_RENEWAL_CHARGE.MONTHLY= { daysBeforeRenewalDate: 11, daysToCombineReminders: 10 }
```

### Email templates referenced
`src/email/enums/template.enum.ts`
- `renewal_auto_on_early_reminder_grouped` — T-45 early reminder
- `renewal_auto_on_charge_reminder_grouped` — pre-charge (valid card)
- `renewal_auto_on_cardexpiry_reminder_grouped` — pre-charge (expiring card)
- `renewal_autooff_manual_reminder_grouped` — no payment method, manual renewal needed
- `renewal_auto_on_charge_failure_manualrequired` — emitted after a failed charge attempt (downstream, not a pre-renewal reminder)

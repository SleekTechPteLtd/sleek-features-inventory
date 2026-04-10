# Send Offboarding Threat Notices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Send offboarding threat notices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Prompts overdue customers to renew before their subscription is cancelled, reducing churn by applying a time-bounded escalation notice |
| **Entry Point / Surface** | Automated — daily cron job at 06:00 (UTC offset configurable); also triggerable via `POST /subscription-renewal/trigger-reminders-to-threaten-offboarding` (authenticated) |
| **Short Description** | Each day, the platform identifies customer subscriptions whose `nextRenewalDate` fell exactly 30 days ago and whose renewal status is still `notDue`, `due`, or `overdue`. For each qualifying company, it enqueues a task to send the `reminder_to_threaten_offboarding` email template, warning that service discontinuation may occur within the remaining grace window (90-day overdue-to-cancelled threshold minus 30 days already elapsed). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: subscription auto-renewal pipeline (sets `subscriptionRenewalStatus`), payment-method and credit-card checks; Downstream: `TaskService.createTask` → email dispatch via `reminder_to_threaten_offboarding` template; Related: manual-renewal reminders (1st and 2nd time), auto-renewal reminder, subscription cancellation flow (`OVERDUE_TO_CANCELLED_DAYS = 90`) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `customersubscriptions` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which markets/countries receive this email? The query has no country filter. 2. Is `SWITCH_TO_SLEEK_BILLINGS` still a meaningful feature flag or always enabled in prod? 3. What happens after the 90-day `OVERDUE_TO_CANCELLED_DAYS` threshold — is there an automated cancellation job? 4. `daysAfterRenewalDate = 30` is hardcoded — is a second offboarding-threat notice planned? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Trigger surfaces
- **Scheduled**: `SubscriptionRenewalSchedulerService.triggerRemindersToThreatenOffboarding` — `@Cron(EVERY_DAY_AT_6AM)` with `utcOffset` from env. Gated on `SWITCH_TO_SLEEK_BILLINGS === 'enabled'`.
  - File: `customer-subscription/services/subscription-renewal-scheduler.service.ts:91–114`
- **Manual override**: `POST /subscription-renewal/trigger-reminders-to-threaten-offboarding` — `@Auth()` guard, accepts optional `{ companyId }` body to scope to a single company.
  - File: `customer-subscription/controllers/subscription-renewal.controller.ts:19–23`

### Core logic
`SubscriptionRenewalService.triggerRemindersToThreatenOffboarding` (service.ts:248–298):
1. Computes a date window: `now − 30 days` (start of day → end of day) using `REMINDER_TO_THREATEN_OFFBOARDING.daysAfterRenewalDate = 30`.
2. Queries `customersubscriptions` where `nextRenewalDate` falls in that window AND `subscriptionRenewalStatus ∈ {notDue, due, overdue}`.
3. Groups results by `companyId`.
4. For each company, calls `TaskService.createTask({ name: 'sendEmail', emailTemplateId: EmailTemplate.reminder_to_threaten_offboarding, emailData: { companyId, subscriptionIds } })`.

### Constants
- `REMINDER_TO_THREATEN_OFFBOARDING = { daysAfterRenewalDate: 30 }` — `shared/consts/common.ts:157–159`
- `OVERDUE_TO_CANCELLED_DAYS = 90` — `shared/consts/common.ts:161` (used in email template to compute remaining days before cancellation)

### Email template
- `EmailTemplate.reminder_to_threaten_offboarding` — referenced in `email/enums/template.enum.ts`
- Template file: `email/email-template/reminder_to_threaten_offboarding.template.ts` — uses `OVERDUE_TO_CANCELLED_DAYS − daysAfterRenewalDate` to show 60 days remaining in the email body.

### Schema / collection
- `CustomerSubscription` Mongoose schema → collection `customersubscriptions`
- Relevant fields: `nextRenewalDate`, `subscriptionRenewalStatus`, `companyId`, `isAutoRenewalEnabled`
- File: `customer-subscription/models/customer-subscription.schema.ts`

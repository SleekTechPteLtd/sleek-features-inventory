# Incomplete Onboarding Reminders

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Incomplete Onboarding Reminders |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Reduces drop-off after payment by nudging companies that have paid but not yet submitted their company details, increasing the proportion of clients who complete onboarding. |
| **Entry Point / Surface** | Automated — daily scheduled job at 8 AM (UTC offset configurable); also triggerable via `POST /company-reminder/incomplete-onboarding` (authenticated internal endpoint) |
| **Short Description** | Every day the system identifies companies in `paid_and_awaiting_company_detail` status and sends two time-gated reminder emails: a first reminder ≥ 5 days after payment, and a final reminder ≥ 15 days after payment. Each reminder is sent at most once per company (idempotency tracked on the invoice). |
| **Variants / Markets** | AU (enabled); SG, HK, UK are currently disabled via `enable_company_reminders_incomplete_onboarding` flag |
| **Dependencies / Related Flows** | CompanyService (company status lookup); InvoiceRepository (paid onboarding invoice lookup); TaskService → `sendEmail` task queue; Email templates `onboarding_completion_first_reminder` and `onboarding_completion_final_reminder` |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `invoices` (reads `status`, `invoiceOrigin`, `paidAt`, `userId`, `onboardingCompletionReminderSent`, `onboardingCompletionFinalReminderSent`); `companies` (reads company list by status, via CompanyService) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Why is this feature disabled for SG, HK, and UK — intentional market rollout or never prioritised? 2. The manual trigger endpoint (`POST /company-reminder/incomplete-onboarding`) uses `@Auth()` — is this called by an internal admin tool or only for ops/debugging? 3. Does `TaskService.createTask` with `sendEmail` ultimately route through sleek-mailer or another email provider? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Scheduler
`company-reminder/services/company-reminder-scheduler.service.ts`
- `@Cron(CronExpression.EVERY_DAY_AT_8AM, { utcOffset: process.env.UTC_OFFSET ?? 0 })`
- Resolves `CompanyReminderService` via `ModuleRef` and calls `processCompanyRemindersIncompleteOnboarding()`
- Guards against disabled platforms via `COUNTRY_SPECIFIC_CONFIG[platform].enable_company_reminders_incomplete_onboarding`

### Manual trigger endpoint
`company-reminder/controllers/company-reminder.controller.ts`
- `POST /company-reminder/incomplete-onboarding` — `@Auth()` guard
- Calls `companyReminderService.processCompanyRemindersIncompleteOnboarding()` directly

### Core logic
`company-reminder/services/company-reminder.service.ts`
- `processCompanyRemindersIncompleteOnboarding()` — entry point; skips if platform flag disabled
- `getCompaniesWithStatusPaidAndAwaitingCompanyDetail()` — calls `CompanyService.getCompanyListByStatus('paid_and_awaiting_company_detail')`
- `findOnboardingInvoice(companyId)` — prefers `invoiceOrigin: betaOnboarding` + `status: paid`; falls back to oldest paid invoice (`sort: { paidAt: 1 }`)
- `shouldSendFirstReminder()` — skips if `onboardingCompletionReminderSent` already set; sends if ≥ 5 days since `paidAt`
- `shouldSendFinalReminder()` — skips if `onboardingCompletionFinalReminderSent` already set; sends if ≥ 15 days since `paidAt`
- `sendFirstReminder()` / `sendFinalReminder()` — calls `TaskService.createTask({ name: 'sendEmail', data: { emailTemplateId: EmailTemplate.onboarding_completion_first_reminder | onboarding_completion_final_reminder, ... } })`

### Market flag (common.ts)
```
COUNTRY_SPECIFIC_CONFIG.au.enable_company_reminders_incomplete_onboarding = true
COUNTRY_SPECIFIC_CONFIG.sg/hk/uk.enable_company_reminders_incomplete_onboarding = false
```

### Invoice schema fields used
`invoice/models/invoice.schema.ts` lines 252–255:
- `onboardingCompletionReminderSent?: Date` — set after first reminder sent
- `onboardingCompletionFinalReminderSent?: Date` — set after final reminder sent

# Expense claim period cutover

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Expense claim period cutover |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System; Company Admin (email recipient when notifications enabled) |
| **Business Outcome** | When a company’s expense-claim period ends, open claim reports for that window become ready for admin review so finance can close the period without manual status changes. |
| **Entry Point / Surface** | Coding engine: `@Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)` in `ClaimReportService.handleCron`; `POST /claim-report/ecCutOver` (same logic, no `AuthGuard` on controller—treat as internal/scheduled surface). Consumer UIs not defined in this repo. |
| **Short Description** | Each day after midnight, the service selects companies whose cut-off day matched “yesterday” (or month-end for last-day-of-month settings), finds claim reports whose period ended on that date, sets status from `new` to `toreview`, publishes an update event, and optionally emails the company owner (from SleekBack) using the review-expense-claims template when `IS_EC_ADMIN_NOTIFICATION_ENABLED` is true. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `Company.ec_cut_off_day` on MongoDB `companies`; `ClaimReport` documents on `claimreports`; SleekBack `getCompanyUsersFromSleekBack` / `getReceiptUsersFromSleekBack` for admin and display names; `EventUtils.publishEvent` with `ECReportEventType.UPDATED`; `MailerService.sendEmail` + `EMAIL_TEMPLATES.EXPENSE_CLAIM.REVIEW_EXPENSE_CLAIMS_REPORTS`; config `SLEEK_WEBSITE_BASE_URL`. Downstream: admin review and publish flows in the same module. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | claimreports, companies |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `processCompanyToEcCutOver` uses `findOneAndUpdate` with filter `{ claimReportId: report._id }` while the Mongoose schema exposes `_id`—confirm whether the stored field name matches or updates apply as intended. `POST /claim-report/ecCutOver` is unauthenticated in the controller; confirm intended exposure (internal gateway only vs oversight). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`claim-report.service.ts`**
  - `ecCutOver`: Computes `yesterday` and `yesterday_DD`. If yesterday was the last calendar day of the month, loads companies with `ec_cut_off_day` null, undefined, or `'0'` (last day of month). Otherwise loads companies where `ec_cut_off_day === yesterday_DD`. Iterates `processCompanyToEcCutOver(company, yesterday)`.
  - `processCompanyToEcCutOver`: Resolves company admin via `getCompanyAdminUserFromSleekBack` (owner user). Queries reports with `company_id`, `end_date` in `[yesterday, today)`. For each report in `ClaimReportStatus.NEW`, updates to `TOREVIEW` and publishes `ECReportEventType.UPDATED` with `EventCaller.CLAIM_REPORT_SERVICE.processCompanyToEcCutOver`. If `IS_EC_ADMIN_NOTIFICATION_ENABLED === 'true'`, calls `sendReviewExpenseClaimsReportEmail(adminUserDetails, yesterday, SLEEK_WEBSITE_BASE_URL)` (recipient is the admin user object; template variables include `month_year`, `month_name`, `sleek_website_base_url`).
  - `sendReviewExpenseClaimsReportEmail`: Uses `EMAIL_TEMPLATES.EXPENSE_CLAIM.REVIEW_EXPENSE_CLAIMS_REPORTS`.
  - `handleCron`: `@Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)` → `ecCutOver()`.
- **`claim-report.controller.ts`:** `POST claim-report/ecCutOver` → `service.ecCutOver()` (no guard).
- **`claim-report.enum.ts`:** `ClaimReportStatus.NEW`, `TOREVIEW`.
- **`company.schema.ts`:** `ec_cut_off_day` (and related fields) drive which companies run on a given day.
- **`claim-report.schema.ts`:** `status`, `company_id`, `claim_user`, `end_date` on `ClaimReport`.

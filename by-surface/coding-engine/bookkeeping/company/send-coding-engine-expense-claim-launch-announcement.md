# Send Coding Engine expense claim launch announcement

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Send Coding Engine expense claim launch announcement |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (manual or scripted trigger of the API); end clients receive the email but do not initiate this flow |
| **Business Outcome** | Active receipt-system clients who have not yet been notified are informed once that expense claim reporting is available (Coding Engine), with links to bookkeeping and support. |
| **Entry Point / Surface** | Coding Engine HTTP API: `POST /company/send-email/ec-launch` (not an end-user Sleek App screen). No `AuthGuard` on this handler in code—actual exposure may depend on gateway or network policy. |
| **Short Description** | Finds companies with `receipt_system_status: 'active'` and `welcome_email_sent` null or false. For each, resolves recipients from accounting questionnaire emails (finance and payroll), plus the company owner from Sleek Back, deduplicates, and sends the transactional template `ec_report_launch_notification` with CTA and enquiry URLs built from `SLEEK_WEBSITE_BASE_URL`. Successfully processed companies get `welcome_email_sent: true` so the announcement is not sent again. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** `SleekBackService.getCompanyUsersFromSleekBack` (owner `is_owner` for admin email). **Transactional email:** `MailerService.sendEmail` with `EMAIL_TEMPLATES.EXPENSE_CLAIM.EC_REPORT_LAUNCH_EMAIL`. **Config:** `SLEEK_WEBSITE_BASE_URL` for `button_url` and `enquiry_url`. **Related:** Company sync and receipt-system status from platform (`synchronize-company-master-data-from-sleekback`); expense claim product flows under claim-report. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (connection `sleek_acct_coding_engine`) — read eligibility; `updateMany` sets `welcome_email_sent` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `welcome_email_sent` is reserved solely for this campaign or shared with other “welcome” emails; production auth story for `POST /company/send-email/ec-launch` (no guard in controller). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/company/company.controller.ts`: `POST company/send-email/ec-launch` → `companyService.sendEmailForEcLaunch()`; `@ApiOperation` summary “To send email once only to clients who are on Coding Engine”.
- **Service** — `src/company/company.service.ts` `sendEmailForEcLaunch`: `find` on `companyModel` with `receipt_system_status: 'active'` and `welcome_email_sent: { $in: [null, false] }`; builds `variables` from `SLEEK_WEBSITE_BASE_URL` (`/bookkeeping`, `/customer/support/`); per company aggregates `customer_finance_email`, `customer_payroll_email` from `accounting_settings`, plus `getCompanyAdminUserFromSleekBack` → `adminUser.email`; `mailerService.sendEmail(EMAIL_TEMPLATES.EXPENSE_CLAIM.EC_REPORT_LAUNCH_EMAIL, variables, uniqueRecipients)`; `updateMany` with `$set: { welcome_email_sent: true }` for successfully processed `company_id`s; per-company errors logged without failing the whole batch.
- **Email template id** — `src/common/constants/email-templates.ts`: `EXPENSE_CLAIM.EC_REPORT_LAUNCH_EMAIL` → `'ec_report_launch_notification'`.
- **Schema** — `src/company/models/company.schema.ts`: `welcome_email_sent` boolean; `receipt_system_status`; `accounting_settings` (customer finance/payroll emails).
- **Sleek Back** — `getCompanyAdminUserFromSleekBack` uses `sleekBackService.getCompanyUsersFromSleekBack` and selects `is_owner` user.

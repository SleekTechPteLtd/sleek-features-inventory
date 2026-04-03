# Sleek bookkeeping digest emails

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sleek bookkeeping digest emails |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Company admins receive timely reminders about missing bank statements and high-impact missing supporting documents so clients can close documentation gaps before compliance deadlines. |
| **Entry Point / Surface** | Scheduled / operations batch: Nest Commander CLI `send-digest-emails.command` (optional `--dryRun`); not an in-app screen. |
| **Short Description** | Streams active companies, filters by CMS feature flags and Sleek Back company status, builds per-FY tasks from the bank-statement engine and ledger transaction rules, splits tasks into due vs overdue, applies FY-based email frequency and snooze rules, then emails the company admin (and optional receipt CC) via the transactional template. Persists each send in `sleek_digests` and writes an auditor log. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | CMS feature config (`getSupportingDocumentsConfig`, `getSleekDigestConfig`); Sleek Back (company status, admin user, Accountant in Charge for sender name, resource users); bank-statement engine (`getMissingBankStatements`); ledger transactions (missing-docs thresholds); mailer (`accounting_bsm_regular_sleek_digest_email`); Sleek Auditor; company subscriptions/FY resolution and `sleek_digest_settings` (snooze, per-FY snooze). |
| **Service / Repository** | acct-coding-engine (coding-engine DB connection) |
| **DB - Collections** | `companies` (including embedded `sleek_digest_settings`), `ledger_transactions`, `sleek_digests` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `handleMissingDocsForHighValueTrx` is fully implemented in `SleekDigestService` but is not invoked by `getMissingDataForFYEs`; the live digest batch only combines missing bank statements and **high-volume** missing supporting documents. Confirm whether high-value is intentionally out of scope for this command or pending integration. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **CLI entry**: `SleekDigestCommand` (`send-digest-emails.command`) calls `SleekDigestService.sendDigestEmails(isDryRun)`; `--dryRun` skips email, `sleek_digests` inserts, and auditor logs (`src/sleek-digest/sleek-digest.command.ts`).
- **Batch orchestration**: `sendDigestEmails` loads CMS configs once, iterates companies in batches (`BATCH_SIZE` 1000 from `SLEEK_DIGEST_CONSTANTS`), filters eligibility via `checkEligibilityForBatch` (supporting-docs + sleek-digest flags, non-churn/non-archived from Sleek Back), then `processCompanyForDigestEmail` per eligible company (`src/sleek-digest/sleek-digest.service.ts`).
- **Task sources**: `getMissingDataForFYEs` runs in parallel `handleMissingBankStatements` (BankStatementEngineService) and `handleMissingDocsForHighVolumeTrx` (ledger queries + thresholds: `HIGH_VOLUME_TRANSACTION_COUNT`, `MISSING_DOCS_COUNT`, `MISSING_DOCS_PERCENTAGE` from `src/sleek-digest/constants/sleek-digest.constants.ts`).
- **Due / overdue**: `categorizeTasks` / `isPastFyeEndDate` — overdue when current date is after FY end (`src/sleek-digest/sleek-digest.service.ts`).
- **Schedule**: `getEmailDigestSchedule` returns 14 or 30 days (or 0) from FY start, filing status, and current date; `shouldSendEmailDigest` enforces resume-day override, snooze, first-send, and interval vs last `sleek_digests` record (`DigestType.REGULAR`).
- **Email**: `MailerService.sendEmail` with `EMAIL_CONFIG.TEMPLATE_ID`, `REMINDER_CONFIGS` subject lines by months since FY end (HK uses default subject only per code), HK translations via `TRANSLATIONS` / `TRANSLATION_PATTERNS`, deep links from `SLEEK_DIGEST_CONSTANTS.DEEP_LINKS` (`src/sleek-digest/constants/sleek-digest.constants.ts`).
- **Persistence**: `digestModel.create` on `sleek_digests` collection (`src/sleek-digest/models/digest.schema.ts`); company scan uses `receipt_system_status: ACTIVE` on companies.
- **Wiring**: `SleekDigestModule` registers command, service, Digest/LedgerTransaction/Company models on `DBConnectionName.CODING_ENGINE` (`src/sleek-digest/sleek-digest.module.ts`).

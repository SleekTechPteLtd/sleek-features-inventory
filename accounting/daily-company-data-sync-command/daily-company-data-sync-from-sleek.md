# Daily company data sync from Sleek (scheduled job)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Daily company data sync from Sleek |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | On a fixed schedule, the coding engine refreshes its stored company profiles, subscriptions, resource users, questionnaire-derived accounting settings, and receipt system status from Sleek platform and Sleek Back so downstream accounting and document flows stay aligned with the live platform. |
| **Entry Point / Surface** | Kubernetes CronJob (per environment/region) runs `npx nest start --entryFile app.command -- daily-company-data-sync.command` (see `acct-coding-engine/kubernetes/**/Cronjob.yaml`). Not a Sleek App screen. |
| **Short Description** | A NestJS CLI command (`nest-commander`) invokes `CompanyService.dailySyncAllReceiptSystemActivatedCompaniesFromSleekback()`, which batches through `syncCompanies` with delta sync and page size 300, reusing the same platform and Sleek Back integration as manual/API-triggered sync. The process exits after completion. |
| **Variants / Markets** | SG, HK, UK, AU (cron manifests exist per region in `kubernetes/`; behaviour is deployment-configured) |
| **Dependencies / Related Flows** | **Implementation:** `CompanyService.syncCompanies`, `updateOrCreateCompany`, `updateOrCreateCompanySetting` — same pipeline as HTTP-triggered sync; see `accounting/company/synchronize-company-master-data-from-sleekback.md`. **Upstream:** `PlatformService.company.findAllCompanies` (with accounting questionnaire), `SleekBackService` (resource users, subscriptions). **Related:** Kafka-driven `companyDataSync` / company-listener updates are a separate path. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (MongoDB connection `CODING_ENGINE` / `sleek_acct_coding_engine` per deployment); `companysettings` (collection name `companysettings`, connection `SLEEK_RECEIPTS`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Cron schedule and owning team are in Kubernetes YAML, not in the command source; exact `findAllCompanies` delta behaviour when only `limit`/`sync_type` are set should match platform contract. Method name references “receipt system activated” but the daily DTO does not set `receipt_system_status` in code—confirm with platform whether listing is implicitly filtered. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **CLI command** — `acct-coding-engine/src/commands/daily-company-data-sync/daily-company-data-sync.command.ts`: `@Command` name `daily-company-data-sync.command`; `run()` logs start, awaits `companyService.dailySyncAllReceiptSystemActivatedCompaniesFromSleekback()`, logs completion, `process.exit(0)`.
- **Daily batch entry** — `acct-coding-engine/src/company/company.service.ts` `dailySyncAllReceiptSystemActivatedCompaniesFromSleekback`: builds `CompanySyncDto` with `limit: 300`, `sync_type: CompanySyncType.DELTA`, calls `syncCompanies(companySyncDto)`.
- **Shared sync pipeline** — `syncCompanies`: paginates with `platformService.company.findAllCompanies({ skip, limit, include_accounting_questionnaire: true, ...delta fields })`; per company: `sleekBackService.getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack`, `mapResourseUsers`, `getActiveSubscriptions`; upserts via `updateOrCreateCompany` and `updateOrCreateCompanySetting`.
- **Registration** — `acct-coding-engine/src/commands/command.module.ts` registers `DailyCompanyDataSyncCommand`.
- **Scheduling** — `acct-coding-engine/kubernetes/*/Cronjob.yaml` (e.g. `ce-daily-company-data-sync-cronjob` in SG/HK) runs the command; some environments disable Kafka producer/consumer for the job.

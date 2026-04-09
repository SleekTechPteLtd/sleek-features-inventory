# Synchronize company master data from Sleek Back

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Synchronize company master data from Sleek Back |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (batch and scheduled jobs); Operations / integration callers for `POST /company/sync` and related endpoints (no auth guard on the sync routes in code) |
| **Business Outcome** | The coding engine’s MongoDB view of each client company stays aligned with platform company data and Sleek Back—subscriptions, resource users, accounting questionnaire settings, receipt system status, and ledger metadata—so downstream bookkeeping, document, and client flows run on current company context. |
| **Entry Point / Surface** | Coding Engine HTTP API: `POST /company/sync` (body `CompanySyncDto`), `POST /company/sync-receipt-system-activated-companies` (fires `dailySyncAllReceiptSystemActivatedCompaniesFromSleekback`). Not an end-user Sleek App screen. |
| **Short Description** | Paginated batches pull companies from the Sleek Platform SDK (`company.findAllCompanies` with accounting questionnaire). For each company, the service loads accounting resource users with roles from Sleek Back, active subscription service codes from Sleek Back, and maps questionnaire fields into `accounting_settings`, `receipt_system_status`, `ledger_type`, and related fields. Upserts the `companies` document and a minimal `companysettings` row (company reference + optional `whitelisted_date`). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** `PlatformService` (sleek-platform) for company listing; `SleekBackService` (`/internal/companies/:id/accounting-resource-users-with-role-info-by-company-id`, `/internal/companies/:id/subscriptions`). **Related:** Kafka-driven partial updates (`company-listener` / `companyDataSync`)—separate path; see `accounting/company-listener/sync-company-records-from-platform-events.md`. **Downstream:** Any feature reading `companies` or `companysettings` in coding engine / sleek receipts DBs. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (connection `sleek_acct_coding_engine`); `companysettings` (connection `sleek_receipts`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Company **listing** uses Platform SDK, not `SleekBackService.getAllCompanies`; confirm product naming (“Sleek Back” vs “platform”) for stakeholder docs. Exact markets and scheduling owner for `sync-receipt-system-activated-companies` (cron caller) not in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/company/company.controller.ts`: `POST company/sync` → `companyService.syncCompanies(options)`; `@ApiOperation` “To sync Companies from SleekBack to CodingEngine”. `POST company/sync-receipt-system-activated-companies` → `dailySyncAllReceiptSystemActivatedCompaniesFromSleekback()` (delta sync with limit 300 per invocation). `CompanySyncDto` / `@ApiBody` on sync.
- **Sync pipeline** — `src/company/company.service.ts` `syncCompanies`: loops with `skip`/`limit`/`delay`; loads pages via `this.platformService.company.findAllCompanies({ skip, limit, include_accounting_questionnaire: true, ...delta filters })`; for each company calls `sleekBackService.getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack`, `mapResourseUsers`, `getActiveSubscriptions` (filters `SubscriptionsStatus.ACTIVE`, maps `service`); builds `companyToBeUpdated` with `uen`, `company_name`, `company_id`, `accounting_tools`, `financial_year`, `ledger_type`, `last_synced`, `accounting_settings` (from `accounting_questionnaire`), `resource_users`, `active_subscriptions`, `banks`, `receipt_system_status`, optional `whitelisted_date`, `incorporation_date`; `updateOrCreateCompany` (upsert on `company_id`); `updateOrCreateCompanySetting` with `{ company: _id, whitelisted_date? }`.
- **Sleek Back HTTP** — `src/sleek-back/sleek-back.service.ts`: `getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack` → `GET .../internal/companies/:companyId/accounting-resource-users-with-role-info-by-company-id`; `getCompanySubscriptionsFromSleekBack` → `GET .../internal/companies/:companyId/subscriptions` (returns `companySubscriptions`). Basic auth via `SLEEK_SERVICE_CLIENT_ID` / `SLEEK_SERVICE_CLIENT_SECRET`.
- **Persistence** — `src/company/models/company.schema.ts` `Company` (`@InjectModel(Company.name, DBConnectionName.CODING_ENGINE)`); `src/company/models/company-setting.schema.ts` `@Schema({ collection: 'companysettings', ... })` on `SLEEK_RECEIPTS` connection.
- **Daily batch** — `dailySyncAllReceiptSystemActivatedCompaniesFromSleekback` sets `CompanySyncDto` with `sync_type: DELTA` and `limit: 300`, then `syncCompanies`.

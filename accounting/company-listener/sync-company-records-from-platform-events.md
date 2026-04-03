# Sync company records from platform events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync company records from platform events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | The coding engine’s view of each client company—profile fields, fiscal year end, assigned resource users, and active subscription services—stays consistent with Sleek Platform and related services when upstream data changes, so bookkeeping and accounting flows operate on current company context. |
| **Entry Point / Surface** | Server integration: Kafka consumers on `CompanyUpdateListener` (`company-listener` routes exist for manual/test injection: `POST company-listener/process-message`, `process-fye-message`, `process-subscription-created-message`, `process-subscription-updated-message`). Not an end-user app screen. |
| **Short Description** | Kafka events (company data to CE, FYE change, subscription created/updated) are handled by a listener that delegates to `CompanyService.companyDataSync`. The service merges partial updates into MongoDB and, when needed, reloads resource users and active subscription service codes from Sleek Back instead of trusting stale payload fields alone. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Kafka (`@SubscribeEvent` / `CompanyDataToCEUpdateReceived`, `sleek-fye.fye_had_changed`, subscription event classes); `SleekBackService` (`getAccountingCompanyResourceUsersWithRoleInfoFromSleekBack`, `getCompanySubscriptionsFromSleekBack`); bulk/platform reconciliation via `syncCompanies` / `PlatformService` (separate scheduled or batch path). Company row must already exist—`companyDataSync` errors if none. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | companies (connection `sleek_acct_coding_engine`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Initial company creation for net-new tenants is not in this listener path—confirm which job or API first inserts `companies` before event sync applies. Whether `CompanyDataToCEUpdateReceived` payload always includes `resource_users` when team membership changes is inferred from conditional refresh logic only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Listener** — `src/kafka/listeners/company-update.listener.ts`: Nest `@Controller('company-listener')`; `@SubscribeEvent(CompanyDataToCEUpdateReceived.name)` → `companyService.companyDataSync(message, false)`; `@SubscribeEvent('sleek-fye.fye_had_changed')` builds payload with `company_id` and `financial_year` from `message.data.fye.next_fy_end_date` then `companyDataSync(..., false)`; `@SubscribeEvent` on subscription created/updated events → `companyDataSync({ company_id }, true)`. Test-only `POST` handlers mirror the same calls.
- **Sync core** — `src/company/company.service.ts` `companyDataSync(payload, isUpdateSubscriptions)`: loads existing company by `company_id`; if `resource_users` present in payload, replaces with `getCompanyResourceUsers` (Sleek Back); if `isUpdateSubscriptions`, sets `active_subscriptions` from `getActiveSubscriptions` (filters `SubscriptionsStatus.ACTIVE`, maps to `service`); if `accounting_tools` present, sets `ledger_type` via `getCompanyLedger`; `findOneAndUpdate` with `$set` on filter `{ company_id }`.
- **Related bulk path** — same service `syncCompanies` / `updateOrCreateCompany` pulls full company rows from `PlatformService.company.findAllCompanies` and Sleek Back—broader than the event listener but same `companies` model and resource/subscription enrichment patterns.
- **Schema** — `src/company/models/company.schema.ts`: `Company` model (default collection `companies`) includes `resource_users`, `financial_year`, `active_subscriptions`, `accounting_tools`, etc.

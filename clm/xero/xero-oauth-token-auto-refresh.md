# Automated Xero OAuth Token Renewal

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Automated Xero OAuth Token Renewal |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Keeps Xero API access tokens fresh on a daily schedule so that invoicing, contact sync, and payment recording never fail due to expired credentials |
| **Entry Point / Surface** | Internal cron job — no UI surface; runs daily at 01:00 AM server time |
| **Short Description** | A NestJS scheduler enqueues a Bull `refreshToken` job every day at 1AM. The job reads each configured Xero token from MongoDB, checks whether it is within the expiry buffer window (default 5 min), and if so calls the Xero OAuth refresh endpoint with up to 3 retries. The refreshed token is re-encrypted and persisted back to the database. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Feature-flag gated via `AppFeatureService` (`billingService.xeroSetting.autoRefreshToken`); requires `SWITCH_TO_SLEEK_BILLINGS=enabled` env flag; upstream of all Xero API calls (invoices, credit notes, contacts, bank transactions, items) |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xero_settings` (SleekXeroDB — stores encrypted token sets, clientId, clientSecret, isActive flag) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which specific token IDs are listed in the `autoRefreshToken.value` array and how many Xero tenants are active? Is the `SWITCH_TO_SLEEK_BILLINGS` flag permanently enabled in prod or still being migrated? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

| File | Key symbols |
|---|---|
| `src/xero/xero-processor.scheduler.ts` | `XeroProcessorScheduler.triggerXeroArchiving()` — `@Cron(EVERY_DAY_AT_1AM)`; checks `SWITCH_TO_SLEEK_BILLINGS` env var; enqueues `refreshToken` job via `QueueService` |
| `src/xero/xero-processor.processor.ts` | `XeroProcessorProcessor.refreshToken()` — `@Process('refreshToken')` on `QUEUES.PAYMENT` Bull queue; reads feature flag `billingService.xeroSetting.autoRefreshToken`; iterates over token IDs and calls `xeroService.init({ tokenId })` + `xeroService.ensureTokenIsRefresh()` |
| `src/xero/services/xero.service.ts` | `ensureTokenIsRefresh()` — reads encrypted token from `XeroSettingRepository`, calls `xeroClient.refreshWithRefreshToken()` with 3-attempt retry loop and exponential back-off (200/500/1200 ms); calls `persistToken()` to re-encrypt and write refreshed `TokenSet` back to DB. `shouldRefreshToken()` computes expiry using `XERO_TOKEN_REFRESH_BUFFER_SECONDS` (default 300 s). |
| `src/xero/repositories/xero-setting.repository.ts` | `XeroSettingRepository extends BaseRepository<XeroSetting>` — backed by `SleekXeroDB` MongoDB connection |
| `src/xero/models/xero-setting.schema.ts` | `XeroSetting` schema — fields: `_id` (token key), `value` (encrypted token JSON), `clientId`, `clientSecret`, `isActive` |

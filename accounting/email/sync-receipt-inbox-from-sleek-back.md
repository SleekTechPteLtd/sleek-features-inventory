# Sync receipt inbox from Sleek Back

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync receipt inbox from Sleek Back |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | Inbound receipt email addresses and activation status in the gateway match Sleek Back so messages route to the correct receipt user and behaviour stays consistent with the accounting system. |
| **Entry Point / Surface** | Sleek Receipt Gateway — HTTP `POST /email/sync` (single-record upsert), `GET /email?email_in_address=…` (lookup for routing), `POST /email/manual-sync` (batch reload from Sleek Back). Scheduled job: `EmailService.handleSync` (daily in production, every 15 minutes otherwise) runs a delta sync per market. `POST /email/reinitialize-email-gateway` reloads the email gateway module. Not a standard end-user app screen; operators or platform jobs trigger manual sync. |
| **Short Description** | Pulls receipt users from Sleek Back’s internal API (`/internal/receipt-users`) with pagination, optional date range (delta) or company filter, and upserts each row into gateway MongoDB by `receipt_user_id` and tenant with `email_in_address` and status from `status_v2`. Skips users without an inbound address. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Upstream: Sleek Back per-tenant API base URLs and service client credentials (`SLEEK_*_SERVICE_CLIENT_SECRET`, `SLEEK_SERVICE_CLIENT_ID`). Downstream: receipt-by-email ingestion and routing that resolves `email_in_address` via `findEmailByEmailInAddress`. Related: `POST /email/sync` for pushing a single email record without calling Sleek Back. |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `emails` (Mongoose model `Email`; connection `SLEEK_RECEIPT_GATEWAY`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `EmailController` routes are protected by guards, API gateway, or internal network only is not visible in the reviewed files. Exact MongoDB collection name if overridden from Mongoose defaults was not confirmed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/modules/email/email.controller.ts`**: `@Controller('email')` — `POST sync` → `EmailService.sync`; `GET` with query `email_in_address` → `findEmailByEmailInAddress`; `POST manual-sync` → `syncReceiptUsers`; `POST reinitialize-email-gateway` → `EmailGateway.onModuleInit()`.
- **`src/modules/email/email.service.ts`**: `updateOrCreateEmailData` uses `findOneAndUpdate` on `{ receipt_user_id, tenant }` with `$set` and `upsert: true`. `sync` delegates to that upsert. `syncReceiptUsers` loops with `skip`/`limit`, calls `sleekBackService.getReceiptUsersFromSleekBack`, maps `email_in_address`, `status_v2` → `status`, `tenant`, and upserts; empty `email_in_address` skipped. `handleSync` `@Cron`: production `0 0 * * *`, else `*/15 * * * *`; builds delta options (`EmailSyncType.DELTA`, yesterday–today) and iterates `CountriesToSync` for `syncReceiptUsers`.
- **`src/modules/sleek-back/sleek-back.service.ts`**: `getReceiptUsersFromSleekBack` — `GET {baseUrl}/internal/receipt-users?…` with HTTP Basic (`SLEEK_SERVICE_CLIENT_ID` / tenant-specific client secret); `baseUrl` from `SLEEK_BACK_API_BASE_URL_*` per `Countries`; returns `response.data.data` or `[]` on error.
- **`src/modules/email/models/email.schema.ts`**: Fields `receipt_user_id`, `email_in_address` (unique index), `tenant`, `status` (enum `EmailStatus`).
- **`src/common/enum/countries.enum.ts`**: `CountriesToSync` lists SG, HK, UK, AU.

# Manage receipt email inbox sync and gateway

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage receipt email inbox sync and gateway |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Receipt-user inbound email addresses and activation status stay aligned with the bookkeeping system, and the Gmail IMAP gateway stays authenticated and running so inbound receipt mail can be matched, deduplicated, and forwarded into the receipt pipeline. |
| **Entry Point / Surface** | **HTTP API (sleek-receipt-gateway):** `POST /email/sync` (upsert single email record), `GET /email?email_in_address=…` (lookup by inbound address), `POST /email/manual-sync` (batch pull from Sleek Back), `POST /email/reinitialize-email-gateway` (re-run gateway init). **Scheduled:** cron in `EmailService.handleSync` (production daily at midnight; non-production every 15 minutes) runs delta sync per tenant for yesterday–today. |
| **Short Description** | Operators or automation sync `receipt_user_id`, `email_in_address`, and status from Sleek Back’s internal receipt-users API into MongoDB, support full or delta paging with optional company filter, and can restart IMAP after Google OAuth by reinitializing `EmailGateway`. The gateway verifies/refreshes Google tokens, connects to `imap.gmail.com` with XOAUTH2, applies configured search filters, and on each message acquires a Redis lock by Message-ID before parsing and forwarding to receipts. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | **Upstream:** Sleek Back `GET /internal/receipt-users` (per-tenant base URL and service client secret). **Same service:** `GoogleService` (OAuth credentials for gateway client id), `EmailForwarderService` → receipt processing, `IncomingEmailReader`, `CacheService` / `CacheUtility` for cross-instance idempotency. **Related:** Google Gmail OAuth and IMAP (`connect-google-gmail-for-receipt-ingestion` in inventory is the parallel narrative for the legacy sleek-receipts app; this gateway is NestJS `EmailGateway`). |
| **Service / Repository** | sleek-receipt-gateway |
| **DB - Collections** | `emails` (Mongoose model `Email`: `receipt_user_id`, `email_in_address`, `tenant`, `status`); `emaillogs` (model `EmailLogs`, used elsewhere for delivery logging — not central to sync/gateway paths in the cited files) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `EmailController` declares no route-level guards; whether these routes are internal-only (network/VPC, API gateway auth) is not visible in code. `syncReceiptUsers` swallows Sleek Back HTTP failures into an empty array via `catch` in `getReceiptUsersFromSleekBack` — confirm operational alerting. Exact OpenAPI tag name `openapi-tag-sleek-receipt-gateway` may be applied in a separate spec bundle not present on the controller file. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/email/email.controller.ts`

- **`POST /email/sync`** → `EmailService.sync(body)` — upserts one email payload.
- **`GET /email`** query `email_in_address` → `findEmailByEmailInAddress`.
- **`POST /email/reinitialize-email-gateway`** → `EmailGateway.onModuleInit()` (async method used without `await` at call site).
- **`POST /email/manual-sync`** → `EmailService.syncReceiptUsers(body)`.

### `src/modules/email/email.service.ts`

- **`updateOrCreateEmailData`:** `findOneAndUpdate` on `receipt_user_id` + `tenant`, upsert.
- **`syncReceiptUsers`:** loops with `skip`/`limit`, calls `SleekBackService.getReceiptUsersFromSleekBack`; maps `email_in_address`, `status_v2` → `status`, `tenant`, `receipt_user_id`; optional delta via `EmailSyncType.DELTA` and `start_date`/`end_date`; optional `company_id`; inter-batch `delay` ms.
- **`@Cron`:** `handleSync` sets delta window yesterday–today, iterates `CountriesToSync` (SG, HK, UK, AU), calls `syncReceiptUsers` per tenant.

### `src/modules/sleek-back/sleek-back.service.ts`

- **`getReceiptUsersFromSleekBack`:** HTTP Basic with `SLEEK_SERVICE_CLIENT_ID` and per-tenant `SLEEK_*_SERVICE_CLIENT_SECRET`; `GET {baseUrl}/internal/receipt-users?…` with skip, limit, dates, company_id as query params.

### `src/modules/email/gateway/email.gateway.ts`

- **`OnModuleInit`:** `verifyAuth` — loads Google credentials for `EMAIL_GATEWAY_CLIENT_ID`, refreshes access token if expired, builds XOAUTH2 via `GoogleService.generateAuth2Token`, recreates IMAP client, `start()`.
- **`createImapClient`:** `simple-node-imap-async` to `imap.gmail.com:993`, TLS, `EMAIL_GATE_WAY_SEARCH_FILTERS` JSON, `fetchUnreadOnStart`, attachments streamed.
- **Listeners:** reconnect on `server:disconnected` via `verifyAuth`; on `message` — random delay, Redis lock on Message-ID, `IncomingEmailReader.readEmailMessage`, `EmailForwarderService.sendEmailToReceipt`.

### `src/modules/email/models/email.schema.ts`

- Indexes: `email_in_address` unique; compound `{ receipt_user_id: 1 }`.

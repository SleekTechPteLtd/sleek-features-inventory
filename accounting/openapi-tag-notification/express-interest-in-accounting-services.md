# Express interest in accounting services

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Express interest in accounting services |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated Sleek user (client-facing) |
| **Business Outcome** | The accounting team receives a structured lead with contact and package context so they can follow up on accounting services interest. |
| **Entry Point / Surface** | Sleek client app or flows that call the notification API — `POST /v2/notification/accounting` (`sleek_auth` per OpenAPI); handler uses `userService.authMiddleware`. |
| **Short Description** | Validates `name`, `email`, and optional `packageType`, then sends a transactional email via the configured `NOTIFY_ACCOUNTING_EMAIL` template to `config.accounting.emails`, with BCC to `config.accountingZapier.emails` for Zapier-side automation. Returns `200` with echoed `userName`, `userEmail`, and `packageType`. |
| **Variants / Markets** | SG, HK, UK, AU (multi-platform config under `multi-platform/config/<tenant>`; recipients and templates are tenant-specific via config). |
| **Dependencies / Related Flows** | **Mailer**: `mailerVendor.sendEmail` with `config.mailer.templates.NOTIFY_ACCOUNTING_EMAIL`, `config.support.emails.from`, BCC `config.accountingZapier.emails`. **Related**: `POST /v2/notification/accountingv2` uses `send-accounting-email-v2` (separate capability). **Sales enquiry**: `POST /v2/notification/sales` is a parallel enquiry path. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None in this flow (no persistence in handler or store-command). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | OpenAPI `NotifyAccountingRequestSchema` marks `packageType` as required, but the handler treats `packageType` as optional — align spec vs implementation. Confirm which client surfaces call v1 vs v2 accounting notification. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/notification.js`

- Mount: `app-router.js` registers `router.use("/v2/notification", …)`.
- **`POST /accounting`** — `buildPostRoute("/accounting", sendAccountingNotificationHandler.execute)` with `userService.authMiddleware`.
- Also registers `/accountingv2` and `/sales` (out of scope for this feature file).

### `controllers-v2/handlers/notification/send-accounting-email.js`

- **Validation** — `Validator.object`: `name` and `email` required (email format); `packageType` optional (html-stripped string, empty/null allowed).
- **`execute`** — `validateRequest` → `sendAccountingEmailCommand.execute(input)` → `200` JSON response; errors passed to `next(error)`.

### `store-commands/notification/send-accounting-email.js`

- **`sendEmail`** — Template `config.mailer.templates.NOTIFY_ACCOUNTING_EMAIL`; variables `subject` (`Interested in Accounting service - ${input.name}`), `name`, `packageType`, `email`; recipients `config.accounting.emails`; `mailerVendor.sendEmail(..., { bccRecipients: config.accountingZapier.emails })`.
- **`execute`** — Awaits `sendEmail`, returns `{ userName, userEmail, packageType }` from `input`.

### `public/api-docs/notification.yml`

- **`POST /v2/notification/accounting`** — Tags `notification`, `v2`; `security: sleek_auth`; 200 → `NotificationAccountingResponseSchema`; 422 for invalid parameters.

### Unknown columns (reason)

- **Disposition** — Unknown per pipeline default.

# Search receipt email delivery logs

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Search receipt email delivery logs |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authorized callers holding the configured logs API token) |
| **Business Outcome** | Authorized operators can look up outbound receipt-related email send history—timing, status, recipients, and failure details—to troubleshoot delivery problems and support audit of communications. |
| **Entry Point / Surface** | Sleek Receipts HTTP API: `GET /api/logs/search` with `Authorization` header matching `config.logsToken.authorization`; not exposed as an in-app Sleek navigation path in this repo (operator/integration surface). |
| **Short Description** | Searches the `EmailLog` Mongo collection with optional UTC `from` / `to` query bounds on `createdAt`, plus any additional query parameters passed through to Mongoose `find`. Responses return `{ success, results }` with matching log documents (subjects, recipients, `sending_status`, `stack_trace` on failures, company/receipt linkage, attachments metadata, etc.). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Log rows are created when outbound mail is sent or fails (`EmailLogCreator` from mailer paths, e.g. `sleekmailer-sender`, `nodemailer-sender`). **Related:** Receipt resubmission and webhooks reference `emaillogs_id` / email log linkage elsewhere in the service. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `emaillogs` (Mongoose model `EmailLog`; default collection name for model `EmailLog`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which internal tools or runbooks call `/api/logs/search` in each environment; whether the logs token is rotated via config management only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route registration** — `index.js`: `app.use("/api/logs", LogsRouter)`.
- **Route** — `src/routes/logs.js`: `GET /search` → `LogsService.logsMiddleware`, then `EmailLogController.searchEmailLog`.
- **Auth** — `src/services/logs.js`: `logsMiddleware` allows the request only if `req.headers.authorization` strictly equals `config.logsToken.authorization` (shared secret style, not user JWT).
- **Controller** — `src/controllers/email-log.js`: `searchEmailLog` reads `from`, `to`, and remaining `req.query` keys; maps `from`/`to` to `createdAt.$gt` / `createdAt.$lt` via `getISOFormat` (UTC from epoch ms); runs `emailLog.find({ ...additionalParams, ...params })`; returns HTTP 200 with `{ success: true, results }` or 400 with `{ success: false, error }`.
- **Schema** — `src/schemas/email-log.js`: `EmailLog` fields include `source`, `sent_via`, `company_id`, `receipt_user`, `receipt_type`, `from`, `message`, `subject`, `email_in_address`, `receiver_address`, `to[]`, `attachments[]`, `sending_status` (tenant enum from `shared-data.json`: success/failed), `stack_trace`, `is_retrigger`, `old_email_log_id`; `timestamps: true` supplies `createdAt`/`updatedAt`; compound index on `source`, `sent_via`, `sending_status`.
- **Write path (context)** — `src/email-logs/creator.js`: `logSuccess` / `logError` persist rows with `sending_status` success or `"failed"` and optional `stack_trace`, tying sends to company and receipt user context.

# Notify operations of future-dated document events

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Notify operations of future-dated document events |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Internal operations get alerted when stored document detail rows have a `document_date` after “today,” so suspicious extraction, timezone, or submission mistakes can be reviewed before they affect bookkeeping. |
| **Entry Point / Surface** | Operational batch script: `sleek-receipts` `src/scripts/send-email-notification-for-future-dss.js` (loads env, connects Mongo, queries future-dated events, sends one transactional email). No in-app UI; intended to run on a schedule outside this repo. |
| **Short Description** | On each run, the script loads all `DocumentDetailEvent` documents whose `document_date` is strictly greater than the current time, aggregates their Mongo `_id`s, and sends a single SleekMailer email using template `dss_with_future_date` to fixed internal recipients with subject “Notification when a future date is extracted.” If no matching rows exist, it logs an error and exits without email. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `DocumentDetailEvent` schema and collection (receipt/document pipeline, ML extraction, submission flows); transactional email via `src/mailer/index.js` (SleekMailer in production/staging/sit, Nodemailer in dev/test); template id `dss_with_future_date` in the mail platform |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (read: `find` on `document_date: { $gt: currentDate }`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Cron or orchestration schedule and environments where this script is deployed are not defined in-repo; whether hardcoded `to` / `cc` should move to config for non-prod; whether “future” relative to UTC vs local `moment()` matches business intent across regions. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Script (`src/scripts/send-email-notification-for-future-dss.js`)

- **`getDocumentEvents`:** `DocumentDetailEvent.find({ document_date: { $gt: currentDate } })` with `currentDate = moment().toDate()`; throws `"No document found to send mail notification"` if empty.
- **`sendMailNotification`:** Builds comma-separated `_id` list; calls `EmailSender.sendEmail` with `templateId: "dss_with_future_date"`, `from: config.noreply.from`, `variables.subject`, `documentText` singular/plural, `documentIds`; `to` and `ccRecipients` from module-level `EMAIL_CONFIG` (fixed addresses).
- **`main`:** Loads events then sends mail; errors logged to console.
- **Boot:** `dotenv-flow`, `databaseServer.connect()`, `main()`, timing logs, `process.exit()` in `finally`.

### Schema (`src/schemas/document-detail-event.js`)

- **Model:** `mongoose.model('DocumentDetailEvent', documentDetailEventSchema)` → collection name follows Mongoose default (`documentdetailevents`).
- **Field used for selection:** `document_date: Date` among company, submission, line items, Dext links, etc.

### Mailer (`src/mailer/index.js`)

- **`emailSender.sendEmail`:** Dispatches to `sleekmailer-sender` when `NODE_ENV` is `production` (live) or `staging` / `sit` (test mode flag); `test` and default use `nodemailer-sender`.

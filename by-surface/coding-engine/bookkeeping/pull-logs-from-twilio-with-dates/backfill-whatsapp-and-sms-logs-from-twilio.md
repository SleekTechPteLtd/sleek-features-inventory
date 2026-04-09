# Backfill WhatsApp and SMS communication logs from Twilio

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Backfill WhatsApp and SMS communication logs from Twilio |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Historical Twilio WhatsApp/SMS traffic for a chosen period is stored in MongoDB so support, auditing, and receipt-related workflows can rely on complete messaging records. |
| **Entry Point / Surface** | Sleek Receipts · batch script (`src/scripts/pull-logs-from-twilio-with-dates.js`), run manually with Node and two date arguments; not an app screen. |
| **Short Description** | Connects to MongoDB, reads start/end dates from CLI (`DD/MM/YYYY`), lists Twilio messages sent in that inclusive day range, maps each message (including media URLs) to the WhatsApp SMS log schema, and inserts rows. Duplicate message SIDs are rejected by a unique index on `sid`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio Messages API and Media API; MongoDB (sleek-receipts); env `RECEIPTS_ACCOUNT_SID`, `RECEIPTS_ACCOUNT_AUTH_TOKEN`; sibling rolling sync `src/scripts/pull-logs-from-twilio.js` and inventory doc `accounting/pull-logs-from-twilio/sync-whatsapp-sms-logs-from-twilio.md`; downstream use of WhatsApp/Twilio logs in support and receipt flows. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `whatsappsmslogs` (Mongoose model `WhatsappSmsLog`; default pluralized collection name — confirm in deployment if overridden) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether Twilio `messages.list` pagination covers very large backfills (SDK returns paginated results; script uses `pageSize: 100`); ops ownership and when backfill is run; confirm live MongoDB collection name. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/scripts/pull-logs-from-twilio-with-dates.js`**: Loads `dotenv-flow`; `databaseServer.connect()`; Twilio client from `RECEIPTS_ACCOUNT_SID` / `RECEIPTS_ACCOUNT_AUTH_TOKEN`; parses `process.argv[2]` and `[3]` with `moment(..., "DD/MM/YYYY")`; requires valid range with `startDate.isSameOrBefore(endDate)`; `getSMSMessagesByDate(startDate, endDate)` uses `startOf("d")` / `endOf("d")` and `defaultClient.messages.list({ dateSentBefore, dateSentAfter, pageSize: 100 })`; `mapWhatsappLog` strips `whatsapp:` from `from`/`to`, lists media via `mes.media().list()`, builds `attachments` as `https://api.twilio.com` + media URI without `.json`; `WhatsappLog.create(mappedMessage)` per message; logs added vs total counts and exits.
- **`src/schemas/whatsapp-sms-logs.js`**: Mongoose schema for `WhatsappSmsLog` with `body`, `direction`, indexed `from`, `to`, `error_message`, `uri`, `account_sid`, `sid`, `attachments[]` (strings), `status`, `number_of_media`, `date_sent`, `date_created`, `timestamps: true`; **unique index** on `{ sid: 1 }` (duplicate inserts fail).

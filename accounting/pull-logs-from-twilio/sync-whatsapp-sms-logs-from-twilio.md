# Sync WhatsApp SMS logs from Twilio

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync WhatsApp SMS logs from Twilio |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Local storage of Twilio WhatsApp traffic (including media URLs) matches what support and downstream receipt flows need for history, resubmission, and analytics alignment. |
| **Entry Point / Surface** | Sleek Receipts · batch script (`src/scripts/pull-logs-from-twilio.js`), run on a schedule or manually with Node; not an app screen. |
| **Short Description** | Connects to MongoDB, lists recent Twilio messages for the receipts account, fetches media URLs when present, maps each message to the WhatsApp SMS log schema, and inserts new rows. Duplicate SIDs are skipped via a unique index on `sid`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Twilio Messages API and Media API; MongoDB (sleek-receipts); env `RECEIPTS_ACCOUNT_SID`, `RECEIPTS_ACCOUNT_AUTH_TOKEN`; downstream use of WhatsApp / Twilio log sources in receipt resubmission and reporting (e.g. `whatsapp twilliologs` in analytics). |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `whatsappsmslogs` (Mongoose model `WhatsappSmsLog`; default pluralized collection name — confirm in deployment if overridden) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Exact schedule and ops ownership of the script; whether `getSMSMessagesByDate` window (roughly “before start of today, after end of two days ago”) matches intended SLA; confirm live MongoDB collection name; relationship to `pull-logs-from-twilio-with-dates.js` variant. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/scripts/pull-logs-from-twilio.js`**: Loads `dotenv-flow`; `databaseServer.connect()` from `../database/server`; Twilio client from `RECEIPTS_ACCOUNT_SID` / `RECEIPTS_ACCOUNT_AUTH_TOKEN`; `getSMSMessagesByDate()` calls `defaultClient.messages.list` with `dateSentBefore` / `dateSentAfter`, `pageSize: 100`; `mapWhatsappLog` strips `whatsapp:` prefixes from `from`/`to`, lists media via `mes.media().list()`, builds `attachments` as `https://api.twilio.com` + media URI without `.json`; `WhatsappLog.create(mappedMessage)` per message; logs counts and exits.
- **`src/schemas/whatsapp-sms-logs.js`**: Mongoose schema for `WhatsappSmsLog` with `body`, `direction`, indexed `from`, `to`, `error_message`, `uri`, `account_sid`, `sid`, `attachments[]` (strings), `status`, `number_of_media`, `date_sent`, `date_created`, `timestamps: true`; **unique index** on `{ sid: 1 }` (duplicate inserts fail).
- **`src/database/server.js`**: `DatabaseServer.connect()` delegates to `MongoServer` or `MemoryServer` by `NODE_ENV` (production/staging/sit → MongoServer with specific flags; test → MemoryServer; default → MongoServer).

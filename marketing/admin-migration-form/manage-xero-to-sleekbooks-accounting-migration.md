# Manage Xero to SleekBooks accounting migration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage Xero to SleekBooks accounting migration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Staff can start and supervise a client’s Xero-to-SleekBooks migration with clear step status, retries, manual completion when work happens outside the automated flow, readable migration history, and Dext setup guidance where the tenant applies. |
| **Entry Point / Surface** | Sleek Admin > Company overview (Accounting) — link to `/admin/migration-form/?cid={companyId}&uid={userId}` (`AccountingMigrationForm`); back link to `/admin/company-overview/?cid=...&currentPage=Accounting` |
| **Short Description** | Admin page loads company and user from query params, reads tenant from platform config, then drives migration via the Xero–SleekBooks service: start migration, poll migration details and steps, re-trigger failed steps, mark steps completed manually, and open a modal of timestamped migration logs. The Dext setup step is shown only when `tenant === "sg"`; it can show “Not Applicable” when the backend marks skip (e.g. inactive receipt system). |
| **Variants / Markets** | SG (full step list including Dext); non-SG tenants hide the Dext setup step in the UI |
| **Dependencies / Related Flows** | **xero-sleekbooks-service** (`API_XERO_SB_URL` / `https://xero-sleekbooks-service.sleek.sg` in prod) — `PUT /migration/uen/:uen/start`, `GET /migration/uen/:uen`, `PUT /migration/uen/:uen` (retrigger / manual complete payloads), `GET /migration/get-logs/:companyId`; **sleek-website** `api.js` — `getCompany`, `getUserDetails` for context; **admin company overview** `accounting-tools.js` — related create/update migration and permission checks; external **Dext** (`app.dext.com`) for manual setup copy |
| **Service / Repository** | `sleek-website` — `src/views/admin/migration-form/index.js`, `src/utils/api-xero-migration.js`, `src/utils/api.js` (`getCompany`, `getUserDetails`); backend: xero-sleekbooks-service |
| **DB - Collections** | Unknown (migration state and logs persisted by xero-sleekbooks-service APIs, not this repo) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact auth surface for admin migration-form page (layout/guard not in `index.js`; relies on same admin session as other admin bundles). Whether all migration step keys from logs (`invoices`, `manualjournal`, `banktransaction`, `reports`, `balancesheet`) can still appear in current step lists or are legacy. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/migration-form/index.js` (`AccountingMigrationForm`)

- **Bootstrap:** `domready` renders into `#root`; `componentDidMount` reads `cid` / `uid` from query string, loads `getCompany` / `getUserDetails` from `api.js`, then `getMigrationStatus()`, then `getPlatformConfig()` for `tenant` (default `sg`).
- **Start migration:** `migrationStarted` → `startMigration(uen)` then `getMigrationStatus()`.
- **Status and steps:** `getMigrationStatus` → `getMigrationDetails(uen)`; merges `response.data.migration` and `response.data.migrationSteps`; derives `currentActiveMigrationStep` from `migration.currentStep`; `checkMigrationStatus` sets `isMigrationStarted` when status is `posted`, `inprogress`, `completed`, or `failed`.
- **Re-trigger / manual complete:** `retriggerMigration` and `completeStepManually` → `retriggerMIgration({ uen }, { body: JSON.stringify({ currentStep, currentStepStatus, currentStepAction: "retrigger" | "manualcompleted", status, initiatedBy, ownerFirstName, ownerLastName, companyId, isAutoMigrate, receiptSystemStatus }) })`, then refresh status. Checkbox gates “I completed the step manually” before manual completion on non-Dext failures; Dext row uses “Dext has been set up successfully” + `CONFIRM SET UP`.
- **Logs:** `setLogsModal(true)` → `getMigrationLogs(companyId)` → `migrationLogs` grouped by day key; `returnLoggerInfoFromType` renders human-readable lines (activation, retrigger, manual complete, skip Dext when receipt system inactive, success/error per step).
- **Dext / tenant:** Renders Dext step only if `tenant === "sg"`; `isSkipDextSetup` shows “Not Applicable”; COA failure index `2` can show scheduled date `coaScheduledDate`.
- **Navigation:** Back and company name link to company overview Accounting tab.

### `src/utils/api-xero-migration.js`

- **Base URL:** `process.env.API_XERO_SB_URL` or prod `https://xero-sleekbooks-service.sleek.sg` / dev `http://localhost:6001`.
- **Endpoints used by this feature:** `startMigration` → `PUT /migration/uen/:uen/start`; `getMigrationDetails` → `GET /migration/uen/:uen`; `retriggerMIgration` / `updateMigration` → `PUT /migration/uen/:uen`; `getMigrationLogs` → `GET /migration/get-logs/:companyId`. Also exported: `createMigration` → `POST /migration/update`, `checkPermissionsToAccessMigration` → `GET /permission/:userId/:companyId` (used from `accounting-tools.js`, not from migration-form).
- **Responses:** `handleResponse` parses JSON, runs `checkResponseIfAuthorized` on status.

### `src/utils/api.js`

- **`getCompany(companyId)`** — company record for UEN and display name (lines ~675+).
- **`getUserDetails(userId, {})`** — admin user for audit fields on PUT bodies (lines ~258+).

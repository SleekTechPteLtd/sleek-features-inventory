# Automated SBA business account creation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Automated SBA business account creation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Approved SBA applicants that are live companies get DBS business accounts opened in bulk without manual per-company setup, once partner authorisation and user consents are satisfied. |
| **Entry Point / Surface** | Sleek Back HTTP API: `GET /v2/sba-auto-creation/trigger` starts the job and returns `executionId` + initial status; `GET /v2/sba-auto-creation/get-status/:executionId` polls in-memory execution status (`running`, `completed`, `failed`). No Sleek app navigation path in this repo—typically called from operator tooling or automation. CLI/script entry: `start("script")` in `autoCreateBusinessAccount.js` boots Mongoose and exits the process when done. |
| **Short Description** | When the CMS feature `sba_auto_account_creation` is enabled, the job selects live companies with `sba_application_status: "approved"` and `sba_account_creation_executed` not true. For each company it resolves the main signee (with optional `autoAssignMainSignee` from Camunda), validates consent and financial-partner TNC on the main signee, optionally sends throttled PII consent reminder emails per CMS `sba_pii_consent_reminder`, records outcomes on `SbaAutoOnboarding`, checks SBA access authorisation via the bank API, gathers eligible owner admins, and POSTs account creation to the SBA business-account service (DBS vendor). Successful creation sets `sba_account_creation_executed` and `has_SBA` on the company. |
| **Variants / Markets** | `SG` (DBS vendor, Camunda SG incorporation helper for main signee; no other markets evidenced in code paths). |
| **Dependencies / Related Flows** | **External**: `SBA_BANK_API_URL` — `GET /sba/v2/customer/onboarding/sba-access-authorisation`, `POST /sba/v2/admin/business-accounts`. **Internal services**: `business-account-service` (`getEligibleUsersForBusinessAccountCreation`, `checkSbaAccessAuthorisation`, `requestCreateAccounts`), `mailer-service` (`BUSINESS_ACCOUNT_CONSENT_REMINDER`), `camunda-workflow` `autoAssignMainSignee`, `company-history-service` (via eligibility), CMS app features via `app-features-util`. **Related**: manual SBA onboarding and consent flows elsewhere in the product. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (Mongoose `Company`: `find`, `updateOne` with `sba_account_creation_executed`, `has_SBA`), `companyusers` (Mongoose `CompanyUser`: `findOne`, `find` with populate), `users` (Mongoose `User`: `updateOne` for consent popup flags), `sba_auto_onboardings` (Mongoose model `sba_auto_onboarding`: `create`, `find` for reminder history). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Who mounts auth in front of `/v2/sba-auto-creation` in production (tests hit routes without auth shown here); whether execution status should survive process restarts (currently in-memory `sba-auto-creation-util` store only). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sba-auto-creation.js`

- Express router: **`GET /trigger`** — generates `executionId` with `uuid`, calls `start(executionId)` from `autoCreateBusinessAccount`, `set(executionId, "running")`, returns JSON `{ executionId, status }` from `get`; on error sets status `failed` and `500` with `{ error: "Failed to trigger SBA auto creation job" }`.
- **`GET /get-status/:executionId`** — `get(executionId)`; `200` `{ status }` or `404` if missing.

### `app-router.js`

- Mounted at **`/v2/sba-auto-creation`**.

### `scripts/business-account/autoCreateBusinessAccount.js`

- **`start(executionId)`** — gates on `isCreateBusinessAccountEnabledInCMS` (`sba_auto_account_creation` general feature); runs **`createBusinessAccountForCompanies`** inside try/catch; sets execution status `completed` or `failed`; `executionId === "script"` triggers `bootMongoose` and `process.exit()`.
- **`createBusinessAccountForCompanies`** — `Company.find({ status: "live", sba_application_status: "approved", sba_account_creation_executed: { $ne: true } })`; loops **`createBusinessAccountForCompany`**.
- **`getCompanyMainSignee`** — `findMainSignee` via `getEligibleUsersForBusinessAccountCreation`, `query: { is_main_point_of_contact: true }` with skipped filter steps for share info / TNC / KYC; if missing, **`autoAssignMainSignee(company._id, "SBA Account Creation")`** then retry; **`checkMainSignee`** for consent/TNC and reminders.
- **`checkMainSignee`** — on consent/TNC failure, optional **`SbaAutoOnboarding`** reminder history and **`mailerService.sendEmail`** `BUSINESS_ACCOUNT_CONSENT_REMINDER` with dashboard URL; **`User.updateOne`** for consent popup flags; **`SbaAutoOnboarding.create`** with `status`, `failedReason`, `consentReminderEmailSentAt`.
- **`createBusinessAccountForCompany`** — if main signee present: **`checkSbaAccessAuthorisation(company._id)`**; if `is_authorised`, loads owner admins via **`getEligibleUsersForBusinessAccountCreation`** with `is_owner: true` excluding main signee; builds **`requestCreateAccounts`** payload (`vendor: "DBS"`, `create_if_no_accounts: true`, `account_type: "static"`); on success **`Company.updateOne`** sets `sba_account_creation_executed: true`, `has_SBA: true`.
- Helpers: **`transformCompanyUserToBusinessAccountUserPayload`**, **`findMainSignee`**, **`parsePhoneNumber`**, **`parseUserSex`**, **`getIdNumber`**, Sentry via **`createSentryLog`**.

### `services/business-account-service.js`

- **`requestCreateAccounts(payload)`** — `sbaAxios.post("/sba/v2/admin/business-accounts", payload)` with `SUPER_ADMIN_AUTH` and `x-correlation-id`.
- **`getEligibleUsersForBusinessAccountCreation`** — `CompanyUser` query with director/owner filters, KYC, PII consent, financial partner TNC, nominee director, resigned director checks (uses **`companyHistoryService.getCompanyHistory`**).
- **`checkSbaAccessAuthorisation(companyId)`** — `GET /sba/v2/customer/onboarding/sba-access-authorisation` with `company_id`.

### `utils/sba-auto-creation-util.js`

- In-memory **`set` / `get`** map for execution id → status string (`running`, `completed`, `failed`).

### Tests

- `tests/controllers-v2/sba-auto-creation/sba-auto-creation.js` — `GET /v2/sba-auto-creation/trigger` and `GET /v2/sba-auto-creation/get-status/:executionId`.

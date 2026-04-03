# Bulk import Australian companies from CSV

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk import Australian companies from CSV |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (authenticated admin with `companies` full access) |
| **Business Outcome** | Internal teams can onboard or migrate many Australian client companies in one step from a spreadsheet, creating live companies with admin users, document folders, and accounting staff assignments without manual entry per row. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `POST /v2/admin/au-companies/import` (multipart field `file`; CSV with a fixed header row skipped, data from row 2). Mounted in `app-router.js` under `/v2/admin`. Requires `userService.authMiddleware` and `accessControlService.can("companies", "full")`. Exact product UI path or screen name is not defined in these files. |
| **Short Description** | Accepts CSV/TXT/XLS uploads, parses rows with Australian company and admin fields (ABN, ACN, TFN, company type Company/Sole Trader, admin identity and contacts, accountant-in-charge and accounting manager emails). Validates each row with Joi, skips duplicates already recorded for the same ABN in the import tracking collection, creates a `Company` plus user/`CompanyUser` links (new user with `temporary_email` or link to existing), creates company root folders via `fileService`, assigns senior accountant and accounting manager via `CompanyResourceUser` when those users exist, and records per-row outcomes in import success/failure collections. Response returns counts and arrays of inserted companies and categorized errors. |
| **Variants / Markets** | AU |
| **Dependencies / Related Flows** | **Files**: `fileService.createCompanyRootFolder` → external file microservice when enabled, else legacy file service; sets `root_folder`, mailroom/secretary/requests/accounting folders on the company. **Users**: `Group` named `Sleek User` for new users; sole-trader path adds a second owner `CompanyUser` for a hardcoded default internal user email when present. **Staffing**: `ResourceAllocationRole` types `senior-accountant` and `accounting-manager`; `User` lookup by email from CSV; missing users are logged only. **Related**: `controllers-v2/handlers/au-companies/find.js` (ABN lookup for onboarding) is a separate flow. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies`; `users`; `companyusers` (model `CompanyUser`); `groups`; `resourceallocationroles`; `companyresourceusers`; `importaucompanies` (inline model `ImportAuCompany` — pending/completed import rows keyed by ABN); `importaufailedcompanies` (inline model `ImportAuFailedCompany` — validation, duplicate ABN, or insert failures). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether a dedicated admin UI calls this endpoint or usage is script-only; whether the hardcoded sole-trader default owner email should be configurable; confirm production volume and operational runbooks for partial failures. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/admin.js`

- **`POST /au-companies/import`** → `importAuCompanies` from `./handlers/au-companies/import`, with `userService.authMiddleware`, `accessControlService.can("companies", "full")`, `multer` upload to `tmp/csv/`, single field `file`.

### `controllers-v2/handlers/au-companies/import.js`

- **`importAuCompanies`**: Rejects extensions not in `csv`, `txt`, `xls`. Streams file through `csv-parser` with `CSV_HEADERS` and `skipLines: 1`. Per row: trims strings; checks `ImportAuCompany.findOne({ company_abn })` — if existing, logs duplicate and upserts `ImportAuFailedCompany` with `error_message: "findExistingABN"`. Else runs `validateBeforeInsert` (Joi): company type Company/Sole Trader, TFN rules, required admin name/email, valid emails for accountant in charge and accounting manager, optional phone and incorporation date. On validation failure, records failure document. On success, inserts `ImportAuCompany` with `status: "PENDING"` and `csv_data_to_insert`, then `insertCompaniesAndUsers`, `assignStaff`, sets import row to `COMPLETED` on success; on `insertCompaniesAndUsers` error, logs and upserts `ImportAuFailedCompany` with the error. Unlinks temp file after processing. JSON response: `totalInsertedCompanies`, `insertedCompanies`, `errors` with validation, duplicate, and unhandled error detail arrays.

- **`insertCompaniesAndUsers`**: Maps CSV to `Company` (e.g. `uen` ← ABN, `business_registered_number` ← ACN, `tax_number`, `company_type` SOLE_TRADER/COMPANY, `app_onboarding_version` Beta-AOT vs Beta-AOT-SoleTrader, `is_transfer`, `incorporation_date` from DD/MM/YYYY). Saves company, `fileService.createCompanyRootFolder`. Resolves admin user by `email` or `temporary_email`; creates new `User` with `temporary_email`, `client_type: "sleekClient"`, Sleek User `groups`, phone from country code + number, or attaches existing user via new `CompanyUser` with owner/director flags (sole trader omits those on primary link and optionally adds default internal owner). Returns inserted company.

- **`assignStaff`**: Loads `ResourceAllocationRole` for `senior-accountant` and `accounting-manager`; for each CSV email, if `User` exists, creates `CompanyResourceUser` linking company, user, and role.

- **Inline schemas**: `ImportAuCompany`, `ImportAuFailedCompany` registered on same module (import audit and failure tracking).

### `app-router.js`

- **`router.use("/v2/admin", require("./controllers-v2/admin"))`** — full path prefix for the route above.

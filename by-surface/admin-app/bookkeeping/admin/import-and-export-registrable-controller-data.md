# Import and export registrable controller data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Import and export registrable controller data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin API; `companies` `full`) |
| **Business Outcome** | Internal teams can bulk align Sleek’s registrable-controller register with imported files and export a CSV snapshot for compliance (e.g. ACRA-related registers) and operational data work. |
| **Entry Point / Surface** | Sleek Admin — authenticated HTTP API on sleek-back: `POST /v2/admin/import-registrable-controllers`, `POST /v2/admin/import-registrable-controllers-v2` (multipart field `file`), `GET /v2/admin/export-registrable-controllers`. Optional query filters: `clientType` (`sk` \| `ms`), `excludeCompanyStatus` (comma-separated company statuses). Exact admin UI labels and navigation are not defined in the referenced files. |
| **Short Description** | **Import (v1)**: Parses a fixed-header CSV, resolves companies by UEN, matches individual controllers to company users by ID/passport, and creates or updates `CompanyResourceUser` rows under the `registrable-controller` resource role via `CompanyResourceUserService`, with discrepancy checks against existing or derived profile data. **Import (v2)**: Same flow with a revised column set (`full_name`, `status`, `remarks`), structured rejection payloads, richer individual ID-type inference (S/G/FIN/passport), and corporate matching rules for foreign entities. **Export**: Aggregates active non-removed registrable-controller assignments, applies optional company filters, and returns `export-registrable-controllers.csv` with ACRA-style columns. |
| **Variants / Markets** | SG (Singapore UEN / ACRA-oriented fields and legends in code); other markets Unknown |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware`. **RBAC**: `accessControlService.can("companies", "full")`. **Domain**: `CompanyResourceUserService.saveResourceUser` / `updateResourceUser` for `registrable_controller` subdocuments; `ResourceRole` lookup `type: "registrable-controller"`. **Related**: Company onboarding / significant controllers elsewhere in product (not in these handlers). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies`; `companyusers` (with `user` populated); `resourceallocationroles`; `companyresourceusers` (read/write; export uses aggregation with `$lookup` to `resourceallocationroles` and `companies`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether v1 import is still preferred for any clients now that v2 exists; whether any caller relies on v1 `clientType` default behaviour when the query param is omitted (v1 wraps `undefined` in an array). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/admin.js`

- **`POST /import-registrable-controllers`** — `userService.authMiddleware`, `accessControlService.can("companies", "full")`, `multer` `upload.single('file')` → `uploadRegistrableControllerCsv.uploadRegistrableControllerCsv`.

- **`POST /import-registrable-controllers-v2`** — Same guards and upload → `importRegistrableControllersCSVV2.importCSV`.

- **`GET /export-registrable-controllers`** — `GET` with same auth and `can("companies", "full")` → `exportRegistrableControllers`.

Router is mounted at **`/v2/admin`** (`app-router.js`: `router.use("/v2/admin", require("./controllers-v2/admin"))`).

### `controllers-v2/handlers/registrable-controller/uploadRegistrableControllerCsv.js`

- CSV via `csv-parser` with `REGISTRABLE_CONTROLLER_HEADERS`, `skipLines: 1`; allowed extensions `csv`, `txt`, `xls`.

- **`ResourceRole.findOne({ type: "registrable-controller" })`**; per row: **`Company.findOne({ uen: { $regex, $options: "i" } })`**; optional **`excludeCompanyStatus`** and **`clientType`** (`sk` vs `ms` via `company.partner`) gate processing.

- **Individual (`category_type` `I`)**: **`CompanyUsers.find`** (shareholder or director) **`.populate("user")`**; match by `id_number` or `passport_number`; find existing **`CompanyResourceUser`** by `data.registrable_controller.identification_number`; **`CompanyResourceUserService.getDifference`**, **`updateResourceUser`** or **`saveResourceUser`**; tracks `updatedRecords`, `newRecords`, `rejectedRecords`.

- **Corporate (`C`)**: Query by `data.registrable_controller.uen_of_registrable_controller` or foreign-company path; same service methods; country check against `company.address.country` for new rows.

- Response JSON: `{ updatedRecords, newRecords, rejectedRecords }`; temp file unlinked after parse.

### `controllers-v2/handlers/registrable-controller/import-registrable-controllers-csv-v2.js`

- Logger `import-registrable-controllers-v2`; logs executor email and filter params.

- Headers include `full_name`, `status`, `remarks`; **`clientType` omitted → `[]`** (process all client types when not filtering).

- **Individual**: Infers `identification_type` from passport match vs `S`/`G` prefixes and **`user.residential_status`**; rejects with coded reasons (`CANNOT_DETERMINE_ID_NUMBER`, `DATA_DISCREPANCIES`, etc.); sets **`updated_using_v2`** / **`imported_using_v2`** / **`record_filed_with_acra`** where applicable; **`_createRejectionReason`** returns spreadsheet-oriented column names for rejected rows.

- **Corporate**: **`business_registered_name`** from `full_name`; stricter **`CORPORATE_RC_MISSING_IDENTIFIER_DETAILS`** when jurisdiction/UEN/foreign identifiers incomplete; lookup branches for SG vs foreign entities.

### `controllers-v2/handlers/registrable-controllers/export-registrable-controllers.js`

- **`CompanyResourceUser.aggregate`**: `$lookup` **`resourceallocationroles`** → `$match` **`role.type` === `registrable-controller`**, `data` not null, `is_removed` not true; `$lookup` **`companies`** → `$match` on **`company.status`** / **`company.partner`** per **`clientType`** and **`excludeCompanyStatus`**.

- Builds CSV header row then **`extractDetails`** per document: reads **`data.registrable_controller`**, **`appointed_date`**, **`cessation_date`** from parent doc; formats dates and nationality/jurisdiction via **`COUNTRIES`**.

- Response: **`Content-Type: text/csv`**, **`Content-Disposition: attachment; filename=export-registrable-controllers.csv`**.

### `services/company-resource-user/company-resource-user-service.js` (referenced)

- **`getDifference`**, **`parseDateToFormat`**, **`updateResourceUser`**, **`saveResourceUser`** — shared persistence for registrable-controller payloads (not re-opened for this row; behaviour invoked by both import handlers).

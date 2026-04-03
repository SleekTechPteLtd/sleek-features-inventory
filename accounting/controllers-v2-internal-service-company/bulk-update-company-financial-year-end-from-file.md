# Bulk update company financial year end from file

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk update company financial year end from file |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (Operations User, Finance User, or Admin running a bulk FYE correction) |
| **Business Outcome** | Many companies’ financial year end fields can be aligned with a spreadsheet in one operation, with authoritative FYE calculations delegated to the FYE service before persisting to the company record. |
| **Entry Point / Surface** | HTTP API: `POST /internal/companies/update-fye-from-file` (multipart field `file`; optional body `worksheetName`, `startRow`, `endRow`). Requires `userService.authMiddleware`. Exact Sleek app or internal-tool UI path is not defined in this repo. |
| **Short Description** | Accepts an Excel workbook (`.xlsx` / `.xls`, max 10MB), reads rows with at least an `_id` column (company Mongo id) and optional `last_filed_fye`, `next_fye_to_file`, and `financial_year`. For each row it loads the company, refreshes FYE from the Get Company FYE path, calls the Sleek FYE microservice to compute updated dates, then writes `financial_year`, `current_fye`, and `last_filed_fye` on the company document. Returns per-row success and error arrays. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek FYE microservice**: `POST .../api/v1/fye/update-fye-from-platform` via `services/sleek-fye/update-fye.js` (HMAC-signed payload, API key). **Same repo**: `Company.loadFye()` → `GetCompanyFyeService`; `Company.updateOne` persists results. **Operational**: `scripts/company/fye-upload-bulk-update.js` reuses `processFyeBulkUpdateFromExcel` for CLI/batch runs. **Monitoring**: `Alert` on FYE service HTTP failures. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (Mongoose model `Company`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | When `last_filed_fye` matches incorporation date, the handler records an error but does not skip the row—confirm whether duplicate processing is intended. `worksheetName` is required for `getWorksheet` to resolve; callers must supply it or the upload fails with validation error. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/internal-service/company.js`

- **`router.use("/companies", require("../handlers/company/fye-upload-bulk-update"))`** — mounts FYE upload routes under the internal company router.

### `app-router.js`

- **`router.use("/internal", require("./controllers-v2/internal-service/company"))`** — full prefix for the feature is `/internal/companies/...`.

### `controllers-v2/handlers/company/fye-upload-bulk-update.js`

- **`router.route("/update-fye-from-file").post(userService.authMiddleware, ...)`** — authenticated POST; `multer` `single("file")`, Excel extensions only, 10MB limit.
- **Body**: `worksheetName`, `startRow` (default 2), `endRow` passed to `processFyeBulkUpdateFromExcel(req.file.buffer, ..., req.user._id)`.
- **Responses**: `200` with `{ success: true, results }`; `422` for validation/multer issues; `500` for other processing errors.

### `services/fye-upload-bulk-update.service.js`

- **`processFyeBulkUpdateFromExcel`**: ExcelJS loads buffer; row 1 = headers; requires `_id` column; iterates from `startRow` to `endRow` or sheet end; skips rows with empty `_id`.
- **`Company.findById`**, **`company.loadFye()`** before applying row data.
- **Row mapping**: `last_filed_fye`, `financial_year` (as `currentFye`), `next_fye_to_file` (empty string → keep `company.financial_year`; `null`/`NULL`/`null` treated as unset).
- **`updateFye(company._id, company.uen, company.name, currentFye, nextFyeToFile, lastFiledFye, userId)`** then **`Company.updateOne`** with `$set` of `financial_year`, `current_fye`, `last_filed_fye` from the service response.
- **Returns** `{ success[], errors[], total }` with row numbers and messages.

### `services/sleek-fye/update-fye.js`

- **Production**: `axios.post` to `config.sleekFye.baseUrl` + `/api/v1/fye/update-fye-from-platform` with HMAC signature headers; **`NODE_ENV === "test"`** returns mock FYE dates.

### `schemas/company.js`

- **`loadFye`**: `GetCompanyFyeService(this._id).execute()` hydrates `current_fye`, `financial_year`, `last_filed_fye` on the document instance before bulk logic runs.

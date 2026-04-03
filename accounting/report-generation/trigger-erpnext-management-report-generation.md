# Trigger ERPNext management report generation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Trigger ERPNext management report generation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System (integrations) |
| **Business Outcome** | Each queued company-and-period request gets a dedicated Google Sheet workbook with standard management-report tabs, and a shareable edit URL is recorded on the request progress sheet so teams can fill or link ERPNext reporting work in one place. |
| **Entry Point / Surface** | Backend HTTP trigger on `sleek-erpnext-service`: **GET** `/report-generation/initiate` (no auth guard in code—likely internal or gateway-only). |
| **Short Description** | Reads pending rows from a configured Google Sheet **REQUESTS** tab, appends them to **REQUEST PROGRESS** with a processing token and timestamp, clears the consumed request rows, creates one new spreadsheet per request (title includes company and month/year), adds tabs named Profit and Loss, Balance Sheet, Trial Balance, General Ledger, and Schedule, moves the file into a configured Drive folder, and writes each workbook’s edit URL into column **I** of **REQUEST PROGRESS**. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Google Sheets API and Google Drive API (service account `credentials.json`); env: `ERPNEXT_REPORT_GOOGLE_SHEET_ID`, `ERPNEXT_REPORT_GDRIVE_FOLDER_ID`. Downstream: manual or separate processes that populate tabs or pull ERPNext data (not implemented in this service code path). |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None—state is held in Google Sheets (`REQUESTS`, `REQUEST PROGRESS`), not MongoDB. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `/report-generation/initiate` is protected by an API gateway or network policy; whether tab content is filled by another job or manually; controller does not `await` `initiateReportGeneration()` so HTTP success does not guarantee completion or surfaced errors. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/report-generation/report-generation.controller.ts`)

- **GET** `/report-generation/initiate` — `initiateReportGeneration` → calls `ReportGenerationService.initiateReportGeneration()` **without** `await` (`ApiOperation`: “Generates ERP Next report requests”). Returns **302** `HttpStatus.FOUND` on the try path; **404** on catch (unlikely if service swallows errors). No `AuthGuard` / `M2MAuthGuard` on the handler.

### Service (`src/report-generation/report-generation.service.ts`)

- **`ErpNextReportTypes`**: tab titles **Profit and Loss**, **Balance Sheet**, **Trial Balance**, **General Ledger**, **Schedule**.
- **`RequestProgress`**: row suffix values **processing**, **done**, **failed** (append path sets **processing**; **done**/**failed** not referenced in this file).
- **`getGSheetValues`**: `spreadsheets.values.get` on `ERPNEXT_REPORT_GOOGLE_SHEET_ID`, strips header row.
- **`addNewRequestProgress`**: `spreadsheets.values.append` to range `'REQUEST PROGRESS'` with appended columns: status **processing**, `Date.now()`, `randomAlphaNumericString(32)`.
- **`removeOldRequest`**: `batchClear` on `'REQUESTS'!2:{n+1}` after processing `n` requests.
- **`createGSheet`**: `spreadsheets.create` with title and per-tab `sheets`; then `drive.files.update` to **addParents** `ERPNEXT_REPORT_GDRIVE_FOLDER_ID` and **removeParents** `'root'`.
- **`updateSheet`**: `spreadsheets.values.batchUpdate` on the **same** progress spreadsheet—writes workbook URLs to **`REQUEST PROGRESS!I{row}`** as `${GSHEET_BASE_URL}{id}/edit#gid=0`.
- **`createReportTemplateForNewRequests`**: maps each `[company, startDate]` to a sheet title `{company}-Management Report- {MMMM YYYY}` and the five enum tabs; aligns new URLs to the last appended progress rows.
- **`initiateReportGeneration`**: orchestrates: read **REQUESTS** → append progress → clear **REQUESTS** → re-read **REQUEST PROGRESS** → `createReportTemplateForNewRequests`. No ERPNext/Frappe HTTP client calls in this module.

### Google utilities (`src/utilities/google-sheet-utilities/index.ts`)

- **`authentication`**: GoogleAuth with `keyFile` `./src/utilities/google-sheet-utilities/credentials.json`, scopes spreadsheets + drive; returns `sheets` v4 and `drive` v3 clients.
- **`GSHEET_BASE_URL`**: `https://docs.google.com/spreadsheets/d/` (used to build edit links in column I).

### Tests (optional cross-check)

- `tests/report-generation/service/report.generation.service.spec.ts`, `tests/report-generation/controller/report.generation.controller.spec.ts`, `tests/report-generation/report.generation.module.spec.ts` — exercise `initiateReportGeneration` and module wiring.

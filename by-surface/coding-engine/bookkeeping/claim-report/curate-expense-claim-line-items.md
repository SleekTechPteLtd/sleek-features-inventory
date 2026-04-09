# Curate expense claim line items

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Curate expense claim line items |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Bookkeeper (authenticated via `AuthGuard` on mutating line-item routes) |
| **Business Outcome** | Each expense claim report lists receipt-backed lines with correct categories, converted amounts, and approval state so reimbursement matches policy and ledger expectations |
| **Entry Point / Surface** | Sleek App > Bookkeeping > Expense claim report (API: `acct-coding-engine` `claim-report` routes; document publish flow links to `/bookkeeping/expense-claim/{reportId}`) |
| **Short Description** | Users attach receipt documents to a report, adjust categories, notes, amounts, FX, and per-line or bulk approval status; the service keeps MongoDB claim reports, linked receipt documents, audit logs, and EC report events in sync |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Receipt **Document** records (`sleek_receipts`); **Company** `ec_report_currency`; **SleekAuditor** audit logs; **document** publish events; **supplier** category rules when publishing; optional FX via `performConversion` / `getAmountConversions`; downstream publish/confirm/export on same controller |
| **Service / Repository** | `acct-coding-engine` |
| **DB - Collections** | MongoDB: **ClaimReport** (`report_items` embedded line items) on `DBConnectionName.CODING_ENGINE`; **Document** on `DBConnectionName.SLEEK_RECEIPTS`; **Feedback** (baseline for change monitoring in `updateReportItem`); **Company** when persisting default report currency |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all client surfaces use the same auth model as `AuthGuard`-protected routes; regional rollout of EC features not visible in these files |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/claim-report/claim-report.interface.ts`

- `ReportItem` models each line: `document_id`, `status`, `is_approved`, `approved_by`, `approval_date`, `category`, `supplier`, `currency`, `base_currency`, `total_amount`, `base_total_amount`, tax fields, `document_date`, `fx_rate` (`FXRate`), `file_uri`, `description`, `comment`, audit fields `updatedBy` / `lastUpdated`.
- `FindAllRequest` supports filtering reports by `status`, `currency`, dates, `claimUser`, etc.

### `src/claim-report/models/claim-report.schema.ts`

- `ClaimReportItem` / `ClaimReport` schema mirrors `ReportItem`; `report_items` is an array on the report; report-level `status` uses `ClaimReportStatus` enum (`new`, `toreview`, `publishing`, `approved`, `rejected`, `completed`, `error`).

### `src/claim-report/enum/claim-report.enum.ts`

- `ClaimReportStatus` values used when validating whether lines can be added or updated.

### `src/claim-report/claim-report.controller.ts`

- **Attach / replace lines from documents**
  - `PUT /claim-report/updateItems/:id` — `addRemoveReportItemsRowsDto` (`document_ids`); calls `addOrRemoveReportItemsRows` then `update` (no `AuthGuard` on this route in code).
  - `POST /claim-report/addReportItem` — `AuthGuard`; `addSingleReportItemRow` — adds a line from a document, resolves report by document date or creates one; passes user details for audit.
- **Edit line fields & approval**
  - `PUT :reportId/update-report-item` — `AuthGuard`; `UpdateReportItemDTO` — `updateReportItem` (note on document, category, `total_amount` with FX recalculation, per-line `status` / `is_approved`).
  - `PUT :reportId/report-items` — `AuthGuard`; bulk set `status` / `is_approved` on all report items via `updateReportItems`.
- **Multi-currency**
  - `POST :reportId/update-report-currency` — `AuthGuard`; `UpdateReportCurrencyDTO` — `updateReportCurrency` converts all items via `convertReportItems` / `performConversion`, updates report `currency` and `total_amount`, optionally sets `company.ec_report_currency` when `change_for_all_future_reports`.

### `src/claim-report/claim-report.service.ts`

- `addOrRemoveReportItemsRows` — blocks when report is `approved` or `completed`; builds new rows from `checkDocument` with `document_id` and status; returns array for controller to persist.
- `addSingleReportItemRow` — loads document; finds or creates EC report by document date; enforces status `new` | `toreview` | `error`; de-links document from other reports; builds `ReportItem` from document (category, supplier, base amounts, dates); `convertMultiCurrencyReportItems`; updates `report_items`, `currency`, `total_amount`; updates document `publish_entries`, `status`, `claim_report`; `sleekAuditorService.insertLogsToSleekAuditor`; `fetchAndPublishECReportEvent` / `fetchAndPublishDocumentEvent`.
- `updateReportItem` — updates line `status`/`is_approved` with `ECReportEventType.APPROVED` when status set; syncs `note` and `category` to **Document**; recalculates `total_amount` and `fx_rate` from edited converted amount vs `base_total_amount`; aggregates report `total_amount`; `monitorDocumentDifferenceAuditLog` vs **Feedback** snapshot.
- `updateReportItems` — bulk line approval/status with per-document audit logs.
- `updateReportItemFromDocumentDetail` — syncs line from document-side edits (category, converted amounts, supplier, date).
- `updateReportCurrency` — rewrites all `report_items` in target currency, updates linked documents’ `currency_rate` / `converted_total_*`, audit logs, `eventUtils.publishEvent`.

### `src/claim-report/dto/updateReportItem.dto.ts`

- Fields: `document_id`, optional `note`, `category` (`CoaData`), `total_amount`, `base_total_amount`, `converted_total_amount`, `currency_rate`, `supplier`, `document_date`, `status`.

### `src/claim-report/dto/updateReportCurrency.dto.ts`

- `report_currency`, optional `change_for_all_future_reports`.

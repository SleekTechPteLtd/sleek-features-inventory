# Backfill base amounts on expense claim line items

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Backfill base amounts on expense claim line items |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated API caller); runs as system-driven batch when invoked |
| **Business Outcome** | Historical or migrated expense claim reports keep line-level base currency, tax, document date, and FX fields aligned with underlying receipt documents so amounts reconcile for reporting and downstream accounting. |
| **Entry Point / Surface** | Coding engine REST API `POST /claim-report/bulk-migrate-base-in-report-items` (requires `AuthGuard`); no in-app navigation defined in this repo |
| **Short Description** | Accepts up to 500 claim report IDs plus `is_dry_run`. Loads those reports and their `report_items`, fetches matching receipt `documents` from Sleek Receipts, and for each line that still has a linked document copies `total_amount` → `base_total_amount`, `currency` → `base_currency`, `total_tax_amount` → `base_total_tax_amount`, `document_date`, and builds `fx_rate` from `currency_rate` and report currency. Persists with MongoDB `arrayFilters` on matching `document_id`, or simulates updates when `is_dry_run` is true. Returns the source documents and resulting report items. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on `claimreports` rows and embedded `report_items`; reads receipt `documents` (Sleek Receipts DB). Complements normal line-item flows (`addReportItem`, `updateReportItem`) that populate items incrementally; used for bulk reconciliation after schema or data migrations. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | claimreports (write); documents (read, Sleek Receipts connection) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Dry-run branch assigns from keys `report_items.$.…` but `$set` uses `report_items.$[eindex].…`, so preview values may not match what a real run would write—worth verifying before relying on dry-run output. Whether `base_*` fields are intentionally mirrored from document `total_amount` / `currency` (vs true company-base conversion) is implied by field names only. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`claim-report.controller.ts`:** `POST bulk-migrate-base-in-report-items` → `ClaimReportService.bulkMigrateBaseInReportItems`; `@UseGuards(AuthGuard)`; body `BulkMigrateBaseInReportItemsDto`, response `BulkMigrateBaseInReportItemsResponse`.
- **`dto/bulkMigrateBaseInReportItems.dto.ts`:** `is_dry_run: boolean`, `claim_report_ids: ObjectId[]` with `@ArrayMaxSize(500)`.
- **`dto/bulkMigrateBaseInReportItemsResponse.dto.ts`:** `documents`, `report_items` arrays.
- **`claim-report.service.ts` — `bulkMigrateBaseInReportItems`:** Validates non-empty `claim_report_ids`; `claimReportModel.find` by IDs; collects unique `document_id` from `report_items`; `documentModel.find` for those IDs; nested loops with `findOneAndUpdate` + `$set` and `arrayFilters` on `eindex.document_id`; `fx_rate`: `rate` from `doc.currency_rate`, `date` from `doc.document_date`, `currency` from `claimReport.currency`.
- **`models/claim-report.schema.ts`:** `ClaimReportItem` fields updated include `base_currency`, `base_total_amount`, `base_total_tax_amount`, `document_date`, `fx_rate`.
- **Tests:** `test/claim-report/service/bulkMigrateBaseInReportItems.spec.ts`, `test/claim-report/controller/bulkMigrateBaseInReportItems.spec.ts`; OpenAPI `openapi.yaml` operation `ClaimReportController_bulkMigrateBaseInReportItems`.

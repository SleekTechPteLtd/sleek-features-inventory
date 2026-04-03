# Unpublish expense claim ledger postings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Unpublish expense claim ledger postings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Finance User (authenticated API callers) |
| **Business Outcome** | When an expense claim report or line was published incorrectly, operators can roll back the in-engine publish state so documents and reports can be corrected and re-processed without leaving stale ledger-linked metadata. |
| **Entry Point / Surface** | Coding engine REST API: `DELETE /claim-report/:reportId/unpublish` and `DELETE /claim-report/:reportId/:documentId/unpublish` (`AuthGuard`); consumer UI not defined in this repo |
| **Short Description** | **Full report:** For reports in completed, publishing, error, or rejected status, loads all line documents, keeps only the latest expense-claim (`IntermidiateLedgerType.EXPENSE_CLAIM`) publish entry per document, sets documents to `EXP_CLAIM_REPORT` and not archived, bulk-writes Mongo updates, emits document update events, logs “Unlink SleekBooks/Xero transactions” to Sleek Auditor, sets report status to `toreview` or `new` (if still current month), and publishes `ECReportEventType.UNPUBLISHED`. **Single document:** Only allowed if the latest SleekBooks/Xero publish entry is not an active ledger post (`publishedToLedger`), report is not completed/publishing, removes the line from the report, clears `claim_report` and `publish_entries` on the document, sets document status to `PROCESSING`, emits events and audit, publishes `UNPUBLISHED`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Publish/confirm flows (`createInvoice`, `confirmECReport`); `DocumentUtilService.fetchAndPublishDocumentEvent`; `EventUtils` + `ECReportEventType.UNPUBLISHED` → `ec-report-events` topic; Sleek Auditor; MongoDB `documents` (Sleek receipts DB) and `claimreports` (coding engine DB); helpers `documentLatestECPublishEntry`, `documentLatestPublishEntry`, `publishedToLedger` in `generic.ts` |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | claimreports, documents |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether external Xero/SleekBooks voiding is performed outside this service (in-repo unpublish is Mongo/event/audit focused); exact product screens for operators |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`claim-report.controller.ts`:** `DELETE :reportId/unpublish` → `ClaimReportService.unPublishECReport(reportId, userDetails)`; `DELETE :reportId/:documentId/unpublish` → `unPublishDocument(reportId, documentId, userDetails)`. Both `@UseGuards(AuthGuard)`.
- **`claim-report.service.ts`:**
  - `unPublishECReport`: validates status ∈ `completed` | `publishing` | `error` | `rejected`; `documentModel.find` + `bulkWrite` per document with `$set`: `publish_entries: [publishedECReport]` from `documentLatestECPublishEntry`, `is_archived: false`, `status: DocumentStatus.EXP_CLAIM_REPORT`; `fetchAndPublishDocumentEvent` with `EventCaller.CLAIM_REPORT_SERVICE.unPublishECReport`; `sleekAuditorService.insertMultipleLogsToSleekAuditor` with action `Unlink SleekBooks/Xero transactions`; `claimReport.status` → `TOREVIEW` or `NEW` via `moment` month check; `eventUtils.publishEvent(ECReportEventType.UNPUBLISHED, ...)`.
  - `unPublishDocument`: guards with `documentLatestPublishEntry` + `publishedToLedger` (blocks if latest SB/Xero entry is active ledger post); blocks if report `completed` or `publishing`; filters `report_items`, `calculateTotalAmount`, `claim_report: null`, `publish_entries: []`, `status: DocumentStatus.PROCESSING`; `fetchAndPublishDocumentEvent`; `insertLogsToSleekAuditor`; `ECReportEventType.UNPUBLISHED`.
- **`claim-report.schema.ts`:** `ClaimReport.status` uses `ClaimReportStatus` enum.
- **`utils/generic.ts`:** `publishedToLedger`, `documentLatestPublishEntry` (latest SB/Xero CE entry), `documentLatestECPublishEntry` (latest `EXPENSE_CLAIM` entry).
- **`claim-report.module.ts`:** `Document` on `DBConnectionName.SLEEK_RECEIPTS`; `ClaimReport` on `DBConnectionName.CODING_ENGINE`.

# Apply SleekBooks invoice outcomes to published documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply SleekBooks invoice outcomes to published documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After a document (or expense-claim batch) is published toward SleekBooks, asynchronous invoice creation eventually succeeds or fails; this flow updates the coding engine’s publish entries, document or claim-report status, downstream events, and audit trail so books, UI, and operations reflect the real invoice result. |
| **Entry Point / Surface** | System: Nest `@SubscribeEvent` handlers on `CESleekBooksInvoiceDoneEvent` and `CESleekBooksInvoiceFailedEvent` (`InvoiceListener` at controller path `invoice-listener`) |
| **Short Description** | The listener routes completion payloads to `DocumentService`: standard documents use `updateInvoiceDoneEvent` / `updateInvoiceFailedEvent`; expense-claim reports (`isECReport`) use `updateECInvoiceDoneEvent` / `updateECInvoiceFailedEvent`, which update the claim report and all approved documents sharing the publish entry. Done paths set publish entry invoice id, link, and `DONE` status, adjust document status (e.g. in books or expense-claim report), decrement bookkeeper counters on success where applicable, republish document events, and write Sleek Auditor logs. Failed paths store errors, set publish entry `FAILED`, revert or error document/report status, republish events, audit, optionally notify via configured Slack templates. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: SleekBooks invoice creation after publish (events carry `document_id`, `publish_id`, `invoice_id`/`link` or `errors`). Downstream: `DocumentUtilService.fetchAndPublishDocumentEvent` / `fetchAndPublishBulkDocumentEvent` (`CodingEngineEventType.DOCUMENT_PUBLISHED`, `DocumentEventType.BULK_UPDATED`), `SleekAuditorService.insertLogsToSleekAuditor`, `UserActivityService.decrementBookkeeperDocCount` (non-EC success), `ClaimReportService` (EC paths), `notifyOnPublishFailure` for selected error patterns. Related: initial publish and publish entry creation elsewhere in `DocumentService`. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (documents); `claimreports` (expense-claim report records, EC success/failure paths via `ClaimReportService`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/kafka/listeners/invoice.listener.ts`** — `InvoiceListener`: `onCESleekBooksInvoiceDone` → `updateECInvoiceDoneEvent` vs `updateInvoiceDoneEvent` when `message.data.isECReport`; `onCESleekBooksInvoiceFailed` → `updateECInvoiceFailedEvent` vs `updateInvoiceFailedEvent`; both pass `CompanyLedgerTypeLabels.SLEEKBOOKS` as `publishTo`.
- **`src/kafka/events/ce-sleekbooks-invoice-done.event.ts`** — `CESleekBooksInvoiceDoneEvent`: `document_id`, `publish_id`, `invoice_id`, `link`, optional `isECReport`.
- **`src/kafka/events/ce-sleekbooks-invoice-failed.event.ts`** — `CESleekBooksInvoiceFailedEvent`: `document_id`, `publish_id`, optional `errors`, optional `isECReport`.
- **`src/document/document.service.ts`** — `updateInvoiceDoneEvent`: load document, optional bookkeeper count decrement, locate `publish_entries` match, `$set` publish entry `invoice_id`, `status` `DONE`, `link`, document `status` (`IN_BOOKS` or `EXP_CLAIM_REPORT` for expense claims), `fetchAndPublishDocumentEvent` with `DOCUMENT_PUBLISHED`, success audit to Sleek Auditor (publisher vs auto-publish), error audit on exception. `updateInvoiceFailedEvent`: `$set` publish entry `errors`, `status` `FAILED`, document `PROCESSING`, republish `DOCUMENT_PUBLISHED`, audit, optional `notifyOnPublishFailure` from `formatPublishErrors`. `updateECInvoiceDoneEvent` / `updateECInvoiceFailedEvent`: load/update `ClaimReport` (`COMPLETED` / `ERROR`), `updateMany` documents for approved IDs matching `publish_entries._id`, bulk document events, EC-specific audit and notifications (report-scoped links for failure notify).

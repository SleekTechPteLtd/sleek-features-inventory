# Reflect Xero invoice publish outcomes in documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reflect Xero invoice publish outcomes in documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After an asynchronous Xero invoice publish finishes, accounting documents and expense-claim report state stay aligned with what actually landed in Xero (success, failure, and linked invoice metadata). |
| **Entry Point / Surface** | Background — Kafka subscriber `CEXeroPublishListener` (no direct app navigation); outcomes surface in Coding Engine document and expense-claim report status after upstream publish completes. |
| **Short Description** | Listens for `CEXeroInvoiceDoneEvent` and `CEXeroInvoiceFailedEvent`. On success, updates the matching publish entry with Xero invoice id, link, and `DONE` status, sets document (or bulk EC) status accordingly, emits document events, and writes audit logs; on failure, records errors, sets publish entry and document/report status to failed/error, emits events, audits, and optionally notifies via configured Slack templates. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream Xero async publish pipeline (events carry `document_id`, `publish_id`, optional `isECReport`); `DocumentService` (`updateInvoiceDoneEvent` / `updateInvoiceFailedEvent` vs `updateECInvoiceDoneEvent` / `updateECInvoiceFailedEvent`); `claimReportService` for EC report id and approved document fan-out; `documentUtilService.fetchAndPublishDocumentEvent` / `fetchAndPublishBulkDocumentEvent`; `sleekAuditorService`; optional `notifyOnPublishFailure` (Slack). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (documents and embedded `publish_entries`); `claimreports` (claim report status for EC flows — Mongoose default for `ClaimReport`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Event payloads reference `link` on done paths in `DocumentService` but `CEXeroInvoiceDoneEvent` typing only lists `document_id`, `publish_id`, `invoice_id`, `isECReport` — confirm whether `link` is supplied at runtime from a wider payload; whether listener module name `ce-xero-publish-listener` is registered consistently with event names in all environments. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Kafka events (`kafka/events/`)

- **`CEXeroInvoiceDoneEvent`:** Extends `DomainEvent` with `document_id`, `publish_id`, `invoice_id`, optional `isECReport`.
- **`CEXeroInvoiceFailedEvent`:** Extends `DomainEvent` with `document_id`, `publish_id`, optional `errors`, optional `isECReport`.

### Listener (`kafka/listeners/ce-xero-publish.listener.ts`)

- **`onCEXeroInvoiceDone`:** If `message.data.isECReport`, calls `documentService.updateECInvoiceDoneEvent(data, CompanyLedgerTypeLabels.XERO)`; else `updateInvoiceDoneEvent`.
- **`onCEXeroInvoiceFailed`:** Same branch for `updateECInvoiceFailedEvent` vs `updateInvoiceFailedEvent`.

### Document service — standard documents (`document.service.ts`)

- **`updateInvoiceDoneEvent`:** Loads document by `document_id`; optional bookkeeper `decrementBookkeeperDocCount`; finds publish entry by `publish_id`; `updateOne` sets `publish_entries.$.invoice_id`, `status: PublishStatus.DONE`, `link`, and document `status` to `EXP_CLAIM_REPORT` (expense-claim receipt types) or `IN_BOOKS`; `fetchAndPublishDocumentEvent` with `CodingEngineEventType.DOCUMENT_PUBLISHED`; Sleek Auditor success log; catch path logs failure to auditor.
- **`updateInvoiceFailedEvent`:** `updateOne` sets `publish_entries.$.errors`, `status: PublishStatus.FAILED`, document `status: PROCESSING`; `DOCUMENT_PUBLISHED` event; `formatPublishErrors` + auditor; optional `notifyOnPublishFailure` with CE document deep link.

### Document service — EC report flows (`document.service.ts`)

- **`updateECInvoiceDoneEvent`:** Treats `document_id` as **report** id; `claimReportService.findById`; sets report `ClaimReportStatus.COMPLETED`; `updateMany` on approved documents sharing `publish_id` to set publish entry done + `DocumentStatus.EXP_CLAIM_REPORT`; `fetchAndPublishBulkDocumentEvent` with `DocumentEventType.BULK_UPDATED`; auditor.
- **`updateECInvoiceFailedEvent`:** Report `ClaimReportStatus.ERROR`; `updateMany` approved docs with `DocumentStatus.ERROR` and failed publish entries; bulk document event; `notifyOnPublishFailure` with `type: 'report'` and expense-claim web URL when template matches.

# Publish and align documents with bookkeeping

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Publish and align documents with bookkeeping |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Bookkeeper (AuthGuard); system/integrations (ApiKeyGuard for payment status sync and autopublish management) |
| **Business Outcome** | Ensures extracted invoices, bills, and related documents are posted to the correct ledger (SleekBooks or Xero) and stay consistent when operators change amounts, categories, or publication state, so books match operational reality. |
| **Entry Point / Surface** | Sleek Accounting / Coding Engine document flows (document API: publish, unpublish, bulk actions, published-document update, payment status, autopublish configuration); webhooks from SleekBooks for cancel/delete alignment |
| **Short Description** | Operators publish or unpublish documents (single or bulk), including expense-claim paths that route to claim reports. Published SleekBooks documents can be updated when SB reports eligible invoice states; payment status is patchable via API key for downstream sync. Supplier-category autopublish rules are evaluated and toggled via an aggregated pipeline and supplier service. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | SleekBooks (`sleekbooksService`: create/cancel/update invoice, journal entry, payment entry); Xero (`xeroService`) when company ledger is Xero; reconciliation (`reconciliationService`, ML auto-reconcile on publish); supplier rules (`supplierService`, `categoryMapping`); expense claims (`claimReportService` on bulk publish); audit logging (`sleekAuditorService`); events (`eventUtils`, `documentUtilService`); user activity; Frappe webhooks (`handleCancelDocumentWebhookFromSB`, `handleDeleteDocumentWebhookFromSB`) |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `documentdetailevents` (documents and embedded `publish_entries`); `companies` (default Mongoose collection for `Company` model) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `PATCH :documentId/payment-status` updates `payment_status` on the document in MongoDB only in the reviewed path—confirm whether callers are always SleekBooks or another service that owns the canonical paid state; whether `ENABLE_UPDATE_PUBLISHED_DOCUMENT` and SB eligibility rules are consistent across environments. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`document.controller.ts`)

- **AuthGuard (authenticated users):** `POST :documentId/publish` → `publishDocument`; `PATCH :documentId/unpublish` → `unPublishDocumentById`; `POST bulk/unpublish` → `bulkUnpublishDocuments`; `POST bulk_publish` → `bulkPublishDocuments` (max 100 per request per service); `PUT :documentId/published` + `UpdatePublishedDocumentDTO` → `updatePublishedDocument` (with `formatPublishErrors` on failure); `GET :documentId/invoice-status` → `getDocumentInvoiceStatus` (eligibility and SB invoice state for UX).
- **ApiKeyGuard:** `PATCH :documentId/payment-status` → `updateDocumentPaymentStatus`; `POST manage-autopublish-supplier-category` → `manageAutoPublishForSupplierCategory`.
- **Related SB alignment (not user CRUD):** `POST webhook/cancel-from-sb`, `POST webhook/delete-from-sb` (`FrappeClientAuthGuard`) — keep documents aligned when SB cancels or deletes.

### Service (`document.service.ts`)

- **`publishDocument`:** Loads document and company; validates line items and supported doc types; resolves ledger (`publish_preference` or `company.ledger_type`, default Xero); default publishing values, tax sanitization, FX rates; `createInitialPublishEntry`; optional ML auto-reconciliation; **SleekBooks:** `createInvoice` with direct-transaction handling; **Xero:** `createInvoice` / `createBankTransaction` / `createCreditDebitNote` by `document_type`; sets status `PUBLISHING`, audit log, user activity, duplicate cleanup; on failure marks publish entry `FAILED`.
- **`bulkPublishDocuments`:** Batches of 10; expense-claim receipts → `claimReportService.addSingleReportItemRow`; else `publishDocument`; audit on failure.
- **`bulkUnpublishDocuments` / `processUnpublishDocument`:** Batches of 10; coordinates claim report unpublish where applicable.
- **`unPublishDocumentById`:** For `IN_BOOKS` (and expense-claim edge cases); `cancelLatestPublishEntry`; `cancelInvoiceAndRelatedEntry` (SleekBooks: cancel payment entry, journal entry, or `cancelTransaction` via `sleekbooksService`); resets document toward `PROCESSING`, events, audit.
- **`updatePublishedDocument`:** `getDocumentInvoiceStatus` must show eligible for updates (`ENABLE_UPDATE_PUBLISHED_DOCUMENT`, SB `docstatus` and unpaid/unreconciled rules); then `updateDocumentById(..., isPublishedDocument: true)` → `updatePublishedDocumentById` → `sleekbooksService.updateSubmittedInvoice` with merged amounts/line items.
- **`getDocumentInvoiceStatus`:** Reads last publish entry; if `publish_to === 'sb'` and `status === done`, fetches SB invoice or journal entry via `sleekbooksService` to compute `isPublishedDocumentEligibleForUpdates` and status fields.
- **`updateDocumentPaymentStatus`:** `findOneAndUpdate` with `payment_status` only (local document record).
- **`manageAutoPublishForSupplierCategory`:** Aggregation on `publish_entries` (last entry `done`), groups by company/supplier, last-two-documents same category heuristic; `supplierService.handleAutoPublishForSupplierCategoryRules`; optional `checkOnly` mode with counts.

### Schema

- **`document.schema.ts`:** Collection `documentdetailevents`; embeds `publish_entries` (see `publish-entry.schema`), status enums, `payment_status`, etc.

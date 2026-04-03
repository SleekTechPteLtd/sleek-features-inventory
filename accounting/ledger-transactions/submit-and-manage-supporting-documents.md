# Submit and manage supporting documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit and manage supporting documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Customer (uploads, status choices); Bookkeeper, Operations User (reject with comment, bulk status updates) |
| **Business Outcome** | Customers and finance users attach evidence to uncoded ledger lines, declare when documents were already shared or cannot be supplied, and staff can reject unacceptable submissions with feedback so bookkeeping stays auditable |
| **Entry Point / Surface** | Sleek App / customer and internal flows for uncoded ledger transactions; REST `ledger-transactions` API (`app-origin` header on relevant routes: `admin`, `customer`, `coding-engine`) |
| **Short Description** | Users upload a file for a ledger transaction, which stores a document link and moves the line to under review. Separate endpoints mark many lines as already shared or not available without a file. Staff can reject submissions in bulk with an optional comment (stored on the transaction and soft-deleting linked documents) when evidence is not acceptable |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Document upload pipeline (`DocumentService`: upload, metadata, optional Xero description); company and receipt-user resolution for upload payload; comments array on rejection; reconciliation and uncoded-queue views that read `document_upload_status` and `document_id` |
| **Service / Repository** | `acct-coding-engine` |
| **DB - Collections** | `ledger_transactions` (`document_upload_status`, `document_id`, embedded `comments` on rejection); `documentdetailevents` (uploaded file records, `is_deleted` on reject, `source` for submit origin) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `rejectLedgerTransactions` only allows rejection when `document_upload_status` is `uploaded` or `already_shared` (`ALLOWED_DOCUMENT_REJECT_STATUSES`), not `under_review`—confirm whether product expects rejection right after `submit-document` (which sets `under_review`). Exact app navigation labels per market |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `ledger-transaction.controller.ts` (`@Controller('ledger-transactions')`)

- **POST** `/:ledgerTransactionId/submit-document` — `submitDocument`; `FileInterceptor('document', multerOptions)`; `AuthGuard`, `CompanyAccessGuard`; query `company_id`, header `app-origin`; multipart field per `SubmitDocumentDto`; 400 if no file; delegates to `LedgerTransactionService.submitDocument`
- **POST** `/mark-already-submitted` — `updateDocumentStatusToAlreadyShared`; body `UpdateDocumentStatusRequestDto` (`ledgerTransactionIds`, `companyId`); sets `document_upload_status` to `already_shared`; `AuthGuard`, `CompanyAccessGuard`
- **POST** `/mark-document-declined` — `updateDocumentStatusToNotAvailable`; same body shape; sets `not_available`; `AuthGuard`, `CompanyAccessGuard`
- **POST** `/reject-submissions` — `rejectLedgerTransactions`; body `RejectSupportingDocumentRequestDto` (`ledgerTransactionIds`, `companyId`, optional `comment` max 4000 chars); optional query `isFromCustomerApp`; `AuthGuard`, `CompanyAccessGuard`; builds `userDetails` from JWT user

### `dto/submit-document.dto.ts`

- Swagger-only shape for multipart: `document` binary field (`SubmitDocumentDto`)

### `dto/ledger-action-request.dto.ts` (`RejectSupportingDocumentRequestDto`)

- `ledgerTransactionIds`: non-empty string array; `companyId`: required string; `comment`: optional string, max 4000

### `ledger-transaction.service.ts`

- **`submitDocument`:** Loads transaction by `ledger_transaction_id`; optional `companyId` must match `transaction.company_id` else `ForbiddenException`; `documentService.uploadDocuments` with payload from `createDocumentPayload` (company, receipt type from deposit/withdrawal, receipt user); sets document `source` via `getSubmitDocumentSource` (`ACCOUNTANT` if `app-origin` is coding-engine, else `SLEEK_MATCH`); `findOneAndUpdate` sets `document_id` and `document_upload_status` `under_review`; for Xero companies, `updateLinkedDocumentDescription` with formatted transaction description
- **`updateDocumentStatus`:** Bulk `updateMany` for `already_shared` or `not_available`; skips missing ids or rows already at target status; may return partial success or throw if none updatable
- **`rejectLedgerTransactions`:** Finds transactions; `processLedgerTransactionsForRejection` → `categorizeTransactions` / `isValidForRejection` (see constants); `updateLedgerTransactions` sets `rejected`, clears `document_id`, optional `$push` comment with `CommentSource` from `isFromCustomerApp`; `setDocumentToDeleted` soft-deletes linked docs via `documentService.updateDocuments` (`is_deleted: true`)

### `constants/ledger-transaction-constants.ts`

- `ALLOWED_DOCUMENT_REJECT_STATUSES`: `uploaded`, `already_shared` only

### `models/ledger-transaction.schema.ts`

- Collection `ledger_transactions`; fields `document_upload_status`, `document_id`, embedded `comments`

### `document/models/document.schema.ts`

- Collection `documentdetailevents` for stored uploads and lifecycle updates referenced by `submitDocument` and rejection

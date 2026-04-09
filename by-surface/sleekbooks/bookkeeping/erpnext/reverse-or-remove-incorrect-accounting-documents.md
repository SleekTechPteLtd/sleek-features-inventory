# Reverse or remove incorrect accounting documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reverse or remove incorrect accounting documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, integration services (M2M); cancel and bulk-cancel routes have no `M2MAuthGuard` in this controller—caller identity depends on upstream auth or network policy |
| **Business Outcome** | Lets operators and automated flows correct or remove wrong SleekBooks (ERPNext) postings when policy allows, including bulk cancellation by document type, while refusing destructive changes when a bank transaction is already reconciled. |
| **Entry Point / Surface** | Service API: `POST /erpnext/delete-doc`, `POST /erpnext/delete-doc/:docID/:docType`, `POST /erpnext/cancel-transaction`, `POST /erpnext/bulk-cancel-transactions` on **sleek-erpnext-service** (consumed by internal apps or integrations, not a single end-user screen in this repo). |
| **Short Description** | Deletes or cancels Frappe documents: direct delete/cancel-by-ID calls ERPNext `frappe.client.delete` and optionally `frappe.desk.form.save.cancel` when `shouldCancel=true`. Deletion by Sleek `transaction_id` loads the **Bank Transaction** by `transaction_id`, returns **406** if status is `Reconciled`, otherwise deletes. Bulk cancel posts `doctype`, `action: cancel`, and `docnames` to custom `sleek.api.submit_cancel_or_update_docs`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | ERPNext / Frappe (`baseURL`); custom app method `sleek.api.submit_cancel_or_update_docs`; related flows: bank reconciliation (`/unreconcile-bank-transaction`, `/revert-ce-reconciliation`) elsewhere in the same controller. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | None in this service; persistence is ERPNext/Frappe. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether global middleware or API gateway enforces auth for `/cancel-transaction` and `/bulk-cancel-transactions` (no `M2MAuthGuard` on those handlers); which client UIs or jobs call each route in production; whether `cancel-transaction`’s `transactionId` is always the ERPNext document `name` (it is passed straight to Frappe cancel, unlike `delete-doc` which resolves `Bank Transaction` by `transaction_id` field). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/erpnext/erpnext.controller.ts`)

- **`POST /erpnext/delete-doc/:docID/:docType`** — `@UseGuards(M2MAuthGuard)`; `@ApiOperation` “delete SB document entry by ID and Type”; calls `deleteDocumentEntryByIDandType(docID, docType, query?.shouldCancel)`.
- **`POST /erpnext/delete-doc`** — `@UseGuards(M2MAuthGuard)`; body `transactionId`; `getTransactionsById(transactionId)`; if missing → **404**; if `status === 'Reconciled'` → **406** “Transaction already reconciled successfully”; else `deleteDocumentEntryByIDandType(transaction?.name, null, query?.shouldCancel)`.
- **`POST /erpnext/cancel-transaction`** — body `CancelTransactionPayload` (`transactionId`, `docType`); `cancelTransaction(transactionId, docType)`; no M2M guard on this handler.
- **`POST /erpnext/bulk-cancel-transactions`** — body `BulkCancelTransactionsPayload` (`docType`, `docNames`); `bulkCancelTransactionByDocType(docType, docNames)`; no M2M guard on this handler.

### Service (`src/erpnext/erpnext.service.ts`)

- **`cancelTransaction(name, type)`** — `POST api/method/frappe.desk.form.save.cancel` with `{ doctype: type, name: name }`.
- **`bulkCancelTransactionByDocType(docType, docNames)`** — `POST /api/method/sleek.api.submit_cancel_or_update_docs` with `FormData`: `doctype`, `action: 'cancel'`, `docnames` JSON array.
- **`getTransactionsById(transactionId)`** — `GET api/resource/Bank Transaction` with filters `[["transaction_id", "=", transactionId]]`; returns first row.
- **`deleteDocumentEntryByIDandType(docID, docType, shouldCancel)`** — defaults `documentType` to `TRANSACTION_TYPES.bank` (`Bank Transaction`) when `docType` is null; if `shouldCancel === 'true'`, calls `cancelTransaction` first; then `POST api/method/frappe.client.delete` with `{ doctype, name: docID }`.

### Types (`src/erpnext/interface/erpnext.interface.ts`)

- **`CancelTransactionPayload`:** `transactionId`, `docType`.
- **`BulkCancelTransactionsPayload`:** `docType`, `docNames: string[]`.

### Constants (`src/erpnext/erpnext.constants.ts`)

- **`TRANSACTION_TYPES.bank`:** `'Bank Transaction'` (default doctype when deleting by transaction flow with `docType` null).

# Sync document lifecycle from SleekBooks webhooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync document lifecycle from SleekBooks webhooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | After a document has been published to SleekBooks, local records stay aligned when the corresponding invoice is cancelled or removed in SleekBooks—avoiding stale active documents and preserving an audit trail. |
| **Entry Point / Surface** | Server-to-server integration: `POST /document/webhook/cancel-from-sb` and `POST /document/webhook/delete-from-sb` (Frappe/SleekBooks webhook callers; not an end-user app screen). |
| **Short Description** | Signed webhooks receive cancel or delete events from the external bookkeeping flow. The service resolves the matching Coding Engine document (published to SleekBooks with a matching invoice id), applies archive or soft-delete updates in MongoDB, and emits structured audit entries to Sleek Auditor. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on SleekBooks publish flow (`publish_entries` with `SLEEKBOOKS` and `DONE` status); `SleekAuditorService.insertLogsToSleekAuditor` for audit; `FrappeClientAuthGuard` + `FRAPPE_WEBHOOK_SECRET` for authentication. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | documentdetailevents |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `extraction_id` is optional in `BaseSBWebhookDto`; when omitted, matching relies only on `publish_entries` matching `invoice_id` to `name`—confirm whether production webhooks always send a valid Coding Engine id. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/document/document.controller.ts`: `POST document/webhook/cancel-from-sb` → `handleCancelDocumentWebhookFromSB` (`FrappeClientAuthGuard`, `ValidationPipe`, Swagger header `HEADERS.FRAPPE_WEBHOOK_SIGNATURE`); `POST document/webhook/delete-from-sb` → `handleDeleteDocumentWebhookFromSB` (same guard and header).
- **DTOs** — `src/document/dto/sb-webhook.dto.ts`: `BaseSBWebhookDto` with optional `extraction_id`, `modified`, `modified_by`, `name`; `CancelFromSBWebhookDto` / `DeleteFromSBWebhookDto` extend the base.
- **Auth** — `src/common/auth/frappe-client-auth.guard.ts`: requires header `x-frappe-webhook-signature` to equal `process.env.FRAPPE_WEBHOOK_SECRET`.
- **Service** — `src/document/document.service.ts`:
  - `handleDeleteDocumentWebhookFromSB`: `findOneAndUpdate` with filter `is_deleted` not true; `$set` `is_deleted: true`, `is_duplicated: false`, `$unset` `duplicated_documents`; audit event `Document Deletion from SleekBooks`.
  - `handleCancelDocumentWebhookFromSB`: filter `is_archived` not true; `$set` `is_archived: true`; audit event `Document Cancellation from SleekBooks`.
  - `processDocumentWebhookAction`: shared path; `sleekAuditorService.insertLogsToSleekAuditor` on success; returns `DocumentWebhookResult` with `success`, `message`, `documentId`, `invoiceId`.
  - `buildQueryCondition`: requires `publish_entries` `$elemMatch` with `invoice_id` = webhook `name`, `publish_to: CompanyLedgerType.SLEEKBOOKS`, `status: PublishStatus.DONE`; if `extraction_id` is a valid ObjectId, also constrains `_id`.
- **Schema** — `src/document/models/document.schema.ts`: MongoDB collection `documentdetailevents`.

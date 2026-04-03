# Remove or request removal of documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Remove or request removal of documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User |
| **Business Outcome** | Users can clear unwanted or mistaken receipt documents from their working set, or—when policy requires—notify accounting (and optionally Zendesk) so removal can be coordinated with Xero or Dext. |
| **Entry Point / Surface** | Client surfaces that call `sleek-receipts` document-event APIs with shared service auth (e.g. Sleek App bookkeeping / receipt document lists aligned with `getAllDocumentEventsByCompanyId` usage). |
| **Short Description** | Bulk **delete** soft-marks documents (`is_deleted`, clears archive) with audit logging and a Kafka bulk-deleted event. Bulk **request delete** flags `is_request_delete`, stores structured `delete_request` (requester, reason per id, pending status), notifies the accountant via Zendesk ticket or email depending on `isCreateZendeskTicket`, writes audit logs, and publishes per-document Kafka updates. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Kafka (`BULK_DOCUMENT_DELETED`, `DOCUMENT_UPDATED`); optional Zendesk integration via `SLEEK_ZENDESK_BASE_URL` and app feature `new_enquiry_page` (category mapping); transactional email (`REQUEST_DELETE_EMAIL`); `EmailForwarder.sendGenericEmail`; company resource users for routing; list filtering via `isRequestDelete` / `isDeleted` on company document queries. |
| **Service / Repository** | sleek-receipts |
| **DB - Collections** | `documentdetailevents` (`DocumentDetailEvent`); `auditlogs` (`AuditLog` for `delete` and `request_delete` actions). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which client toggles `isCreateZendeskTicket` vs email-only path in production; exact Sleek App navigation strings for bulk actions. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP routes (`src/routes/document-event.js`)

- **`PUT /document-events/actions/delete`** → `documentEventController.deleteMultipleDocumentEventDetails` — body: `ids`, `userid` (see controller spelling).
- **`PUT /document-events/actions/request-delete`** → `documentEventController.requestDeleteMultipleDocumentEventDetails` — body: `ids`, `userId`, `companyResourceUsers`, `userDetails`, optional `isCreateZendeskTicket` (default `false`), optional `reasons` map keyed by document id.

### Auth (`src/middleware/document-event-middleware.js`)

- **`validateDocumentEventAuth`:** requires `Authorization` header equal to `process.env.SLEEK_RECEIPTS_TOKEN` (service-to-service style gate, not end-user JWT in this file).

### Controller (`src/controllers/document-event-controller.js`)

- **`deleteMultipleDocumentEventDetails`:** reads `body.ids`, `body.userid`, calls `documentEventService.deleteMultipleDocumentEventDetails(ids, userId)`.
- **`requestDeleteMultipleDocumentEventDetails`:** reads ids, `userId`, `companyResourceUsers`, `userDetails`, `isCreateZendeskTicket`, `reasons`; success via `SUCCESS_CODES.DOCUMENT_EVENT_CODES.REQUEST_DELETE_DOCUMENT`.

### Service (`src/services/document-event-service.js`)

- **`deleteMultipleDocumentEventDetails(ids, userId)`:** validates ObjectIds; `auditLogEvent.createAuditLog` with `action: "delete"`; `DocumentDetailEvent.updateMany` sets `is_deleted: true`, `is_archived: false`; `KafkaService.publishEvent(DocumentEventType.BULK_DOCUMENT_DELETED, …)`.
- **`requestDeleteMultipleDocumentEventDetails(…)`:** loads documents by ids; per document either `createTicketInZendesk(companyResourceUsers, data, userDetails)` or `EmailForwarder.sendGenericEmail` with `config.mailer.templates.REQUEST_DELETE_EMAIL` to first company resource user email; `createAuditLog` with `action: "request_delete"`; `DocumentDetailEvent.bulkWrite` sets `is_request_delete: true` and nested `delete_request` (request date, requester name/email, `status: 'pending'`, `request_reason` from `reasons[id]`); per id `KafkaService.publishEvent(DocumentEventType.DOCUMENT_UPDATED, …)`.
- **`getAllDocumentEventsByCompanyId`:** query flags `isDeleted` and `isRequestDelete` (`'true'`) filter `is_deleted` / `is_request_delete` for list UX.

### Zendesk (`src/services/sleek-zendesk-service.js`)

- **`createTicketInZendesk`:** skips companies whose name starts with `Autotestcom`; loads `new_enquiry_page` app feature for `category_resource_mapping`; builds HTML body with document id, submission date, status label, Xero vs Dext hint; `axios.post` to ``${process.env.SLEEK_ZENDESK_BASE_URL}/zendesk/delete-request`` with tags including `request_deleted`.

### Schema (`src/schemas/document-detail-event.js`)

- **Fields:** `is_deleted`, `is_request_delete`, `delete_request` (object, default `{}`).

### Related (not expanded here)

- **`src/audit-logs/creator.js`:** persists `AuditLog` with `user_id`, `document_ids`, `action`.

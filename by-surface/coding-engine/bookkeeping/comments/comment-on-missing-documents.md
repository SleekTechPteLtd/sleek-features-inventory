# Comment on missing documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Comment on missing documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (end user submitting context on a missing receipt) |
| **Business Outcome** | Accounting is notified by email when someone adds context to a missing-receipt case, and the comment is persisted for bookkeeping follow-up |
| **Entry Point / Surface** | Client flows that collect a comment against a missing-document record; `sleek-receipts` REST `POST /api/comment` (exact in-app navigation path not determined from this service alone) |
| **Short Description** | Users submit a comment linked to a missing-document (missing receipt) record. The service validates the missing document exists, stores the comment with company and receipt metadata, and sends a transactional email (`notify_save_comment`) to accounting with amount and transaction description from the missing-document row |
| **Variants / Markets** | SG (default notification emails use `accounting@sleek.sg` and a `@sleek.com` CC; not shown as market-configurable in code) |
| **Dependencies / Related Flows** | Missing document lifecycle (`missing-document-service`, `MissingDocument` records); outbound email via `mailer` (`EmailSender.sendEmail`); optional linkage to `document_event_id` on stored comments for broader receipt/document-event context |
| **Service / Repository** | `sleek-receipts` (`comments-controller.js`, `comments-service.js`, `schemas/comments.js`, `routes/comments.js`) |
| **DB - Collections** | `comments` (mongoose model `Comment`); reads `missingdocuments` via `MissingDocument.findById` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `validateDocumentEventAuth` is imported but commented out on `POST /comment`—whether the route is intentionally open, protected elsewhere (gateway), or should match other `/api/*` document-event routes. Whether notification recipients should be environment- or company-specific instead of hardcoded |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `routes/comments.js`

- `POST /comment` (mounted under `/api` in `routes.js` → **`POST /api/comment`**) — `commentsController.create`; `validateDocumentEventAuth` is **not** applied (commented out), unlike `missing-document` routes that use the shared token guard

### `controllers/comments-controller.js`

- `create` — reads body, calls `commentsService.saveComment`, returns `COMMENT_CODES.CREATE` (`CREATE_COMMENT_SUCCESS`)

### `services/comments-service.js`

- `saveComment` — requires `missing_document_id`; loads row via `getMissingDocumentById`; throws `MISSING_DOCUMENT_CODES.INVALID_QUERY` when missing or invalid
- After `Comments.create(restData)`, sends email via `sendEmail` → `EmailSender.sendEmail` with `templateId: "notify_save_comment"`, default `to`/`cc` from `EMAIL_CONFIG`, optional overrides from `options.to`, `options.fromEmail`, `commentData.cc`
- Template variables: `company_name`, `amount` (from `missingDocument.spent`), `comment`, `transaction_description`, `subject`

### `schemas/comments.js`

- Model `Comment`: `receipt_user`, `receipt_email`, `company`, `comment`, `missing_document_id`, `document_event_id`, `attachments`, `source`, `is_deleted`, timestamps

### `services/missing-document-service.js` (supporting)

- `getMissingDocumentById` — `MissingDocument.findById` after ObjectId validation

### `schemas/missing-document.js` (supporting)

- Model `MissingDocument`: company, amounts, `transaction_description`, `document_events`, `status`, etc.

### `middleware/document-event-middleware.js` (contrast)

- `validateDocumentEventAuth` — compares `Authorization` header to `process.env.SLEEK_RECEIPTS_TOKEN`; used on other receipt API routes but not on comments route as committed

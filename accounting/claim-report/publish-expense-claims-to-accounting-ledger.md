# Publish expense claims to the accounting ledger

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Publish expense claims to the accounting ledger |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Bookkeeper (reviewer confirms); Claimant receives notification after publish |
| **Business Outcome** | Approved expense claim lines become purchase invoices in the company’s connected ledger (SleekBooks or Xero) with traceability and claimant communication. |
| **Entry Point / Surface** | Sleek App > Bookkeeping > Expense claim (`/bookkeeping/expense-claim/:reportId`); API `POST /claim-report/:reportId/confirm` and `POST /claim-report/:reportId/publish` (acct-coding-engine) |
| **Short Description** | Reviewers confirm a report (`confirm`), moving it toward publication; publishing (`createInvoice`) builds a purchase-invoice payload from approved line items, posts to SleekBooks or Xero depending on `company.ledger_type`, records Sleek Auditor entries per document, updates document publish metadata and events, and emails the claimant using the expense-claim approval template. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Company ledger type (`SleekBooks` / `Xero`); `SleekbooksService.createECInvoice`, `XeroService.createECInvoice`; document `publish_entries` and bulk document events; `ECReportEventType` updates; Sleek Auditor; Mailer (`EC_APPROVE_EMAIL`); optional claimant resolution via SleekBack when not supplied in body |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `claimreports` (Coding Engine connection); `companies` (Coding Engine); `documents` (Sleek Receipts connection — `publish_entries`, `last_published_on`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact product markets/variants for Xero line-item vs legacy payload (`enableNewECPublishingLineItems`, `isCountryNotSupported`) should be confirmed with product; UI copy for confirm vs publish order may live in customer-mfe — not verified here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Status model

- `ClaimReportStatus`: `new`, `toreview`, `publishing`, `approved`, `rejected`, `completed`, `error` — `src/claim-report/enum/claim-report.enum.ts`.

### HTTP surface (`src/claim-report/claim-report.controller.ts`)

- `POST :reportId/publish` — `AuthGuard` — `ClaimReportService.createInvoice` (publishes to ledger).
- `POST :reportId/confirm` — `AuthGuard` — `ClaimReportService.confirmECReport` (reviewer confirmation; sets status to `publishing` or `rejected` when all items rejected).
- `DELETE :reportId/unpublish` and `DELETE :reportId/:documentId/unpublish` — rollback / unlink flows (related to published state).

### Publishing pipeline (`src/claim-report/claim-report.service.ts`)

- **`confirmECReport`**: Only from `NEW` or `TOREVIEW`; archives rejected documents; may set status to `REJECTED` (all lines rejected) or `PUBLISHING`; emits `ECReportEventType.UPDATED` via `eventUtils.publishEvent`.
- **`createInvoice`**: Validates company UEN and `ledger_type`; resolves claimant (`receiptUser` from body or `getReceiptUserFromSleekBack`); **`createInitialPublishEntry`** pushes `publish_entries` on approved documents (`purchase_invoice`, `EXPENSE_CLAIM`), sets `last_published_on`, fires bulk document events.
- **Ledger posting**: `company.ledger_type === SLEEKBOOKS` → `sleekbooksService.createECInvoice`; `XERO` → `xeroService.createECInvoice` (with supplier validation for Xero).
- **Payload**: `getLedgerInvoicePayload` — approved items only (`is_approved`); Xero path can attach tax line detail when feature flags allow.
- **After success**: May adjust report `end_date` (early-approval / self-heal logic); `createAuditLogsForECReportPublishing` → `sleekAuditorService.insertLogsToSleekAuditor` per approved item (success or error path).
- **Notification**: `sendNotificationToUser` with `EMAIL_TEMPLATES.EXPENSE_CLAIM.EC_APPROVE_EMAIL`, link built from `SLEEK_WEBSITE_BASE_URL` + `/bookkeeping/expense-claim/:reportId`.

### Module wiring (`src/claim-report/claim-report.module.ts`)

- Injects `SleekbooksService`, `XeroService`, `SleekAuditorService`, `MailerService`, `SleekBackService`, document/company models across `CODING_ENGINE` and `SLEEK_RECEIPTS` connections.

### Schema

- `src/claim-report/models/claim-report.schema.ts` — `ClaimReport.status` enum-aligned; `report_items` hold approval and amounts used for invoice lines.

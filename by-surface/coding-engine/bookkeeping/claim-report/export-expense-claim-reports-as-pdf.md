# Export expense claim reports as PDF

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Export expense claim reports as PDF |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User (authenticated); recipient of the file acts as stakeholder for reimbursement or records |
| **Business Outcome** | Stakeholders obtain a single, printable expense claim summary with claimant identity, line-level detail, and reimbursement totals for approval workflows, payment, and audit retention. |
| **Entry Point / Surface** | Coding engine REST API `POST /claim-report/:reportId/export` with `AuthGuard`; consumer (e.g. Sleek App > Bookkeeping / expense claims) triggers download — exact UI path not defined in this repo |
| **Short Description** | Loads the claim report and company, resolves the claimant display name (from request body or SleekBack), recomputes totals, builds a landscape A4 PDF via pdfmake (`generateClaimReportPDF`), and streams it as an attachment with the report title as filename. The PDF includes header branding, report metadata (dates, report ID link to Sleek web, submitter, currency), a table of line items (doc ID with link to document details, supplier, category, reason, amount, approval status), subtotals for review and amount to be paid, and optional signature blocks when the report is not yet completed/publishing. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Depends on persisted claim report data and line items; `companies` (requires `uen`); SleekBack `getReceiptUserFromSleekBack` when `receiptUser` is not supplied in body; links in PDF use `SLEEK_WEBSITE_BASE_URL`; related: manage/publish/confirm expense claim reports in the same module |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | claimreports, companies |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`claim-report.controller.ts`:** `POST ':reportId/export'` — `exportReport` — `@UseGuards(AuthGuard)`; passes `reportId`, `ClaimReportBodyDTO` body, and Express `res` for streaming.
- **`claim-report.service.ts` — `exportReport`:**
  - `claimReportModel.findById(reportId)`; error if missing.
  - Recalculates `total_amount` from `report_items` via `calculateTotalAmount` when items exist.
  - Loads company by `company_id`; throws if company missing or no `uen`.
  - Claimant name: `claimReportBody.receiptUser` (with `emails`) if present, else `getReceiptUserFromSleekBack(companyId, report.claim_user)`.
  - `total_to_be_paid` from `calculateTotalAmountToBePaid(report.report_items)`.
  - Payload: spread report document, `claim_username` (full name), `total_to_be_paid`.
  - `generateClaimReportPDF(payload)` → PDFKit document; `Content-Type: application/pdf`, `Content-Disposition: attachment` with `report_title` as filename; `doc.pipe(res)` / `doc.end()`.
- **`utils/claim-report.ts` — `generateClaimReportPDF`:** pdfmake `PdfPrinter` with shared fonts; landscape A4; `generateContent` builds title (“Expense Claim Report for {user} from … to …” with CJK-safe text), company block (report date, linked report ID, submitter, currency), item table (`REPORT_ITEMS_HEADER`: DOC ID, SUPPLIER, CATEGORY, REASON, TOTAL, STATUS), rows with links to document and expense-claim URLs, `Total to be reviewed` / `Total to be paid`, empty state message, signature section when status is not `COMPLETED` or `PUBLISHING`; header SVG logo; footer page numbers.
- **`claim-report.schema.ts`:** `ClaimReport` fields consumed indirectly via stored report (`report_title`, `start_date`, `end_date`, `currency`, `total_amount`, `status`, `report_items`, `claim_user`, `_id`).

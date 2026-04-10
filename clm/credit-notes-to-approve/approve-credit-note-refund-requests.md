# Approve Credit Note Refund Requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Approve Credit Note Refund Requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance Operations User (Billing Operations Admin group) |
| **Business Outcome** | Enables authorised billing admins to review, approve, or reject pending customer refund requests before they are executed in Xero — ensuring a controlled, two-step approval gate for all credit note disbursements. |
| **Entry Point / Surface** | Sleek Billings App > Refunds > CN (Approval) (`/credit-notes-to-approve`) |
| **Short Description** | Displays a paginated, searchable queue of draft credit notes awaiting approval, with working-days-lapsed tracking per request. Billing Operations Admins can approve (triggering Xero credit note generation and refund processing) or reject (voiding the credit note with a mandatory reason). Both actions are permission-gated to the `BillingSuperAdmin` or `BillingOperationsAdmin` group. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Credit Note Payment queue (`/credit-notes-to-pay`, downstream after approval); Xero (credit note generated on approve via `xeroService.updateOrCreateCreditNote`; voided on reject if `externalId` exists); Linked invoice (via `linkedInvoice.externalUrl`); Zendesk support ticket (`zendeskUrl`); Admin app company overview (`/admin/company-overview`) for request form review; `sleek-back` permission API (`/users/is-member`) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend, sleek-back (permission check) |
| **DB - Collections** | `invoices` (MongoDB, SleekPaymentDB) — filtered by `type=creditNote, status=draft, migratedFrom=null`; `items[].creditNoteData` sub-documents; `companyDetails` embedded |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Which markets/jurisdictions does this queue cover — SG, HK, AU, UK, or all? (2) Is there an SLA target for the working-days-lapsed counter (e.g., escalation at N days)? (3) The `migratedFrom: null` filter excludes migrated credit notes — is there a separate approval flow for those? (4) For the $0 cash refund special case, what downstream subscription changes are triggered on approve? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/App.jsx:186` — `<Route path="credit-notes-to-approve" element={<CreditNotesToApprove />} />`
- `src/components/Navbar.jsx:125` — nav item label "CN (Approval)", path `/credit-notes-to-approve`
- `src/data/nav-rail-items.js:61–63` — nested under "Refunds" rail section, label "Credit Notes (Approval)"
- `src/pages/Home.jsx:52` — home page card: "Review and approve credit note requests"

### Data fetching
- `src/pages/Refunds/CreditNotesToApprove.jsx:34–61` — `sleekBillingsApi.getInvoices({ page, limit: 100, populateLinkedInvoice: true, filter: { type: 'creditNote', status: 'draft', migratedFrom: null, [optional $or search on number/title] } })`
- `src/services/api.js:169–177` — `GET /invoices/?<queryParams>` via `sleekBillingsApi`
- Backend: `invoice.controller.ts:49–54` — `@Get('') @Auth()` → `invoiceService.getInvoiceList(params)`

### Permission gate (frontend)
- `src/pages/Refunds/CreditNotesToApprove.jsx:67–77` — calls `sleekBackApi.isMember({ group_name: 'Billing Operations Admin' })` on mount
- `src/services/sleek-back-api.js` — `GET /users/is-member?group_name=...` on `SLEEK_BACK_API_URL`
- `src/lib/constants.jsx` — `SLEEK_GROUP_NAMES.BILLING_OPERATIONS_ADMIN = "Billing Operations Admin"`
- Users without this group see a modal: "You do not have access to submit credit notes."

### Permission gate (backend)
- `invoice.controller.ts:230–235` — `@Post('credit-note/:id/approve') @Auth() @GroupAuth(Group.BillingSuperAdmin, Group.BillingOperationsAdmin)` — server-side enforcement on top of frontend check

### Working-days-lapsed calculation
- `src/pages/Refunds/CreditNotesToApprove.jsx:117–147` — client-side, counts Mon–Fri days between `note.createdAt` and today (UTC-normalised); displays "Today" or "N day(s)"

### Actions

**Approve** — `sleekBillingsApi.approveCreditNote(id)` → `POST /invoices/credit-note/:id/approve`
- `src/services/api.js:319–327` (frontend call)
- `invoice.controller.ts:230–235` (backend route)
- `invoice.service.ts:2701–2756` (`approveCreditNote`):
  1. Finds credit note by `_id`, asserts `status=draft` and `type=creditNote`
  2. Initialises Xero (`xeroService.init`) and calls `xeroService.updateOrCreateCreditNote` to create the credit note in Xero
  3. Updates DB record with `externalId`, `externalNumber`, `number`, `status` (mapped from Xero status), `submittedBy`, `issueDate`, `expireAt`
  4. Writes audit log entry
- Special case: if `totalCashRefund === 0` and credit balance fully covers the refund, frontend warns the note will be $0 and auto-marked as Credited in Xero, triggering subscription changes and refund notifications immediately

**Reject** — `sleekBillingsApi.voidInvoice(id, { voidReason })` → `POST /invoices/:id/void`
- `src/services/api.js:328–336` (frontend call); requires non-empty `voidReason`
- `invoice.controller.ts:206–212` (backend route, `@Auth()` only — no group guard on void)
- `invoice.service.ts:2403–~2470` (`voidInvoice`): validates status (rejects paid/voided/deleted); if `externalId` exists, voids credit note in Xero first; updates DB status to `voided`

**View Request Form** — opens `VITE_ADMIN_APP_URL/admin/company-overview/?cid=...&activeCreditNote=...&tab=1` in a new tab for pre-decision context review.

### Table columns surfaced to user
`#`, Date Raised (`createdAt`), Working Days Lapsed, Requester (`createdBy.email`), Company Name (`companyDetails.name`), Invoice Number (links to `linkedInvoice.externalUrl`), Subscriptions Refunding (`items[].name`), Reason for Refund (`items[].creditNoteData.reasonForRefund`), Additional Details (`items[].creditNoteData.reasonAdditionalDetails`), ZD Ticket Link (`zendeskUrl`), Actions

### Pagination
- 100 items per page; MUI `<Pagination>` component; page state reset on search.

### MongoDB collection
- Collection name `invoices` confirmed via `invoice.service.spec.ts:510` (`$lookup.from: 'invoices'`) and `MongooseModule.forFeature([{ name: Invoice.name, schema: InvoiceSchema }], SleekPaymentDB)`

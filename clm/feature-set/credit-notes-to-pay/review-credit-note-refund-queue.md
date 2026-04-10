# Review Credit Note Refund Queue

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Credit Note Refund Queue |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance Operations User (Billing Operations Admin group) |
| **Business Outcome** | Enables finance ops staff to efficiently process customer refunds by surfacing all approved credit notes awaiting disbursement in a prioritised, searchable queue — reducing delays and ensuring SLA-aware handling via working-days-lapsed tracking. |
| **Entry Point / Surface** | Sleek Billings App > Refunds > CN (Payment) (`/credit-notes-to-pay`) |
| **Short Description** | Displays a paginated, searchable list of authorised credit notes (type=creditNote, status=authorised, not migrated) with working-days-elapsed since submission. Finance admins can mark a credit note as paid (disbursement confirmed) or reject/void it with a mandatory reason. Both actions are gated to the "Billing Operations Admin" group. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Credit Note Approval queue (`/credit-notes-to-approve`); Xero credit note record (deep-link via `externalId`); Linked invoice (via `linkedInvoice.externalUrl`); Zendesk support ticket (`zendeskUrl`); Admin app company overview (`/admin/company-overview`) for request form review; `sleek-back` permission API (`/users/is-member`) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-api (via `sleekBillingsApi`), sleek-back (via `sleekBackApi`) |
| **DB - Collections** | Unknown — API surfaces `invoices` collection (queried via `GET /invoices/` with filter `type=creditNote, status=authorised`); `companyDetails` embedded; `items[].creditNoteData` sub-documents |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Which markets/jurisdictions does this queue cover — SG, HK, AU, UK, or all? (2) Is there an SLA target for the working-days-lapsed counter (e.g., escalation at N days)? (3) The `migratedFrom: null` filter excludes migrated credit notes — is there a separate flow for those? (4) The `markCreditNoteAsPaid` action (`PUT /invoices/credit-note/:id/mark-as-paid`) — does it trigger a downstream payment disbursement or only update status after manual bank transfer? (5) `DB - Collections` column lists Unknown because the frontend calls the API; the backend collection name needs verification. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `src/App.jsx:185` — `<Route path="credit-notes-to-pay" element={<CreditNotesToPay />} />`
- `src/components/Navbar.jsx:126` — nav item label "CN (Payment)", path `/credit-notes-to-pay`
- `src/data/nav-rail-items.js:48,68` — nested under "Refunds" rail section

### Data fetching
- `src/pages/Refunds/CreditNotesToPay.jsx:36–51` — `sleekBillingsApi.getInvoices({ page, limit: 100, populateLinkedInvoice: true, filter: { type: 'creditNote', status: 'authorised', migratedFrom: null, [optional $or search on number/title] } })`
- `src/services/api.js:169–178` — `GET /invoices/?<queryParams>` via `sleekBillingsApi`

### Permission gate
- `src/pages/Refunds/CreditNotesToPay.jsx:66–76` — calls `sleekBackApi.isMember({ group_name: 'Billing Operations Admin' })`
- `src/services/sleek-back-api.js:58–71` — `GET /users/is-member?group_name=...` on `SLEEK_BACK_API_URL`
- `src/lib/constants.jsx:400` — `SLEEK_GROUP_NAMES.BILLING_OPERATIONS_ADMIN = "Billing Operations Admin"`
- Users without this group see a modal: "You do not have access to submit credit notes."

### Working-days-lapsed calculation
- `src/pages/Refunds/CreditNotesToPay.jsx:116–146` — client-side, counts Mon–Fri days between `note.issueDate` and today (UTC-normalised); displays "Today" or "N day(s)"

### Actions
- **Mark as Paid** — `sleekBillingsApi.markCreditNoteAsPaid(id)` → `PUT /invoices/credit-note/:id/mark-as-paid` (`src/services/api.js:337–345`). Confirmation modal warns action is irreversible.
- **Reject** — `sleekBillingsApi.voidInvoice(id, { voidReason })` → `POST /invoices/:id/void` (`src/services/api.js:328–336`). Requires non-empty reason; voids the credit note and cancels the refund process.
- **View Request Form** — opens `VITE_ADMIN_APP_URL/admin/company-overview/?cid=...&activeCreditNote=...&tab=1` in a new tab for context review.

### Table columns surfaced to user
`#`, Date Submitted, Working Days Lapsed, Requester (createdBy.email), Approver (submittedBy.email), Company Name (companyDetails.name), Credit Note # (links to Xero), Invoice # (links to external URL), Subscriptions Refunding (items[].name), Reason for Refund (items[].creditNoteData.reasonForRefund), Additional Details (items[].creditNoteData.reasonAdditionalDetails), ZD Ticket Link (zendeskUrl), Actions

### Pagination
- 100 items per page; MUI `<Pagination>` component; client-driven page state reset on search.

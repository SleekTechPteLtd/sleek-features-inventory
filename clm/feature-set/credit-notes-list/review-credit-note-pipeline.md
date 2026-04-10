# Review Credit Note Pipeline

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Credit Note Pipeline |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance Operations User (Billing Operations team) |
| **Business Outcome** | Gives operators a single searchable view of every credit note across all companies so they can monitor where each refund sits in the approval and credit lifecycle without navigating per-company. |
| **Entry Point / Surface** | Sleek Billings Admin > Refunds > CN (List) (`/credit-notes-list`) |
| **Short Description** | Displays a paginated, searchable table of all credit notes with key lifecycle dates (requested, approved/rejected, credited) and their current status (Draft, Approved, Credited, Voided). Each row links out to the company's billing overview in the main Admin app to drill into the underlying refund request. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | CN (Approval) — `CreditNotesToApprove.jsx` at `/credit-notes-to-approve` (approve/reject step); CN (Payment) — `CreditNotesToPay.jsx` at `/credit-notes-to-pay` (mark-as-paid step); Sleek Admin app company overview (`VITE_ADMIN_APP_URL/admin/company-overview`) for per-credit-note drill-down |
| **Service / Repository** | sleek-billings-frontend; sleek-billings (backend, inferred from `/invoices/` API) |
| **DB - Collections** | Unknown (frontend only; backend collections not visible from this layer) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/regions are credit notes available for (SG/HK/UK/AU)? What backend service owns the `/invoices/` endpoint? Is this view accessible to all Billing Ops users or restricted to a specific role/group (unlike `CreditNotesToApprove` which checks `SLEEK_GROUP_NAMES` membership)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### File
`src/pages/Refunds/CreditNotesList.jsx`

### API call
`sleekBillingsApi.getInvoices()` → `GET /invoices/?page=N&limit=100&populateLinkedInvoice=true&filter=...`

Filter shape:
```json
{
  "type": "creditNote",
  "migratedFrom": null,
  "$or": [
    { "number": { "$regex": "<query>", "$options": "i" } },
    { "title": { "$regex": "<query>", "$options": "i" } },
    { "createdBy.email": { "$regex": "<query>", "$options": "i" } }
  ]
}
```
(`$or` clause only present when a search query is active)

### Table columns rendered
| Column | Source field |
|---|---|
| # | row index + page offset |
| Requester (email) | `note.createdBy.email` |
| Date requested | `note.createdAt` |
| Date Approved/Rejected | `note.issueDate` (or `note.updatedAt` when status is `voided`) |
| Date credited | `note.paidAt` |
| Company Name | `note.companyDetails.name` (links to Admin app company overview) |
| Invoice Number | `note.linkedInvoice.number` (links to `linkedInvoice.externalUrl`) |
| Credit Note Number | `note.number` |
| Request Status | `note.status` — badge colours: Draft=yellow, Approved=green, Credited=blue, default=gray |
| View Refund Request | Opens Admin app at `…/company-overview/?cid=…&currentPage=Billing+Beta&activeCreditNote=…&tab=1` |

### Status lifecycle visible in this view
`draft` → `approved` → `credited` (or `voided` at the approval step)

### Related API methods (defined in `src/services/api.js`)
- `approveCreditNote(id)` → `POST invoices/credit-note/:id/approve`
- `voidInvoice(id, data)` → `POST invoices/:id/void`
- `markCreditNoteAsPaid(id)` → `PUT invoices/credit-note/:id/mark-as-paid`

These are used by the sibling Approval and Payment screens, confirming this list view is the read-only monitoring layer for the same pipeline.

### Routing (`src/App.jsx`)
```jsx
<Route path="credit-notes-list" element={<CreditNotesList />} />
```

### Navigation label (`src/pages/Home.jsx`)
Section: **Refunds** — item label `CN (List)`, description `View all credit notes`

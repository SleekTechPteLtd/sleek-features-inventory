# Process Credit Note Refund

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Process Credit Note Refund |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Billing Operations Admin |
| **Business Outcome** | Enables ops admins to complete the subscription refund lifecycle by confirming payment disbursement or cancelling the refund with a recorded reason, ensuring every authorised credit note is either closed as paid or voided with an audit trail. |
| **Entry Point / Surface** | Sleek Billings Admin > Finance Dashboard > Refunds > CN (Payment) (`/credit-notes-to-pay`) |
| **Short Description** | Lists all authorised credit notes awaiting disbursement (paginated, searchable by number or title). Admins mark a credit note as paid (after funds are disbursed) to finalise the refund, or reject it with a mandatory reason which voids the credit note in Xero and cancels the refund process. Both actions are gated to the Billing Operations Admin group. |
| **Variants / Markets** | Unknown — currency symbol is read from localStorage at runtime; Xero dependency implies markets where Xero is the accounting system (likely SG, HK) |
| **Dependencies / Related Flows** | Upstream: credit note approval flow (`/credit-notes-to-approve`); Xero (credit note record via `externalId`, deep-link to `go.xero.com`); Zendesk (support ticket link per row); Stripe (payment processing on backend); sleek-back-api (Billing Operations Admin permission check via `GET /users/is-member`) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend, sleek-back-api |
| **DB - Collections** | `invoices` (SleekPaymentDB — filtered by `type=creditNote`, `status=authorised`, `migratedFrom=null`); `paymenttokens` (referenced on backend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | (1) Which markets use this queue — confirm if SG/HK only or all Xero markets. (2) Is there an SLA target for the working-days-lapsed counter (escalation threshold)? (3) `migratedFrom: null` filter excludes migrated credit notes — is there a separate flow for those? (4) `markCreditNoteAsPaid` — does it trigger downstream payment disbursement or only update status after a manual bank transfer? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend files
- `sleek-billings-frontend/src/pages/Refunds/CreditNotesToPay.jsx` — primary screen component

### Backend files (sleek-billings-backend)
- `src/invoice/controllers/invoice.controller.ts` — defines the three API routes
- `src/invoice/services/invoice.service.ts` — implements `markCreditNoteAsPaid` (lines ~1132–1203) and `voidInvoice` (lines ~2403–2488)
- `src/invoice/models/invoice.schema.ts` — `invoices` collection schema (SleekPaymentDB)

### API endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/invoices/?type=creditNote&status=authorised&migratedFrom=null&populateLinkedInvoice=true` | Fetch pending credit notes (paginated 100/page, searchable by `number` or `title`) |
| PUT | `/invoices/credit-note/{creditNoteId}/mark-as-paid` | Confirm disbursement — finalises the refund; downstream: Xero update, downgrade invoices if needed, credit balance refund |
| POST | `/invoices/{invoiceId}/void` | Reject — voids the credit note in Xero and cancels the refund; requires `voidReason` body payload |

### Permission gate
- `sleekBackApi.isMember({ group_name: "Billing Operations Admin" })` via `GET /users/is-member` on sleek-back-api
- `SLEEK_GROUP_NAMES.BILLING_OPERATIONS_ADMIN` constant (`src/lib/constants.jsx`)
- Users outside this group see a "no access" modal and cannot mark as paid or reject

### External integrations (backend)
- **Xero** — `XeroService`: `getCreditNoteFromId()` (verify status), `updateInvoice()`, `updateOrCreateCreditNote()`; credit note `externalId` links to `go.xero.com/AccountsReceivable/ViewCreditNote.aspx`
- **Stripe** — `StripeService`: payment processing on mark-as-paid path
- **Zendesk** — `zendeskUrl` field surfaced as "View Ticket" link per credit note row

### Data displayed per credit note
- Date Submitted (`issueDate`), Working Days Lapsed (client-side business-day count from `issueDate`, Mon–Fri UTC)
- Requester (`createdBy.email`), Approver (`submittedBy.email`), Company Name (`companyDetails.name`)
- Credit Note # (links to Xero via `externalId`), Invoice # (links to `linkedInvoice.externalUrl`)
- Subscriptions Refunding (`items[].name`), Reason for Refund (`items[].creditNoteData.reasonForRefund`), Additional Details (`items[].creditNoteData.reasonAdditionalDetails`)
- Zendesk Ticket link (`zendeskUrl`)

### Secondary action
- "View Request Form" opens Admin App > Company Overview > Billing Beta tab at the specific credit note (`VITE_ADMIN_APP_URL/admin/company-overview/?cid=...&activeCreditNote=...&tab=1`)

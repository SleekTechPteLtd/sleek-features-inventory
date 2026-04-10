# Manage Invoices and Credit Notes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Invoices and Credit Notes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (internal Sleek operations staff) |
| **Business Outcome** | Gives billing admins full control over a company's invoice lifecycle — from creation and dispatch through payment collection, voiding, and credit note issuance — so that billing records remain accurate and recoverable without engineering intervention. |
| **Entry Point / Surface** | Sleek Admin Panel → Company detail → Billing tab → Invoices section |
| **Short Description** | Admins view, search, and act on all invoices and credit notes for a company. Actions include editing draft invoices, marking invoices as paid, voiding authorised invoices (with a mandatory reason), deleting drafts, duplicating invoices, and initiating refund or downgrade credit notes. Credit notes can be marked as credited once payment is disbursed, and both document types can be viewed against their linked Xero record. |
| **Variants / Markets** | SG, HK, UK, AU (tax calculation and Stripe Direct Debit are UK-specific; currency is platform-configured per market) |
| **Dependencies / Related Flows** | Xero (invoice/credit-note sync, external URLs); Stripe (card and direct-debit charge via `chargePaymentMethod`); sleek-billings-api microservice (all read/write operations); company subscriptions (linked to invoice line items); credit balance (applied as discount on invoices); audit log (`getAuditLogsByCompanyIdAndTags` tagged per invoice) |
| **Service / Repository** | sleek-website (frontend); sleek-billings-api (backend microservice) |
| **DB - Collections** | Unknown — data is served by the sleek-billings-api microservice; collections not visible from frontend code |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. Which sleek-billings-api collections store invoices and credit notes? 2. "Mark as Paid" for regular invoices is gated to dev/SIT environments only — is manual payment marking intentionally disabled in production? 3. Is void reason stored and surfaced anywhere beyond audit logs? 4. `manualRenewal` draft invoices are hidden from the list — is there a separate UI for those? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files

| File | Role |
|---|---|
| `src/views/admin/company-billing/invoices-list.js` | Main list view; all list actions and status rendering |
| `src/views/admin/company-billing/invoice-form.js` | Invoice create/edit form; Stripe charge trigger |
| `src/views/admin/company-billing/credit-note-form.js` | Credit note create/edit/void/mark-as-credited form |

### API calls (`src/utils/sleek-billings-api.js`)

| Function | Description |
|---|---|
| `getInvoices({ companyId, page, limit, filter })` | Fetches paginated invoice + credit note list for a company (up to 1 000 per load) |
| `updateOrCreateInvoice(options)` | Creates or updates an invoice (draft → authorised) |
| `chargePaymentMethod(options)` | Charges a stored Stripe payment method against an invoice |
| `markInvoiceAsPaid(invoiceId)` | Manually marks an invoice as paid (dev/SIT only in production guard) |
| `voidInvoice(invoiceId, voidReason)` | Voids an authorised invoice; requires a non-empty reason string |
| `deleteInvoice(invoiceId)` | Soft-deletes a draft invoice |
| `getExternalUrl(invoiceId)` | Retrieves the Xero-hosted URL for viewing the invoice/credit note |
| `updateOrCreateCreditNote(options)` | Creates or updates a credit note (refund or downgrade type) |
| `markCreditNoteAsCredited(creditNoteId)` | Marks a credit note as credited/paid after disbursement |
| `getAuditLogsByCompanyIdAndTags({ companyId, tags })` | Fetches audit log entries tagged `invoice-<id>` for the drawer |

### Status lifecycle observed

- **Invoice**: `draft` → `authorised` → `paid` | `voided`
- **Credit note**: `draft` → `authorised` → `paid` (displayed as "CREDITED") | `voided`

### Menu actions per status

| Invoice status | Available actions |
|---|---|
| `draft` | Edit, Delete, Duplicate |
| `authorised` | Edit, Void, Duplicate, (Mark as Paid — dev/SIT only) |
| `paid` | View (read-only), Duplicate, Refund/Downgrade (if no open credit note) |
| Credit note `authorised` | View request form, Mark as Paid, Duplicate |

### External integrations

- **Xero** — invoices carry `externalNumber`, `externalId`, `externalUrl`; credit notes link to `go.xero.com/AccountsReceivable/ViewCreditNote.aspx`
- **Stripe** — `chargePaymentMethod` used for card (`stripe_card`) and direct debit (`stripe_dd`, UK only); minimum charge amount is platform-configured

### Market-specific behaviour (observed in code)

- `taxCalculation.enabled` — UK only; switches line amounts between tax-inclusive and tax-exclusive
- `stripe_dd` (Direct Debit) — only offered when platform currency is GBP
- Currency code and symbol read from `platformConfig.currency` at runtime

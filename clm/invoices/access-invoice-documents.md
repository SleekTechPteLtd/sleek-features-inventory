# Access Invoice Documents

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Access invoice documents |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User |
| **Business Outcome** | Allows users and operators to view or share invoice and credit note documents sourced from Xero, giving clients and internal teams direct access to billing artefacts without manual export. |
| **Entry Point / Surface** | Sleek App > Billing > Invoices — document link / download action |
| **Short Description** | Retrieves the online Xero URL for an invoice, or a signed PDF URL for a credit note, so users can open or share the document. For invoices the URL is fetched from Xero on demand and cached; for credit notes the PDF is pulled from Xero, stored in file storage, and a short-lived (120 s) signed URL is returned. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero integration (XeroService — `getOnlineInvoiceUrl`, `getCreditNoteAsPdf`); FileUploadService (credit note PDF storage & signed URL generation); Invoice create/sync flow that populates `externalId` and `externalUrl` |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | invoices (SleekPaymentDB — read `externalId`, `externalUrl`, `type`; write cached `externalUrl` for invoices) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets use this? The endpoint has no market guard. The public redirect (`GET /invoices/:id/url`) has no `@Auth()` — is this intentional for direct email links? Signed credit note URLs expire after 120 s; is that the intended client experience? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `invoice/controllers/invoice.controller.ts`

| Endpoint | Auth | Behaviour |
|---|---|---|
| `GET /invoices/:id/url` | **None** (no `@Auth()`) | Looks up invoice by ID; redirects (`res.redirect`) to `invoice.externalUrl`. Returns 404 if invoice or URL missing. |
| `GET /invoices/:id/external-url` | `@Auth()` | Calls `invoiceService.getInvoiceCreditNoteExternalUrl(invoiceId)`; returns `{ externalUrl: string }`. Works for both invoices and credit notes. |

### Service — `invoice/services/invoice.service.ts`

**`getInvoiceCreditNoteExternalUrl(invoiceId)`** (line 1077):
- Loads invoice from `invoiceRepository.findById`.
- Returns `''` if record or `externalId` is absent.
- **Credit note path**: calls `getCreditNoteSignedPdfUrl(invoice)` — checks file storage for `credit-notes/<externalId>.pdf`; if missing, fetches PDF from Xero via `xeroService.getCreditNoteAsPdf(externalId)`, uploads it, then returns a signed public URL (120 s TTL).
- **Invoice path**: if `externalUrl` is not yet cached, calls `xeroService.init({ clientType: ClientType.main })` then `xeroService.getOnlineInvoiceUrl(invoice.externalId)`, persists the URL to the DB, and returns it. If already cached, returns the stored value.

**`getOnlineInvoiceUrl`** is also called during invoice creation (line 953) to pre-populate `externalUrl` when a Xero invoice is first synced.

### Schema — `invoice/models/invoice.schema.ts`

Relevant fields on `Invoice`:
- `type` — `InvoiceType.invoice` | `InvoiceType.creditNote`
- `externalId` — Xero invoice / credit note ID
- `externalUrl` — cached Xero online URL (invoices only; credit notes store `''`)

Collection registered as `Invoice.name` against `SleekPaymentDB` (Mongoose default → `invoices`).

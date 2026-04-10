# Review Credit Note History

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Credit Note History |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Gives operations staff a single searchable view of all credit notes across every lifecycle stage so they can audit refund requests, verify approvals, and confirm credits without switching contexts. |
| **Entry Point / Surface** | Sleek Billings App > Billing > Refunds > All Credit Notes (`/credit-notes-list`) |
| **Short Description** | Displays a paginated, searchable table of all credit notes (type = `creditNote`, non-migrated) with columns for requester email, dates requested / approved / credited, company name, linked invoice number, credit note number, and status badge. Each row links out to the full refund request in the Admin app. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Credit Notes (Approval) — `credit-notes-to-approve`; Credit Notes (Payment) — `credit-notes-to-pay`; Invoice module (shared `Invoice` collection); Admin App company-overview page (deep-link target) |
| **Service / Repository** | sleek-clm-monorepo (sleek-billings-frontend, sleek-billings-backend) |
| **DB - Collections** | invoices (filtered by `type: creditNote`, `migratedFrom: null`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Status "voided" is handled in UI (uses `updatedAt` as the approval/rejection date) but no dedicated `voided` badge colour is defined in `getStatusBadge` — falls through to default grey. Intentional? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Frontend
- `apps/sleek-billings-frontend/src/pages/Refunds/CreditNotesList.jsx`
  - Calls `sleekBillingsApi.getInvoices({ page, limit: 100, populateLinkedInvoice: true, filter: JSON.stringify({ type: "creditNote", migratedFrom: null, ... }) })`
  - Debounced search (500 ms) on `number`, `title`, and `createdBy.email` via MongoDB `$regex`
  - Status badges: `draft` (yellow), `approved` (green), `credited` (blue), default/voided (grey)
  - Date columns: `createdAt` (requested), `issueDate` / `updatedAt` (approved/rejected), `paidAt` (credited)
  - "View Refund Request" button deep-links to `VITE_ADMIN_APP_URL/admin/company-overview/?cid=…&activeCreditNote=…&tab=1`
  - Company name links to Admin App billing tab for that company
  - Pagination: 100 items per page via MUI `Pagination`

- `apps/sleek-billings-frontend/src/data/nav-rail-items.js`
  - Route: `Billing > Refunds > All Credit Notes` → `/credit-notes-list`

- `apps/sleek-billings-frontend/src/services/api.js`
  - `sleekBillingsApi.getInvoices(options)` → `GET /invoices/?{queryParams}` (JWT Bearer or token auth, `App-Origin: admin` / `admin-sso`)

### Backend
- `apps/sleek-billings-backend/src/invoice/controllers/invoice.controller.ts`
  - `GET /invoices/` → `@Auth()` guard → `InvoiceService.getInvoiceList(params: GetInvoiceListRequestDto)`
  - `GetInvoiceListRequestDto` extends `BaseGetListRequestDto<Invoice>` with optional `companyId`, `populateLinkedInvoice`

- `apps/sleek-billings-backend/src/invoice/models/invoice.schema.ts`
  - Collection: `invoices`
  - Relevant fields: `type` (enum: `invoice | creditNote | msInvoice | msCreditNote`), `status` (enum includes `draft`, `authorised`, `paid`, `voided`), `number`, `title`, `createdBy`, `issueDate`, `paidAt`, `updatedAt`, `companyId`, `linkedInvoice`, `migratedFrom`, `creditNoteType` (enum: `downgrade | refund`), `refundPaymentMethodDetails`

- `apps/sleek-billings-backend/src/invoice/enums/invoice.enum.ts`
  - `InvoiceType.creditNote` is the filter key used by this view
  - `CreditNoteType`: `downgrade`, `refund`

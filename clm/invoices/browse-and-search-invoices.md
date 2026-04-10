# Browse and Search Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse and Search Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Billing Ops / Admin) |
| **Business Outcome** | Gives operations staff a single view to locate, monitor, and act on any invoice across all companies — covering payment status, amounts, and key dates — without needing direct database access. |
| **Entry Point / Surface** | Sleek Billings Admin App > Invoices |
| **Short Description** | Displays a paginated table of all invoices (100 per page) with real-time debounced search by invoice number or title. Each row shows invoice number (linked to its external URL), title, amount, status (paid / unpaid), issue date, due date, payment date, type, and a shortcut to the company billing view in the admin app. Auto-renewal charge errors surface inline as tooltip warnings on the status badge. |
| **Variants / Markets** | SG, HK, UK, AU (multi-market; `invoice.migratedFrom` distinguishes `sleek-tech` vs `sleek-accounting` for UK migrations; Xero as external invoice source across markets) |
| **Dependencies / Related Flows** | Sleek Billings API (`GET /invoices/` endpoint, `@Auth()` guard); Admin App company-overview page (`VITE_ADMIN_APP_URL`); invoice `externalUrl` (links out to Xero invoice); auto-renewal charge pipeline (surfaces errors here); reconciliation flow (`/invoices/reconcile`) |
| **Service / Repository** | sleek-billings-frontend, sleek-billings-backend |
| **DB - Collections** | `invoices` (MongoDB, `SleekPaymentDB` connection — `mongoose-paginate-v2`; response shape: `docs`, `totalDocs`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions does this cover? Is the `/invoices/` API authenticated via the same admin SSO as other billing admin pages? Currency symbol stored in `localStorage` — is this set per-session or per-company? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `sleek-billings-frontend/src/pages/Invoices/InvoicesList.jsx` — React component; full list + search + pagination UI
- `sleek-billings-frontend/src/services/api.js` — `sleekBillingsApi.getInvoices()` → `GET /invoices/?page=N&limit=100&filter=...`
- `sleek-billings-backend/src/invoice/controllers/invoice.controller.ts` — `GET /invoices/`, `@Auth()` guard, `GetInvoiceListRequestDto`
- `sleek-billings-backend/src/invoice/models/invoice.schema.ts` — `Invoice` Mongoose schema, `SleekPaymentDB`
- `sleek-billings-backend/src/invoice/repositories/invoice.repository.ts` — `InvoiceRepository extends BaseRepository<Invoice>`

### API call
```js
// services/api.js:169
getInvoices: async (options) => {
  const queryParams = new URLSearchParams(options);
  const response = await api.get(`/invoices/?${queryParams.toString()}`);
  return response;
}
```

### Search filter (MongoDB `$or` regex, built client-side)
```js
// InvoicesList.jsx:24–29
filter: searchQuery ? JSON.stringify({
  $or: [
    { number: { $regex: searchQuery, $options: 'i' } },
    { title:  { $regex: searchQuery, $options: 'i' } },
  ]
}) : undefined
```

### Columns rendered
`number` (linked via `invoice.externalUrl`), `title`, `totalAmount`, `status` (paid / other), `issueDate`, `expireAt` (due date), `paidAt`, `type`

### Status error surface
`invoice.autoRenewalChargeError` → MUI `Tooltip` warning on status badge (InvoicesList.jsx:218–226)

### Actions
"View Company" → `VITE_ADMIN_APP_URL/admin/company-overview/?cid={invoice.companyId}&currentPage=Billing+Beta` (InvoicesList.jsx:243)

### Backend endpoint
```ts
// invoice.controller.ts:49–54
@Get('')
@Auth()
@UsePipes(new ValidationPipe({ transform: true }))
async getInvoiceList(@Query() params: GetInvoiceListRequestDto) {
  return this.invoiceService.getInvoiceList(params);
}
```
`GetInvoiceListRequestDto` extends `BaseGetListRequestDto<Invoice>` — accepts `filter` (MongoDB `FilterQuery`, JSON-serialised), `page`, `limit`, `sort`, `populate`, `projection`.

### Invoice status enum
`draft | submitted | authorised | paid | voided | deleted | failed | ddInProgress`

### Invoice origin enum
`paymentRequest | betaOnboarding | autoRenewal | manualRenewal | reconcile | customerRequest | downgrade | autoUpgrade`

### Auth
Bearer JWT (OAuth) or raw token from `localStorage`; `App-Origin: admin | admin-sso` header (services/api.js:16–18). Backend guard: `@Auth()` decorator on all invoice endpoints.

### Pagination
100 items per page (`ITEMS_PER_PAGE = 100`); MUI `Pagination` component; page reset to 1 on new search (InvoicesList.jsx:47)

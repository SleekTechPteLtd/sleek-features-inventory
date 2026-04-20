# View Billing History and Invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | View Billing History and Invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (Company Admin / Finance User) |
| **Business Outcome** | Gives customers a self-serve record of all settled charges — paid invoices and credited credit notes — so they can verify payments, retrieve PDF copies, and reconcile billing without contacting support. |
| **Entry Point / Surface** | **Customer app** — **`/billing/billing-and-subscriptions?tab=history`** (Billing & Subscriptions → Billing History tab). |
| **Short Description** | Displays a table of all paid invoices and credit notes for the customer's company, searchable by reference or invoice number. Columns show reference (with credit-note-type pill), invoice number, status (Paid / Credited), amount, issue date, and payment date. Clicking a Paid or Credited invoice number fetches a fresh signed external URL and renders the PDF inline in an iframe. |
| **Variants / Markets** | Unknown — currency code is read from CMS `localization.currency_code` in platform config, suggesting multi-market support (likely SG, HK, UK, AU), but markets are not hard-coded in this component |
| **Dependencies / Related Flows** | Platform Config store (`configModule/GET_PLATFORM_CONFIG`); CMS `localization` feature prop for currency; Sleek Billings API (`GET /invoices`, `GET /invoices/:id/external-url`); My Subscriptions tab and Payment Methods tab (siblings on same page); Xero / external billing system (source of `externalUrl` and `externalNumber`) |
| **Service / Repository** | customer-billing, sleek-billings-backend |
| **DB - Collections** | `invoices` (MongoDB, read via sleek-billings-backend — filter applied: `deleted: false, status: { $in: ['paid'] }`, limit 1000) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Are credit notes stored in the same `invoices` collection as invoices (distinguished by `type: 'creditNote'`), or in a separate collection? Does `GET /invoices/:id/external-url` return a short-lived signed URL (implying expiry constraints)? Which specific markets are enabled? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `customer-billing/src/modules/sleek-billing/billing-and-subscriptions/components/BillingHistoryContent.vue` — primary component; fetches and renders billing history table, handles iframe PDF view
- `customer-billing/src/modules/sleek-billing/billing-and-subscriptions/components/BillingsAndSubscriptionsContent.vue` — parent tab container; renders `<BillingHistoryContent />` when `activeTab === 'history'`
- `customer-billing/src/modules/sleek-billing/billing-and-subscriptions/containers/BillingAndSubscriptionsContainer.vue` — page-level container; wraps in `<MasterLayout>`
- `customer-billing/src/proxies/back-end/sleek-billings-backend/sleek-billings-api.js` — `getInvoicesByCompanyId()` and `getExternalUrl()` methods
- `customer-billing/src/routes/routes.js` — route `/billing/billing-and-subscriptions` → `BillingAndSubscriptionsContainer`

### API calls

```js
// BillingHistoryContent.vue — fetch history
proxy.getInvoicesByCompanyId({
  companyId,
  authToken,
  filter: JSON.stringify({ deleted: false, status: { $in: ['paid'] } }),
  limit: 1000,
})
// → GET /invoices?companyId=&limit=1000&filter=...
// Response: { docs: Invoice[] }

// BillingHistoryContent.vue — open PDF
proxy.getExternalUrl({ invoiceId, authToken })
// → GET /invoices/:invoiceId/external-url
// Response: { externalUrl: string }
```

### Data fields mapped per row
`invoice._id` → `id`, `invoice.title` → `reference`, `invoice.externalNumber` → `invoiceNumber`, `invoice.totalAmount` → `amount` (formatted with `Intl.NumberFormat` using CMS currency code), `invoice.issueDate`, `invoice.paidAt` → `paymentDate`, `invoice.type` (detects `creditNote`), `invoice.creditNoteType` (shown as pill label), `invoice.externalUrl` (passed to iframe)

### Status logic
- `paid` + `type !== 'creditNote'` → `Paid`
- `paid` + `type === 'creditNote'` → `Credited`
- Only `Paid` or `Credited` rows render a clickable invoice number link

### Auth
Bearer token from `localStorage.getItem('id')` or `LocalStoreManager.getToken()`; `companyId` from `LocalStoreManager.getCompanyId()` (from `@sleek/customer-common`)

### Localization
Currency code loaded from platform config via Vuex: `configModule/GET_PLATFORM_CONFIG` → CMS `localization` feature prop → `value.currency_code` (defaults to `'SGD'`)

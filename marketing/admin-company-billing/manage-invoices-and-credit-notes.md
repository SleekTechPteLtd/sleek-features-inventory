# Manage invoices and credit notes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage invoices and credit notes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / billing staff (Sleek Admin). Credit note **Approve** / **Reject** / **Mark as paid** paths require membership in **`BILLING_OPERATIONS_ADMIN`** (checked via `isMember`). |
| **Business Outcome** | Staff can raise payment requests, authorise and adjust invoices in Xero-backed billing, create and settle refund/downgrade credit notes, void or delete documents where allowed, and review per-invoice audit history so company billing stays accurate and traceable. |
| **Entry Point / Surface** | **sleek-website** admin: **`/admin/company-billing/?cid=<companyId>`** (webpack entry `admin/company-billing`), and the same UI embedded under **Company overview → Billing** (“Billing Beta”, `PAGES.BILLING_BETA`). Tabs: **Subscriptions**, **Invoices & Credit Note**, **Credit Balance**. **Payment Request** opens the invoice composer; optional query **`tab`** / **`activeCreditNote`** deep-links list tab or a credit note. |
| **Short Description** | Loads company context (`cid`), services/tax rates/subscriptions from **Sleek Billings**, and lists invoices and credit notes with search. Operators open **InvoiceForm** to draft or edit payment-request invoices (line items, tax, subscriptions, Xero issuance, optional card charge via Stripe). **CreditNoteForm** handles refund vs downgrade flows with cash/bank payout details (tenant-specific fields), Zendesk URL, subscription delivery updates, Xero credit note approval, mark-as-paid, and void/reject. **InvoicesList** row/menu actions: mark paid (dev/SIT or authorised invoice), void with reason, duplicate, delete draft, refund/downgrade entry, external document links, and **View Logs** opening **AuditLogDrawer** with tagged audit records. |
| **Variants / Markets** | **Multi-tenant**: `platformConfig.tenant` drives bank-refund field sets (**sg**, **hk**, **gb**, **au**) and UK-only Direct Debit (`stripe_dd`). Tax line behaviour follows CMS **`billing_service.taxCalculation`**. Currency from `platformConfig.currency`. |
| **Dependencies / Related Flows** | **`SLEEK_BILLINGS_API`** (env) — invoices, credit notes, customer subscriptions, Xero tax rates, subscription catalog, audit logs, external URLs, payment charge. **Xero** — invoice/credit note documents (`getExternalUrl`, direct credit note link when unpaid). **Stripe** — `chargePaymentMethod` after invoice send. **Main API** — `getCompany`, `getCompanyUsers`, `getUser`. Related: company overview billing, reconcile-invoice flows, subscription management on same billing pages. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-billing/index.js`, `invoices-list.js`, `invoice-form.js`, `credit-note-form.js`, `AuditLogDrawer.js`, `src/utils/sleek-billings-api.js`. **Sleek Billings** backend (HTTP API) for persistence and Xero/Stripe orchestration — not in this repo. |
| **DB - Collections** | **Unknown** (invoice/credit note and audit storage live in Sleek Billings services; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Page-level **AdminLayout** / secondary permission for `company-billing` is commented out in `index.js` — confirm which admin roles can open this surface in production. Whether standalone `/admin/company-billing/` vs overview-embedded routing is the primary entry for most users. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-billing/index.js` (`AdminBillingConfigurationView`)

- Mount: `querystring` **`cid`** → **`api.getCompany`**, **`api.getCompanyUsers`**, **`sleekBillingsAPI.getServicesForPaymentRequest`** / **`getXeroTaxRates`** (partner → `manage_service` vs `main` client type), **`getCustomerSubscriptions`**.
- Tabs: Subscriptions, **Invoices & Credit Note**, Credit Balance; **Payment Request** sets **`showInvoiceCreator`** → **`InvoiceForm`** inside **`ErrorBoundary`**.
- **`sleekBillingsAPI.getSleekBillingsConfig`** (stub returns `SWITCH_TO_SLEEK_BILLINGS`).

### `src/views/admin/company-billing/invoices-list.js` (`InvoicesList`)

- **`getInvoices`** — query `companyId`, `populatePaymentToken: true`, `filter: { deleted: false }`; filters out draft **`manualRenewal`** origin rows.
- **`getExternalUrl`**, **`markInvoiceAsPaid`**, **`deleteInvoice`**, **`voidInvoice(voidReason)`**, **`markCreditNoteAsCredited`**, **`getAuditLogsByCompanyIdAndTags`** (`tags: ['invoice-${id}']`).
- Row click / menu: edit invoice or credit note, duplicate invoice, void invoice (reason dialog), mark invoice CN paid (dev/SIT + authorised), mark credit note paid, **View Logs** → **`AuditLogDrawer`** title “Invoice audit log”.
- Credit notes: **`activeCreditNote`** query opens **`CreditNoteForm`** with linked invoice.

### `src/views/admin/company-billing/invoice-form.js` (`InvoiceForm`)

- **`updateOrCreateInvoice`** — `POST …/invoices` with items (service, price, tax, discounts, subscription metadata), flags **`isCreateXeroInvoice`**, **`isSendPREmail`**, **`isAutoCharge`**, totals, **`invoiceOrigin`** (e.g. `paymentRequest`).
- **`getInvoiceById`**, **`getInvoices`**, **`chargePaymentMethod`** — `POST …/v2/payment/charge-payment-method` for card charge after send.
- **`getAuditLogsByCompanyIdAndTags`** + **`AuditLogDrawer`** (“Invoice audit log”).
- **`getCompanyCreditBalance`**, **`getCustomerPaymentMethods`** for payment UX.

### `src/views/admin/company-billing/credit-note-form.js` (`CreditNoteForm`)

- **`isMember`** with **`SLEEK_GROUP_NAMES.BILLING_OPERATIONS_ADMIN`** for approve/reject/mark paid.
- **`updateOrCreateCreditNote`** — `POST …/invoices/credit-note`; optional **`isCreateXeroCreditNote`**; **`updateCreditNotePaymentMethod`** — `PUT …/invoices/credit-note/:id/payment-method`.
- **`markCreditNoteAsCredited`**, **`voidInvoice`** (reject credit note).
- **`getAuditLogsByCompanyIdAndTags`** + **`AuditLogDrawer`** (“Credit note audit log”).
- Refund/downgrade validation, migrated-invoice path with subscription ID entry, tenant bank field configs.

### `src/views/admin/company-billing/AuditLogDrawer.js`

- Renders **`logs`** (`actionBy.email`, `text`, `createdAt`). Optional **`subscription`** prop adds tabs with **`getRenewalHistory`** (not used by invoice-only audit from list/form without `subscription`).

### `src/utils/sleek-billings-api.js`

- Base URL from **`getAppCustomEnv().SLEEK_BILLINGS_API`**.
- Documented endpoints: **`/invoices`**, **`/invoices/:id/external-url`**, **`/invoices/:id/void`**, **`/invoices/:id` (DELETE)**, **`/external-invoices/:id/mark-as-paid`**, **`/invoices/credit-note`**, **`/invoices/credit-note/:id/mark-as-paid`**, **`/invoices/credit-note/:id/payment-method`**, **`/audit-logs`**, **`/v2/payment/charge-payment-method`**, **`/xero/tax-rates`**, **`/subscription-config`**, **`/customer-subscriptions`**.

### Build / route

- **`webpack/paths.js`**: entry **`admin/company-billing`** → `./src/views/admin/company-billing/index.js`.
- **`webpack.common.js`**: outputs **`admin/company-billing/index.html`**.

# Record payments and manual journals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record payments and manual journals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (integration services: Xero migration/sync, Coding Engine reconciliation); Finance User benefits from accurate ledger |
| **Business Outcome** | Payments and manual journals land in SleekBooks (ERPNext) so the general ledger reflects Xero-sourced activity, CE-driven bank reconciliation, and idempotent checks before create. |
| **Entry Point / Surface** | **sleek-erpnext-service** REST API under `POST/GET /erpnext/*` — consumed by back-end integrations (not a primary Sleek App screen). Representative routes: `POST /erpnext/create-payment-from-xero`, `POST /erpnext/create-ce-payment-entry`, `POST /erpnext/create-mj-xero`, `GET /erpnext/check-manual-journal`, `GET /erpnext/check-journal-full/:journalName`, `GET /erpnext/check-payment`, `GET /erpnext/get-payment-entry-by-invoice-id`. |
| **Short Description** | Creates **Payment Entry** documents in ERPNext from Xero payment payloads (`createPaymentFromXero`) and from Coding Engine reconciliation data (`createPaymentEntryFromCE`), including deduplication when a submitted payment entry already exists for an invoice, HK-only same-currency bank-fee threshold handling, and tagging. Creates **Journal Entry** (manual journals) from Xero-shaped lines (`createManualJournalFromXero`) with multi-currency and FX gain/loss line logic where needed. Read APIs **check** existing payments and journals (`checkPayment`, `checkManualJournal`, `checkJournalFULL`, `getExistingPaymentEntryWithSubmittedStatusCreatedForInvoiceManually`). |
| **Variants / Markets** | Unknown (code branches on `PLATFORM` for HK-specific CE payment behaviour; not full market matrix in repo) |
| **Dependencies / Related Flows** | **Upstream:** Xero-sleekbooks / migration services calling payment and MJ endpoints; Coding Engine supplying `CreatePaymentEntryTransaction` + bank account context for CE payment entry. **Downstream:** ERPNext Frappe REST (`frappe.desk.form.save.savedocs`, `api/resource/Payment Entry`, `Journal Entry`, `Company`). **Adjacent:** Invoice documents (PI/SI) for allocation; `assignTagToSB` for reconciliation tags; `SleekAuditorService` elsewhere in module. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | none — this capability persists via **ERPNext** HTTP APIs only; `Companies` Mongoose schema is registered on `ErpnextModule` but `ErpnextService` does not inject it for these flows. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `GET /erpnext/check-manual-journal` uses `@Param()` but the path has no `:company_name` / `:mjId` segments — are clients expected to pass query parameters under a different contract, or is this route mis-wired? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/erpnext/erpnext.controller.ts`

- **`POST /erpnext/create-payment-from-xero`** — `createPaymentFromXero`: body `paymentRow`, `invoice`, `paidDate`, `companyUen`, `paymentCount` → `erpnextService.createPaymentFromXero`. `@ApiOperation`: “Create Payment record from Xero in SB”.
- **`POST /erpnext/create-ce-payment-entry`** — `createPaymentEntryFromCE`: body `uen`, `transaction`, `account` → `createPaymentEntryFromCE(uen, data.transaction, data.account)`. Summary: “Create Payment Entry From CE”.
- **`GET /erpnext/check-payment`** — `checkPayment`: query `paymentId` → `checkPayment(paymentId)`.
- **`GET /erpnext/get-payment-entry-by-invoice-id`** — `getPaymentEntryByInvoiceID`: query `invoice.id` → `getExistingPaymentEntryWithSubmittedStatusCreatedForInvoiceManually`.
- **`GET /erpnext/check-manual-journal`** — `checkMJ`: `@ApiOperation` “Get/Check Existing Manual Journal” → `checkManualJournal(filters.company_name, filters.mjId)` (param binding caveat above).
- **`GET /erpnext/check-journal-full`** and **`GET /erpnext/check-journal-full/:journalName`** — `checkJournal` / `checkJournalName` → `checkJournalFULL`.
- **`POST /erpnext/create-mj-xero`** — `createMJFromXero`: body `mjDetails`, `journalLines`, `companyUen`, `voucherType`, `manualJournalID` → `createManualJournalFromXero`.

These payment and manual-journal routes have **no** `@UseGuards` on the handler (unlike several other `ErpnextController` routes that use `M2MAuthGuard`). Trust boundary is likely service mesh, API gateway, or private network — confirm in deployment.

### `src/erpnext/erpnext.service.ts`

- **`createPaymentFromXero`**: Resolves company via `getCompaniesByFilter` (ERPNext `Company` resource), maps Xero `ACCPAY` / `ACCREC` to Pay/Receive Payment Entry, builds `Payment Entry` with references to Purchase/Sales Invoice, optional **Payment Entry Deduction** rows for exchange gain/loss using `exchange_gain_loss_account`, submits via `frappe.desk.form.save.savedocs` with action `Submit`.
- **`createPaymentEntryFromCE`**: Short-circuits if `getExistingPaymentEntryWithSubmittedStatusCreatedForInvoiceManually` finds a submitted PE for the invoice (PI/SI only). Loads draft PE via `erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry`, merges invoice totals and bank transaction linkage (`bank_transaction` id), `overridePaymentEntryFormData`, **`applySameCurrencyBankFeesThreshold`** when `PLATFORM === HK`, submits, `assignTagToSB`, optional `createBankFeesPaymentEntryIfNeeded`.
- **`getExistingPaymentEntryWithSubmittedStatusCreatedForInvoiceManually`**: Filters `Payment Entry` / `Payment Entry Reference` for `reference_name` = invoice and status Submitted, then loads full document.
- **`checkPayment`**: Lists `Payment Entry` by `reference_no`.
- **`checkManualJournal`**: `GET api/resource/Journal Entry` with filters on `company` and `bill_no` (= external MJ id).
- **`checkJournalFULL`**: `frappe.desk.form.load.getdoc` for doctype `Journal Entry`.
- **`createManualJournalFromXero`**: `formMJLineItems` for debit/credit lines (including Bank Entry voucher rules and multi-currency FX lines), builds `Journal Entry`, submit via `savedocs` action `Submit`.
- **`formMJLineItems`**: Shared line builder used for Xero-sourced manual journals (bank vs journal voucher types, `getExchangeRate`, optional rounding gain/loss line).

### `src/erpnext/interface/erpnext.interface.ts`

- **`CreatePaymentEntryTransaction`**, **`CreatePaymentEntryAccount`**, **`PaymentEntryInfo`**, **`JournalEntryFormData`** — shapes used by CE payment entry and journal flows.

### `src/erpnext/erpnext.module.ts`

- Registers `MongooseModule.forFeature` for `Companies` and Kafka listeners; **payment/MJ methods in `ErpnextService` do not use the injected model** (constructor only has `HttpService`, `DataStreamerService`, `SleekAuditorService`).

# Create onboarding invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Create onboarding invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (authorized company user) |
| **Business Outcome** | Companies receive a correct draft Xero invoice for incorporation or corporate-secretary transfer packages (including selected services and coupons) so clients can complete card payment for onboarding. |
| **Entry Point / Surface** | Sleek customer app — onboarding flows that prepare billing before payment; API `POST /v2/invoice/onboarding/:companyId` (mounted under `/v2/invoice` in `app-router.js`). |
| **Short Description** | Authenticated company users with `companyUser` management rights trigger invoice calculation from the company’s transfer/incorporation selection, optional locked coupon, and Xero item catalog. The backend creates or reconciles a **processing** invoice record and a **draft** Xero sales invoice: it reuses the existing unpaid processing invoice when totals match, otherwise deletes the old Xero invoice and Mongo invoice and creates fresh ones. Failures are logged to external failures and emailed to support. |
| **Variants / Markets** | Unknown — line items and Xero config are resolved via `clientTypeConfigName` and shared `xeroInvoiceCodes` / invoice vendor; no fixed country list in these files. |
| **Dependencies / Related Flows** | Xero (OAuth2 client, create/get contact, create/delete invoice); `invoice-vendor-oauth2` for priced catalog items; Redis-backed Xero tokens; locked `Coupon` on company; downstream card payment and post-payment onboarding (`pay-company-formation-and-onboarding` and payment/invoice services); `mailer-service` failure notifications. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `invoices` (Invoice model — create, deleteMany by company + PROCESSING status, findOne processing); `users` (ensure `xero_contact_id`); `coupons` (read locked coupon bound to company); `externalfailures` (persist invoicing failures). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/invoice.js`

- **`POST /onboarding/:companyId`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`, delegates to `createOnBoardingInvoiceHandler.execute`.

### `controllers-v2/handlers/onboarding-invoice/create.js`

- **`parseRequest` / `validateRequest`** — Requires `req.company` populated (middleware) and returns `COMPANY_TO_INVOICE_DOES_NOT_EXISTS` if missing.
- **`onBoardingInvoiceCalculator.execute(company, req.clientTypeConfigName)`** — Builds invoice payload.
- **`getCompanyProcessingInvoiceQuery`** — If a processing invoice exists: **`updateInvoice`** when `unpaidInvoice.total_amount === invoice.totalPrice` (reuse id only); else **`deleteXeroInvoice`**, **`deleteExistingInvoice`**, then **`generateXeroInvoice`** + **`storeInvoice`**. If none: **`storeNewInvoice`**.
- **`storeInvoice`** — Persists title `Transfer of CS - {name}` vs `Incorporation - {name}`, Xero url/number/`InvoiceID`, `status: PROCESSING`, `payment_method: INSTANT_CARD`, `paid_at: moment()` (timestamp placeholder on record).
- **Xero path** — **`createXeroContactIfNotExists`** (`createXeroContactProxy`, **`user.save()`**), **`getXeroContact`**, **`buildXeroInvoice`** (draft status, line items from mapped item codes, optional coupon line via **`buildXeroCouponItem`** / `xeroInvoicing.COUPON_*`), **`createXeroInvoiceProxy.execute`**.
- **Errors** — **`storeExternalFailureCommand`**, **`sendFailureNotificationEmail`** (`FAILURE_NOTIFICATION` template); HTTP 500 with `GENERAL_API` and `error_code`.

### `calculators/invoice/onboarding-invoice-calculator.js`

- **`getItemCodes`** — Transfer vs incorporation base items from `INVOICE_ITEM_NAMES`; walks **`company.selected_services`** with duration; optional incorporation discount when yearly secretary applies; **`invoiceVendor.getAllItems(clientTypeConfigName)`** filtered to those codes.
- **`getCouponByCompanyIdQuery`** — Locked, non-expired coupon bound to company.
- **`getTotalAmount`** — Sums Xero unit prices plus coupon amount (floors at zero).

### Related modules (not in FEATURE_LINE but referenced)

- `store-commands/invoice/create.js`, `store-queries/invoice/get-company-processing-invoice.js`, `store-commands/invoice/delete-company-processing-invoices.js`, `proxies/xero/create-contact`, `get-contact`, `create-invoice`, `delete-invoice`.

### Columns marked Unknown

- **Variants / Markets**: Tenant-driven Xero catalog and `clientTypeConfigName`; no explicit SG/HK/AU/UK list in the cited files.

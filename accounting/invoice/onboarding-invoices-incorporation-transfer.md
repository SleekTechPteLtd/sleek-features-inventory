# Create onboarding invoices for incorporation or transfer

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Create onboarding invoices for incorporation or transfer |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authorized company user (company manager) |
| **Business Outcome** | Clients get an accurate Xero draft invoice for incorporation or company-secretary transfer packages so they can pay for onboarding services that match selected add-ons and applied coupons. |
| **Entry Point / Surface** | Sleek API `POST /v2/invoice/onboarding/:companyId` (authenticated client; exact in-app screen path not determined from these files) |
| **Short Description** | Company users who can manage the company trigger calculation of line items from the company record (transfer vs incorporation, selected services mapped to Xero item codes, optional locked coupon), then create or refresh a **processing** invoice in MongoDB and a matching **draft** invoice in Xero. If a processing invoice already exists and the total is unchanged, the existing record is returned; otherwise the prior Xero invoice and processing rows are removed and replaced. Failures are logged to external failures and a support notification email is sent. |
| **Variants / Markets** | Unknown (tenant-specific Xero item config via `clientTypeConfigName`; no explicit region list in the reviewed code) |
| **Dependencies / Related Flows** | Xero (contact create/read, invoice create/delete); OAuth2 invoice vendor for catalog items (`invoiceVendor.getAllItems`); company coupon binding; payment completion and reconciliation handled elsewhere (e.g. Xero webhooks / subscription payment flows). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `invoices` (create, read processing, delete processing); `coupons` (read locked coupon by company); `users` (persist `xero_contact_id` when missing); `externalfailures` (on handler error) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which product surfaces call this route and how navigation is labeled; mapping from `clientTypeConfigName` to markets; whether all environments share the same Xero chart/item setup. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route and auth**: `controllers-v2/invoice.js` — `POST /onboarding/:companyId` with `userService.authMiddleware` and `companyService.canManageCompanyMiddleware("companyUser")`, handler `createOnBoardingInvoiceHandler.execute`. Mounted at `/v2/invoice` in `app-router.js` → full path `POST /v2/invoice/onboarding/:companyId`.
- **Handler** (`controllers-v2/handlers/onboarding-invoice/create.js`): Parses `req` for `company` and `user`; validates company exists; runs `onBoardingInvoiceCalculator.execute(company, req.clientTypeConfigName)`; loads existing processing invoice via `getCompanyProcessingInvoiceQuery`; **update path** if unpaid invoice exists: if total matches, returns same id; else deletes Xero invoice and processing DB rows, then generates new Xero + DB invoice; **create path** calls `generateXeroInvoice` then `createInvoiceCommand`. Success returns `{ code: SUCCESSFUL_INVOICING, id }`. Errors → `storeExternalFailureCommand` + `mailerService.sendEmail` (failure notification template) + `500` with generic API error and `error_code`.
- **Xero integration**: Ensures Xero contact (`createXeroContactIfNotExists` / `getXeroContact`); builds draft receivable invoice with line items from calculated items plus optional coupon line (`buildXeroCouponItem`); `createXeroInvoiceProxy` / `deleteXeroInvoiceProxy`. Invoice titles use `Incorporation - {name}` or `Transfer of CS - {name}` from `company.is_transfer`.
- **Calculator** (`calculators/invoice/onboarding-invoice-calculator.js`): Derives Xero item codes from `xeroInvoiceCodes` for transfer vs incorporation, `selected_services` (including incorporation + yearly secretary discount pairing), fetches item rows via `invoiceVendor.getAllItems(clientTypeConfigName)`, loads coupon via `getCouponByCompanyIdQuery`, computes `totalPrice` (coupon amount included; floored at zero).
- **Persistence**: `store-commands/invoice/create.js` (Mongoose `Invoice` model), `store-queries/invoice/get-company-processing-invoice.js`, `store-commands/invoice/delete-company-processing-invoices.js`; status `PROCESSING`, payment method `INSTANT_CARD` on create payload.

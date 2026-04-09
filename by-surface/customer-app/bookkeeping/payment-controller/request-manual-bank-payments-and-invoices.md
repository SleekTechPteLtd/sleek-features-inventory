# Request manual bank payments and invoices

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Request manual bank payments and invoices |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (authenticated company user), Operations / staff (invoice creation and renewal comms) |
| **Business Outcome** | Let customers pay by bank transfer or cheque with a correct Xero invoice, Sleek-side invoice record, and clear emailed banking instructions, while keeping subscription and payment-request state aligned until payment settles. |
| **Entry Point / Surface** | Customer app authenticated APIs: `POST /payment/manual-payment-request`, `POST /payment/manual-payment-upgrade-corpsec`; staff-assisted flows `POST /invoices/:companyId/create`, `PUT /invoices/:companyId/update`, `GET /companies/:companyId/invoice`; renewal comms `sendRenewalReminderEmail` (bank-transfer branch) in renewal handlers. Exact product labels for “Billing” / “Pay by bank” in the web app are not encoded in these files. |
| **Short Description** | Builds or refreshes unpaid Xero invoices via `invoiceService.createExternalUnpaidInvoice` / `updateExternalUnpaidInvoice`, persists matching `Invoice` rows (bank transfer or cash from cheque), links `ExternalPaymentInfo`, and emails `MANUAL_PAYMENT_BANK_TRANSFER_V3` / `V2` templates with bank details and invoice links. Supports payment-request line items (`validatePaymentRequestItems` vs `PaymentRequest.services_availed`), manual renewal tags (`manual_renewal`, `payment_request*`), subscription date updates, credit-balance charging, and renewal bank-transfer invoice creation plus reminder emails with optional PDF attachment. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Xero**: `invoice-vendor-oauth2` (`createCompanyInvoice`, `updateCompanyInvoice`, online invoice URLs). **Billing config**: `billingConfigService.getXeroCodesAndItems`, item filtering for payment requests. **Related**: Admin payment-request CRUD (`PaymentRequest` model, `payment-request-controller`); card flows `payment/company-subscriptions`, `payment/all-types`; **renewal**: `renewalService.filterInvoice`, `createRenewalBankTransferInvoice`, `mailerService.sendEmail` for renewal templates; **Nominee Director** entry from payment-request line items. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `paymentrequests` (Mongoose `PaymentRequest` — validation only in these paths); `invoices`; `externalpaymentinfos`; `companies`; `users`; `companyusers`; company subscription documents (via `updateSubscription` / `getSubscriptionsByCompanyId`); `companyaddnewshareholders` (corpsec upgrade manual path). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm which customer-facing screens call each route (new payment page vs legacy `expected_pay_at` / cheque fields). Whether all tenant markets use the same manual-payment email templates and banking CMS keys. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/payment-controller.js`

- **`validatePaymentRequestItems`**: Compares client `requestPaymentItems` (excluding credit-balance lines) to `PaymentRequest.findById` `services_availed`; mismatch returns 422 “already been edited”.
- **`POST /payment/manual-payment-request`** — `userService.authMiddleware`; body validation with `new_payment_page_enabled` (optional `expected_pay_at`, `cheque_number` on legacy path); `prepareOneOffAndSubscriptionInvoiceData` or existing invoice refresh via `new_payment_ui` + `invoice_tag`; `createExternalUnpaidInvoice` / `updateExternalUnpaidInvoice`; `Invoice.create` / update with `payment_method` `bank_transfer` or `cash`; `ExternalPaymentInfo`; `paymentService.chargeUserFromCreditBalance`; `mailerService.setEmailTemplate('MANUAL_PAYMENT_BANK_TRANSFER_V3', 'MANUAL_PAYMENT_BANK_TRANSFER_V2', ...)` and `mailerService.sendEmail` with `sleek_banking_details`, PayNow flag, invoice number/URL/amount; subscription updates, ND entry, `insertSubscriptionHistory` with `bankTransfer` + `paymentRequest`.
- **`POST /payment/manual-payment-upgrade-corpsec`** — Same email pattern for corpsec upgrade unpaid Xero invoice; links `ExternalPaymentInfo` to `CompanyAddNewShareholder`.
- **`POST /invoices/:companyId/create`** — For `invoice_tag` `payment_request*` or `manual_renewal`, uses `renewalService.filterInvoice` to reuse matching processing invoice or `createExternalUnpaidInvoice`; `createExternalPaymentInfo` / `createPaymentRequestItemEPI` to set `expected_external_payment_info` and manual subscription dates; emails manual bank-transfer template when tag is payment request or manual renewal.
- **`PUT /invoices/:companyId/update`** — Refreshes unpaid Xero invoice for `payment_request` or `manual_renewal` via `updateExternalUnpaidInvoice`.
- **`createPaymentRequestItemEPI`**: Mirrors subscription linking logic for staff-created payment-request invoices (xero item codes → subscription updates, `manual_active_at` / `manual_overdue_at`).

### `services/invoice-service.js`

- **`prepareOneOffAndSubscriptionInvoiceData`**: Merges subscription line items and one-off Xero items; totals via `getAmountChargedFromItems`.
- **`createExternalUnpaidInvoice`**: `loadContact`, `getModifiedItems` when `requestPaymentItems` present (custom unit/quantity/descriptions), `createCompanyInvoice`, `getOnlineInvoiceUrl`.
- **`updateExternalUnpaidInvoice`**: Loads by invoice number; skips update if Xero status `PAID`; else `updateCompanyInvoice`.
- **`getModifiedItems`**: Aligns Xero line items to `requestPaymentItems` (`service_code`, `service_unit_price`, `quantity`, dated descriptions).
- **`constructManualPaymentInvoiceFromInvoiceData`** / **`updateManualPaymentInvoiceFromInvoiceData`**: Helpers for bank vs cash titles and metadata (used elsewhere in module).

### `services/mailer-service.js`

- **`setEmailTemplate`**: Feature-toggle resolution for template ids.
- **`sendEmail`**: `mailerVendor.sendEmail` with tenant `resource_link`, accounting from-address when `isFromAccounting`, customer/support from-address rules.

### `schemas/payment-request.js`

- **Model `PaymentRequest`**: `company`, `to_be_paid_by`, `services_availed[]`, `status`, `paid_at`, `is_deleted`, `is_charge_now`, `auth_token`, `token_expiry_date`, `email`, `totalAmount`, `createdBy`; auto-increment `number`.

### `controllers-v2/handlers/renewal/renewal-service.js`

- **`createRenewalBankTransferInvoice`**: `invoiceService.prepareInvoiceData`, `filterInvoice`, `createExternalUnpaidInvoice`, `Invoice.create` with `payment_method: "bank_transfer"`, `tag: "manual_renewal"`, `createRenewalBankTransferExternalPaymentInfo` → `ExternalPaymentInfo` + `expected_external_payment_info` on subscriptions.
- **`sendRenewalReminderEmail`**: When `is_bank_transfer`, creates/refreshes bank-transfer renewal invoice, builds variables (`bank_details`, invoice amount/number/url, PDF attachment), `mailerService.sendEmail` with renewal template ids (`AUTO_RENEWAL_REMINDER_WITHOUT_CREDIT_CARD`, expired variants, etc.).

### Unknown columns (reason)

- **Variants / Markets**: Tenant-driven (`tenant`, CMS app features); no single country list in the referenced paths.

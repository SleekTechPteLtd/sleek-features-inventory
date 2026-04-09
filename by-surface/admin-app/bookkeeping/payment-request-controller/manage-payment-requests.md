# Manage payment requests

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage payment requests |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin |
| **Business Outcome** | Collect payment for company services by issuing trackable requests that can apply company wallet credit to line items, attempt immediate charges on stored cards when enabled, or email a customer payment link when charging is not used or fails. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `GET /admin/:companyId/payment-requests`, `POST /admin/payment-requests`, `POST /admin/payment-requests/:paymentRequestId/change-status`, `GET /admin/payment-requests/item-names/:serviceType`, `GET /admin/payment-requests/xero-items` (requires `invoices` full permission). Customer-facing payment page is linked from email as `{sleekWebsite2BaseUrl}/payment-request?authToken=...` (config). Exact admin app navigation label is not defined in these files. |
| **Short Description** | Admins list a company’s payment requests (with `createdBy` populated), create new requests or refresh an existing unused draft with services, totals, recipient email, and optional “charge now” when the `payment_request` admin app feature enables immediate card charging. New saves apply available accounting, corpsec, and general company credit as negative Xero line items via wallet balance and credit-balance item codes. If immediate charge is requested and enabled, the flow iterates eligible company credit cards (non-declined, unexpired), creates a short-lived `PaymentToken`, and calls `paymentAllTypes` until success or exhaustion; success sets status to USED and writes auditor logs. If no successful charge, it sends a transactional email with the payment link and enriched subscription rows (from `getBillingItems` + tenant invoice duration strings). Admins can change request status arbitrarily via a dedicated route. Separate v2 handlers expose payment-request details and status updates by auth token or id for the customer journey. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Xero / billing**: `paymentRequestService.getPaymentRequestXeroItems`, `xeroServices` constants, `billingConfigService` / `invoiceService` (items, external invoices). **Wallet / credit**: `applyAvailableCompanyCreditBalance` uses `walletService.getWalletBalanceService`, `invoiceService.getOneOffItemsFromXero(xeroCreditBalanceCodes)`. **Payments**: `paymentAllTypes` orchestrates card charge, invoice creation, subscription updates, company subscription history, optional ND entry point; uses `PaymentToken`, `Invoice`, `CreditCard`. **Email**: `store-commands/request-payments/send-payment-request` → `mailerVendor` template `PAYMENT_REQUEST_SEND_LINK`. **Renewal module**: `getBillingItems` only for email line metadata. **Auditing**: `buildAuditLog` / `saveAuditLog` on auto-charge attempts. **Access**: `accessControlService.userHasPermission(..., "invoices", "full")` for Xero items listing. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `paymentrequests` (Mongoose model `PaymentRequest`, auto-increment `number`); reads/writes `companies`, `users`, `creditcards`, `paymenttokens`, `invoices` (via `paymentAllTypes` and related services). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Map each route to the exact Sleek admin UI screen if product naming differs. Confirm market-specific behaviour for `payment_request` validity and `enable_charge_card_immediately` beyond app-feature CMS. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/payment-request-controller.js`

- **`GET /admin/:companyId/payment-requests`** — `userService.authMiddleware`; loads `Company`, `PaymentRequest.find({ company }).populate('createdBy')`.
- **`POST /admin/payment-requests`** — validates `company_id`, `services_availed`, `email`, `totalAmount`, optional `paymentRequestId`, `isChargeNow`; resolves user by email; creates or updates `PaymentRequest` (token expiry from `appFeatureUtil.getAppFeaturesByName("payment_request", "admin")`); on new request calls `applyAvailableCompanyCreditBalance(...)`; if `isChargeNow` and `enable_charge_card_immediately`, loads `CreditCard` for company, `sanitizeCreditCards`, loops cards calling `paymentAllTypes` with `requestPaymentId` / `requestPaymentItems`; on HTTP 200 sets `USED`, `paid_at`, auditor logs; if no charge success, builds `sleekWebsite2BaseUrl` link, `getBillingItems(company)`, maps services with duration/currency, `sendPaymentRequest.send(...)`.
- **`POST /admin/payment-requests/:paymentRequestId/change-status`** — body `status`, saves `PaymentRequest`.
- **`GET /admin/payment-requests/item-names/:serviceType`** — validates `serviceType` against `payment_request` allowed types, returns filtered `xeroServices`.
- **`GET /admin/payment-requests/xero-items`** — `accessControlService.userHasPermission(req.user, "invoices", "full")`; `paymentRequestService.getPaymentRequestXeroItems`, filters out `xeroCreditBalanceCodes`.

### `schemas/payment-request.js`

- **Model `PaymentRequest`**: `company`, `to_be_paid_by`, `services_availed` (nested line items), `status` (enum from `tenant.features.admin.payment_request.status`), `paid_at`, `is_deleted`, `is_charge_now`, `auth_token`, `token_expiry_date`, `email`, `totalAmount`, `createdBy`; timestamps; plugin `AutoIncrement` field `number`.

### `store-commands/request-payments/send-payment-request.js`

- **`send`**: template `config.mailer.templates.PAYMENT_REQUEST_SEND_LINK`; `mailerVendor.sendEmail` with `payment_url`, `subscriptions`, `pay_date`, `customer_email`.

### `controllers-v2/handlers/payment-requests/details.js`

- **`applyAvailableCompanyCreditBalance`**: wallet balances by currency name (`accounting`, `corpsec`, `general`), splits amounts by service code prefixes (`AC-`, `CO-`), appends credit lines via `addCreditBalanceToPaymentRequestItems` with fixed item codes `AC-53-OT-12`, `CO-58-OT-12`, `CO-59-OT-12`.
- **`getDetails`**: `PaymentRequest` by `auth_token`, `populate('company')`, reapplies credit balance for display.
- **`updateStatus`**: status update by `paymentRequestId` (v2 handler).

### `services/payment-all-types.service.js`

- **`paymentAllTypes`**: validates `payment_token`, loads card, company, prepares one-off/subscription invoice data; for payment-request flows uses `requestPaymentId` / `requestPaymentItems`, `invoice_tag`, creates/updates `Invoice`, `chargeUserFromCreditBalance`, `chargeFromCard`, `createExternalInvoice` / `updateExternalInvoice`, marks `PaymentRequest` items via `validatePaymentRequestItems`; subscription history with `subscriptionTransactionType.paymentRequest`; exported for admin auto-charge loop.

### `controllers-v2/handlers/renewal/renewal-service.js`

- **`getBillingItems`**: used by payment-request controller when formatting email lines (billing config or `invoiceVendor.getAllItems`, `invoiceService.getAvailableItems`).

### `services/credit-card-service.js`

- **`sanitizeCreditCards`**: strips `token` from card documents before use in admin charge loop; **`getCreditCards`** and other APIs not central to this capability but same module.

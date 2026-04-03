# Pay for corporate secretary upgrades

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Pay for corporate secretary upgrades |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated company user (client) |
| **Business Outcome** | Charge the pro‑rated difference when a company moves to a higher corporate‑secretary shareholder tier, record the sale in Xero, and advance the add‑shareholder workflow after card payment or after manual bank/cash settlement arranged via the app. |
| **Entry Point / Surface** | Customer app payment flows backed by `POST /payment/upgrade-corpsec` (card) and `POST /payment/manual-payment-upgrade-corpsec` (manual bank transfer or cash), with `companyId` on the query string; exact in‑app menu labels are not defined in these files. |
| **Short Description** | Pricing is derived from `CompanyAddNewShareholder` (target tier vs current corp‑sec Xero codes) and days remaining on the active subscription (`invoiceService.getCorpSecUpgradePrice`). Card flow validates an optional idempotent `payment_token`, charges Stripe via `paymentService.chargeFromCard`, creates a Xero paid invoice, updates the internal `Invoice`, then runs `invitationService.addNewShareholderFromRequest`. Manual flow creates an unpaid Xero invoice, persists an internal processing `Invoice` plus `ExternalPaymentInfo`, emails bank/PayNow instructions, and links the pending payment to the add‑shareholder record for follow‑up. |
| **Variants / Markets** | SG, HK, UK, AU (tenant `shared-data` defines `xeroCorpSecUpgradeCode` per platform; same upgrade item code `CO-64-OT-01` appears across listed configs). |
| **Dependencies / Related Flows** | **Stripe**: card charges (`payment-service.js`, client type `main` vs `manage_service`). **Xero**: `invoiceService.createExternalInvoice`, `createExternalUnpaidInvoice`, item metadata from billing config / `getOneOffItemsFromXero`. **Subscriptions**: `autoRenewalService.preparePrePaymentData` / `restorePrePaymentData` on card failure; corp‑sec tier bands in `invoice-service` / `corp-sec-subscription-service` for other change‑of‑tier math. **Shareholder onboarding**: `invitationService.addNewShareholderFromRequest` after successful card charge. **Email**: `mailerService` templates for manual bank transfer. **Wallet**: `payment-service` CO‑58 / corpsec credit balance codes appear in broader payment flows but are not the primary path for this upgrade route. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `invoices`, `companies`, `creditcards`, `companyaddnewshareholders`, `externalpaymentinfos`, `paymenttokens` (when `payment_token` is used on card upgrade) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Where webhook or ops marks manual `ExternalPaymentInfo` as paid and completes `addNewShareholderFromRequest` for the bank‑transfer path (not in the excerpted `payment-controller` routes). Confirm exact customer‑app navigation strings per tenant. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/payment-controller.js`

- **`POST /payment/upgrade-corpsec`** — `userService.authMiddleware`. Optional body `payment_token`: loads `PaymentToken`, rejects invalid/in‑progress tokens, sets `IN_PROGRESS` then deletes on success. Validates `card_id`, `companyId`, `addShareholderId`. Loads `CreditCard` for `req.user`, `Company` by `req.query.companyId`. Calls `invoiceService.getCorpSecUpgradePrice(addShareholderId, companyId, clientTypeConfigName)` for `items`, `totalAmount`, `upgradeToService`. Creates internal `Invoice` (`status: processing`, `payment_method: instant_card`). `autoRenewalService.preparePrePaymentData(company, [subscriptionCurrentCorpsec], invoice, upgradeToService.service)`. On success: `paymentService.chargeFromCard(...)`. On failure: audit logs, `Invoice.findByIdAndDelete`, `restorePrePaymentData`. On success: JSON response, then `invoiceService.createExternalInvoice`, `updateInvoicePostPayment`, `PaymentToken.deleteMany`, `invitationService.addNewShareholderFromRequest(addShareholderId, user)`.

- **`POST /payment/manual-payment-upgrade-corpsec`** — `userService.authMiddleware`. Feature `new_payment_page_enabled` toggles validation (with vs without `expected_pay_at`, `cheque_number`). Builds `ExternalPaymentInfo` (empty or with expected pay date / cheque). `invoiceService.getCorpSecUpgradePrice` → `createExternalUnpaidInvoice` with title `Corporate Secretary Upgrade - {company.name}`. Creates internal `Invoice` with `payment_method` `bank_transfer` or `cash` from cheque presence, links to `externalPaymentInfo`, saves. Sends email via `MANUAL_PAYMENT_BANK_TRANSFER_V3` / `V2` / `new_payment_ui_email_template` with bank details, invoice number/URL, optional PayNow. Sets `CompanyAddNewShareholder.expected_external_payment_info` to the `ExternalPaymentInfo` id.

### `services/invoice-service.js`

- **`getCorpSecUpgradePrice(addShareholderId, companyId, clientTypeConfigName)`** — `CompanyAddNewShareholder.findById` populated with `company`; verifies `companyId` matches. Loads Xero line items for `upgrade_to`, `current_corpsec`, and `sharedData.xeroCorpSecUpgradeCode`. Pro‑rates: \(((upgrade amount − current amount) / 365) × daysRemaining\)` into the upgrade line’s `SalesDetails.UnitPrice`. Returns `items`, `totalAmount`, `upgradeToItem`, `subscriptionCurrentCorpsec`.

- **`createExternalInvoice` / `createExternalUnpaidInvoice`** — used for posting to Xero and (for card) marking paid via Stripe charge id; `getModifiedItems` treats `xeroCorpSecUpgradeCode` as custom unit pricing (`isCustomUnitAmountQuantity`).

- **Corp‑sec subscription catalog** — `availableItems` / `xeroInvoiceCodes` entries such as `corp-sec-*-shareholder` (`CO-42`–`CO-48`‑RE‑12) and related logic in `createCompanyServicesFromItems` for tier changes.

### `services/corp-sec-subscription-service.js`

- **`computeNewCorpSecSubscription`**, **`prepareItemsDetails`** — general change‑of‑tier pricing (current vs new service, refund credit line `CO-58-OT-12`, ACRA fee `CO-73-RE-12`); used by other flows (e.g. shareholder count updates with `invoice_tag` in the same controller). Complements `getCorpSecUpgradePrice` for the dedicated upgrade payment routes.

### `services/payment-service.js`

- **`chargeFromCard`**, **`getTransactionFromCharge`** — Stripe charges and balance transactions for `createExternalInvoice` post‑payment steps; `clientTypeConfigName` selects main vs manage_service Stripe keys.

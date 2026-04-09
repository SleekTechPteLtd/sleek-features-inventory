# Reconcile Xero invoice payments (manage services)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile Xero invoice payments (manage services) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | When Xero marks an invoice as paid or voided for the manage-service integration, Sleek updates internal invoices, subscriptions, onboarding, renewals, and related workflows so billing state matches accounting reality. |
| **Entry Point / Surface** | Xero → HTTP webhook `POST /webhook/xero-manage-service` on sleek-back (no in-app navigation; server-to-server from Xero) |
| **Short Description** | Verifies each request with the manage-service Xero webhook signing key (HMAC-SHA256 of the raw body vs `x-xero-signature`). For `INVOICE` events, loads the Xero invoice by resource id and runs subscription payment reconciliation: void handling, company onboarding payment completion, corp-sec upgrade lines, accounting plan upgrades, renewals (including auto-renewal history), emails, workflow hooks, and optional staff auto-allocation for KYC. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Xero OAuth2 manage_service tenant (`invoiceVendor` / `invoice-service` for external invoice fetch and status updates); `company-subscription-service`, `company-subscriptions-schema-service`, `auto-renewal-service`, `auto-upgrade-accounting-*`, `workflow-manual-payment-handler`, `mailer-service`, `invitation-service` (add shareholder); companies using `microservice_enabled` skip processing in `processInvoiceIfPaid`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `invoices`, `companies`, `externalpaymentinfos`, `companyaddnewshareholders`, `updowngrades` (plus subscription/company updates via subscription schema services) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all markets use the same webhook and tenant config; exact Xero app registration per environment. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route and auth surface**: `controllers/invoice-controller.js` — `router.route("/webhook/xero-manage-service").post(...)`. Unauthenticated public webhook; trust is **signature only**: `CryptoJS.HmacSHA256(req.bodyPlainText, manageServicesWebhookKey)` compared to `req.headers["x-xero-signature"]` (Base64). Mismatch → `401`; match → `200`. Key from `process.env.XERO_MANAGE_SERVICES_WEBHOOKKEY` or `config.xero.oAuth2.manage_service.webhookKey`.
- **Event dispatch**: `callProcessInvoiceIfPaid` runs after `res.end()`; only when `event.eventCategory == "INVOICE"`, passes `event.resourceId` as `externalId` and `clientTypeConfigName: "manage_service"` to `subscriptionPayment.processInvoiceIfPaid`.
- **Main webhook** (`/webhook/xero`) is commented out in the same file; live path for manage services is `/webhook/xero-manage-service` only.
- **Core reconciliation**: `services/payment/subscription-payment.js` — `processInvoiceIfPaid({ externalId, clientTypeConfigName, ... })`:
  - Resolves Xero document via `getExternalInvoice` → `invoiceService.getExternalInvoiceFromId` / `getExternalCreditNoteFromNumber`.
  - Skips if company has `microservice_enabled`.
  - **Voided**: `Status === VOIDED` → `invoiceService.updateInvoiceAsVoided`.
  - **Paid path** (`AmountDue === 0`, not credit note): finds `ExternalPaymentInfo` by `xero_invoice_id`, internal `Invoice` by `InvoiceNumber`.
  - **Onboarding / draft company**: company with `expected_external_payment_info` matching → `validateDraftCompanyManualPaymentAndProcessAfterPaymentAndValidateCouponForManualPayment` (KYC invitation gating via tenant `trigger_kyc_invitation`, `processAfterPayment`, FYE updates, coupons, immigration email, etc.).
  - **Corp sec upgrade line items**: `performUpgradeCorpSecItem` / `handleCorpUpgrade` when line matches `sharedData.xeroCorpSecUpgradeCode`.
  - **Accounting upgrade**: `UpDownGrade` unpaid by invoice number → `handleAccountingUpgrade` (email + `updateInvoicePostPayment`).
  - **Renewals**: `performRenewal` → `moveCompanySubscriptionToPaid` (refresh subscription, company status, `insertServiceToSubscription` or reconcile unset), `upgradeAccountingSubscription`, `shiftAccountingCode`, `addBRService`, validation emails, `handleWorkflow` for manual payment workflows.
  - **Auto accounting upgrade by bank transfer**: branch when no subscriptions tied to `ExternalPaymentInfo` but company `new_auto_accounting_plan_upgrade` matches invoice → `autoUpgradeAccService.performAccountingAutoUpgradeByBankTransfer` and delete `ExternalPaymentInfo`.
  - **Tenant feature**: `autoAllocateStaff` for `adhoc_workflows` when enabled.
- **Exports used by webhook path**: `module.exports` includes `processInvoiceIfPaid` (and helpers for other callers): `setExpectedExternalinfoAndProcessInvoiceIfPaid`, `isUpdateCompanyStatusAndSendKYCInvitation`.

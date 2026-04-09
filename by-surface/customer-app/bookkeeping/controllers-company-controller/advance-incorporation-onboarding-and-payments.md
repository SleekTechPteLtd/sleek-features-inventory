# Advance incorporation onboarding and payments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Advance incorporation onboarding and payments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (authenticated company user); Sleek operations (admin notification on submit-to-validation); partner admins when the company is partner-attributed |
| **Business Outcome** | Move draft companies from self-serve setup into Sleek-led processing, paid-member onboarding, and bank-transfer (or post-payment) invoicing so incorporation or transfer work can continue without blocking on card checkout alone. |
| **Entry Point / Surface** | Sleek customer app — company onboarding flows: submit company for validation (`POST /companies/:companyId/submit-to-validation`), mark members submitted / advance paid status (`POST /companies/:companyId/submit-company-members`), request post-payment continuation (`PUT /companies/:companyId/apply-for-post-payment`), and arrange external bank-transfer invoicing (`PUT /companies/:companyId/apply-for-external-payment`). Exact dashboard labels are not encoded in these handlers. |
| **Short Description** | Validates shareholders/directors and invitations, sets company status toward Sleek processing (`processing_by_sleek`), emails the client (and optionally admins) about submission and next steps. Separately advances **paid and incomplete** (or partner-paid) membership, creates or refreshes Xero-backed unpaid invoices for manual bank transfer, persists `ExternalPaymentInfo`, emails bank-instruction templates, logs subscription history, and can trigger accounting onboarding questionnaire sends after external payment or post-payment. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Xero**: `invoiceService.createExternalUnpaidInvoice` / `updateExternalUnpaidInvoice`, line items from `prepareInvoiceData` + incorporation/transfer titles. **App features**: `email_notifications` (confirm processing, submit-to-validation), `onboarding_meta` (extra processing steps copy), `new_payment_page_enabled`, `onboarding` / `accounting_onboarding_workflow` (post-payment emails and questionnaire). **Related**: `companySubscriptionService.insertSubscriptionHistory`, `companySubscriptionSchemaService.updateSubscription` with `expected_external_payment_info`; accounting onboarding questionnaire (`companyUserService.sendAccountingOnboardingQuestionnaire`); `setEstimatedDateOfIncorporation`; partner white-label domains and MSCOMSEC handling for partner companies. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies`; `companyusers`; `invoices`; `externalpaymentinfos`; company subscription documents (via `updateSubscription` / `loadSubscriptions`); subscription history (via `insertSubscriptionHistory`); **Coupons** when checkout includes coupon binding (`invoiceService.bindCouponInCompany`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Full matrix of beta (`app_onboarding_version`) vs standard paths for `invoice_only` and `valid_external_payment_info`; which tenant markets use the `submit-to-validation` admin email vs confirm-processing-only; confirm product UI strings for each PUT/POST from the customer app. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/company-controller.js`

- **`POST /companies/:companyId/submit-to-validation`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`. Enforces at least one shareholder and one director, no blocking pending invitations for roles that matter, and share allocation for non-transfer companies (`ERROR_CODES.COMPANY.INVALID_SHARE_COUNT`). Sets status via `setCompanySubOrPrimaryStatus(company, "processing_by_sleek")`. Emails: `CONFIRM_PROCESSING_BY_SLEEK` or `CONFIRM_PROCESSING_BY_SLEEK_TRANSFER` (feature `confirm_processing_by_sleek_enabled`) to recipient from `companyUserService.findCompanyUserWithPreference` or, for partner companies, `partnerService.getAllPartnerAdminByCompanyId`; optional `COMPANY_SUBMIT_TO_VALIDATION` to `config.admin.emails` when `company_submit_to_validation_enabled`. Uses `partnerService.getPartnerByCompany` for `domain_url` / dashboard links and `onboarding_meta` for extra step copy.
- **`POST /companies/:companyId/submit-company-members`** — `canManageCompanyMiddleware("ownerIncompleteCompany")`; `companyService.updateStatus(company, COMPANY_STATUSES.value.PAID_AND_INCOMPLETE)` to advance paid member state after members are submitted.
- **`PUT /companies/:companyId/apply-for-post-payment`** — `userService.authMiddleware` (no `canManageCompany` in the grep block). If feature-flagged post-payment email and not a partner company, may `companyUserService.sendAccountingOnboardingQuestionnaire` for owner when accounting services are selected (`subscriptionService.getAccountingSubscriptionByTags` with `TAGS.ENABLE_ACCOUNTING_PAGE_IN_CUSTOMER_APP`).
- **`PUT /companies/:companyId/apply-for-external-payment`** — `canManageCompanyMiddleware("ownerIncompleteCompany")`. Optional `checkoutItems` → `invoiceService.createCompanySelectedService`, coupon bind. Builds or updates Xero unpaid invoice via `prepareInvoiceData`, `updateExternalUnpaidInvoice` or `createExternalUnpaidInvoice`, `constructIncorpManualPaymentInvoiceFromInvoiceData`; links `ExternalPaymentInfo` (`xero_invoice_id`, `xero_invoice_amount`, `invoices`). `setEstimatedDateOfIncorporation`. `invoice_only` short-circuits with invoice JSON for beta flows. `mailerService.setEmailTemplate('MANUAL_PAYMENT_BANK_TRANSFER_V2' | 'MANUAL_PAYMENT_BANK_TRANSFER_V3' ...)` and `sendEmail` with `sleek_banking_details` or `ms_banking_details` for partners; partner branch adjusts BCC/CC and branding. Post-external-payment: optional accounting onboarding questionnaire same as post-payment. `companySubscriptionService.insertSubscriptionHistory` with `bankTransfer` + `onboarding`. Updates subscriptions with `expected_external_payment_info`.

### `services/company-user-service.js`

- **`findCompanyUserWithPreference`**: Resolves email recipient for confirm-processing and bank-transfer emails (used from company-controller).
- **`sendAccountingOnboardingQuestionnaire`**: Triggered from `apply-for-post-payment` and `apply-for-external-payment` when flags and subscriptions match (not for partner path in these branches).
- **`canManageCompanyUserMiddleware` / status checks**: `companyStatusValidator` and flows including `paid_and_incomplete`, `partner_paid`, `paid_and_awaiting_company_detail` appear elsewhere in this service for access during onboarding (context for who can act when company is mid-onboarding).

### `services/invoice-service.js`

- **`prepareInvoiceData`**, **`createExternalUnpaidInvoice`**, **`updateExternalUnpaidInvoice`**: Core Xero invoice creation/update for incorporation/transfer titles.
- **`constructIncorpManualPaymentInvoiceFromInvoiceData`**: Creates `Invoice` with `status: "processing"`, `payment_method` `bank_transfer` or `cash` from cheque number, links Xero number/url/external id.
- **`createCompanySelectedService`**, **`bindCouponInCompany`**: Checkout selection and coupon binding before invoicing.
- **`validateDraftCompanyManualPayment`**, **`validatePayment`**, **`setCompanySubOrPrimaryStatus`**: Related paths for moving companies to `paid_and_incomplete` / partner paid after payment (complementary to the external-payment flow).

### `services/mailer-service.js`

- **`setEmailTemplate`**, **`sendEmail`**: Used for bank-transfer instructions and submit/confirm templates (template resolution and delivery; exact template id strings passed from controller/config).

### `services/partners/partner-service.js`

- **`getPartnerByCompany`**: Partner detection for domain, banking details, MSCOMSEC email branding, and suppressing certain BCC/post-payment behaviours.
- **`getAllPartnerAdminByCompanyId`**: Recipient list for confirm-processing when the company is under a partner.

### Unknown columns (reason)

- **Variants / Markets**: Tenant and `clientTypeConfigName` drive Xero and copy; no single country list in the referenced controller paths.

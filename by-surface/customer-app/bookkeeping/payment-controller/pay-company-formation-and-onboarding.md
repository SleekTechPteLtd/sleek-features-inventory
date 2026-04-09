# Pay company formation and onboarding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Pay company formation and onboarding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (company user) |
| **Business Outcome** | Clients pay for incorporation or transfer and related onboarding services so the company can move past draft status, subscriptions and Xero billing align to what was purchased, and downstream onboarding (invites, compliance, optional accounting setup) can proceed. |
| **Entry Point / Surface** | Sleek customer app — company creation / onboarding checkout flows that call payment APIs (`POST /payment/create-company/:companyId`, `POST /payment/onboarding/:companyId`, `POST /payment/update-company-before-payment/:companyId`, `POST /payment/update-company-post-payment/:companyId`, `GET /companies/:companyId/charge-amount`, `GET /payment/items`). |
| **Short Description** | Authenticated company users pay by card for formation or onboarding line items: the backend charges the card, builds or updates Xero-backed invoices, updates company status (including partner and Beta onboarding paths), runs shared post-payment processing (invitations, services from invoice lines, optional questionnaires and emails), and syncs subscription or FYE-related dates where billing rules apply. |
| **Variants / Markets** | Unknown — market and catalog behaviour are driven by tenant config, `clientTypeConfigName`, and billing/Xero item maps (e.g. AU incorporation codes appear in invoice line metadata); not a single fixed country list in these files. |
| **Dependencies / Related Flows** | `payment-service` (card charge); `invoice-service` (invoice prep, Xero create/update, `validatePayment`, `processAfterPayment`, coupons); `company-subscription-service` (history, emails); `sleek-payment` `getInvoice` for post-external payment path; invitations and mailer; optional accounting onboarding questionnaire (`company-user-service`, `subscription.service`); AGM/annual return deadlines; `billing-config-service` / Xero vendor. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `Company`, `Invoice`, `CreditCard`, `CompanyUser`, `Coupon` (coupon usage), `PaymentToken` (where used); partner linkage via `Partner` when resolving partner context. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/payment-controller.js`

- **`POST /payment/create-company/:companyId`** — `authMiddleware`, `canManageCompanyMiddleware("companyUser")`. Loads company subscriptions, blocks duplicate secretary subscription where applicable, validates card belongs to user, `invoiceService.prepareInvoiceData`, `paymentService.chargeFromCard`, `invoiceService.validatePayment`, creates/updates `Invoice` (title `Incorporation -` or `Transfer of CS/Accounting -` vs partner naming), `invoiceService.createExternalInvoice` / `updateExternalInvoice`, **`invoiceService.processAfterPayment`**, `companyService.updateSubscriptionAndFYEDates`, optional ecommerce/holding and accounting onboarding emails, `insertSubscriptionHistory` with onboarding transaction type.
- **`POST /payment/onboarding/:companyId`** — Same middleware. `invoiceService.createCompanySelectedService` from `checkoutItems`, optional `bindCouponInCompany`, `prepareInvoiceData`, charge card, `validatePayment`, early JSON response with transaction id/items, Xero invoice create/update, **`processAfterPayment`**, `updateSubscriptionAndFYEDates`, subscription history, `sendImmigrationEmail`, auditor logs.
- **`POST /payment/update-company-before-payment/:companyId`** — Persists `checkoutItems` into `company.selected_services`, optional coupon bind, sets `microservice_enabled` and `pre_payment`.
- **`POST /payment/update-company-post-payment/:companyId`** — Loads invoice via **`getInvoice`** (`sleek-payment`), advances company status (`PARTNER_PAID`, Beta `PAID_AND_AWAITING_COMPANY_DETAIL`, else `PROCESSING_INCORP_TRANSFER`), clears subscriptions array, **`invoiceService.processAfterPayment`**, `sendImmigrationEmail`, optional accounting questionnaire when feature flags allow and not partner.
- **`GET /companies/:companyId/charge-amount`** — `invoiceService.getCompanyCoupon`, `getItemsFromCompany`, `getAmountChargedFromItems`, `applyCompanyCoupon` for checkout pricing display.
- **`GET /payment/items`** — Billable line items from billing config or Xero for transfer vs incorporation.
- Local **`processAfterPayment`** (lines ~559–590) handles coupon validation and corp-sec renewal discount item collection before external invoice steps in some flows; route handlers predominantly call **`invoiceService.processAfterPayment`**.

### `services/invoice-service.js`

- **`prepareInvoiceData`**, **`getItemsFromCompany`**, **`setItemIdForOnboarding`**, onboarding feature flags (`incorporation_new_pricing`, bundle promotions, etc.).
- **`validatePayment`** — Applies selected services, sets company status to `paid_and_awaiting_company_detail` (Beta) or `paid_and_incomplete`, `setEstimatedDateOfIncorporation`, `partner_paid` when `isPartnerPayment`, nominee director hook.
- **`createExternalInvoice`** — Loads/creates Xero contact, creates company invoice in Xero.
- **`processAfterPayment`** — Partner vs standard invitation paths (`invitationService`), name-check hooks, `createCompanyServicesFromItems` when not `microservice_enabled`, marks invoice done with Xero ids/url, `updateSubscriptionsForCompany`, optional pre-payment PDF generation, auto-allocate staff, payment confirmation emails.

### `services/company-service.js`

- **`updateSubscriptionAndFYEDates`** / **`updateSubscriptionDates`** — After payment, aligns subscription dates with FYE/billing rules when admin billing features are enabled; early exit when `company.microservice_enabled` for subscription date updates.

### `services/partners/partner-service.js`

- **`getPartnerByCompany`**, **`getPartnerByCompanyId`** — Resolve partner for partner payment title, post-payment flows, invitation and email behaviour (skip some paths when partner present).

### Columns marked Unknown

- **Variants / Markets**: No single enum of countries in these files; behaviour is tenant- and billing-config-driven (per skill, use Unknown when not determined from code).

# Manage subscriptions and billing

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage subscriptions and billing |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations users and admins (company services edit/full for subscription edits; full customer-app access for “Add New Service”; CSS admin group for auto-renewal / auto-upgrade toggles) |
| **Business Outcome** | Internal staff can maintain a client company’s services, invoices, payment requests, and credit-balance activity from the company overview so billing state matches operations without switching to unrelated tools. |
| **Entry Point / Surface** | **sleek-website** admin: **Companies & Clients → Company overview** for a company (`/admin/company-overview/?cid=…`), **Billing** page section; with the newer billing UI, tabbed area under the same page (`?tab=` for Services, Invoice & Credit Note, Payment Request, Credit Balance). Breadcrumb pattern: `Companies & Clients > {company} - billing`. |
| **Short Description** | Presents subscription management (view/edit/add services, transaction history, auto-renewal and optional auto-upgrade, customer-app access toggle), invoice and credit-note reconciliation and maintenance, payment-request creation and status handling, and wallet-style credit balances — using legacy CMS APIs when the company is not on microservice billing, and swapping in microservice-backed billing components when enabled. Access is blocked when Sleek Billings migration switch is enabled for the environment (staff are told to contact support). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Backend HTTP API** (`src/utils/api.js` et al.): invoices, payment requests, subscriptions, company status, nominee directors, invoice reconcile. **Wallet API** (`api-wallet`): credit balance read/update and transactions. **Xero catalog**: `getXeroItemsForPaymentRequest` for line items when adding a service. **Platform config** / CMS app features: `companies.billing.new_ui`, `credit_balance`, `payment_request`, billing toggles (auto invoice on create, discontinued status, toggle auto-renewal UI, auto-upgrade accounting). **Parallel surface**: standalone **Company Billing** / Sleek Billings (`/admin/company-billing/`) when organisations use the newer stack — behaviour differs from this overview billing bundle. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/billing.js`, `src/views/admin/company-overview/billing-subscription.js`, `src/views/admin/company-overview/billing-invoice.js` (plus sibling `*.microservice.js` components and shared forms under `src/components/` when microservice mode is on). |
| **DB - Collections** | Unknown — this UI talks to HTTP APIs; MongoDB collection names are not declared in these view files. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | How environments map `SWITCH_TO_SLEEK_BILLINGS` and `microservice_enabled` to customer segments; whether legacy overview billing remains primary for any markets after full Sleek Billings rollout. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-overview/billing.js` (`Billing`)

- **Gate**: On mount, if `sleekBillingsConfig.SWITCH_TO_SLEEK_BILLINGS === "enabled"`, shows an alert and returns (page unusable).
- **Data load (non–microservice company)**: `api.getCompanyInvoices(companyId)`, `api.getPaymentRequests(company._id)`; optional wallet: `walletApi.getWalletBalance`, `walletApi.getWalletTransactions` when `credit_balance` feature is on.
- **Legacy layout** (`isNewBillingUIEnabled` false): tables for invoices and payment requests; `CompanySubscriptions` with `activateSubscription` / `deactivateSubscription`; credit balance table and edit form; links to `/admin/invoices/reconcile/` for create invoice.
- **Tabbed layout** (`isNewBillingUIEnabled` true): Material-UI tabs — Services → `BillingSubscription` or `BillingSubscriptionMicroservice`; Invoice → `BillingInvoice` or `BillingInvoiceMicroservice`; Payment Request → `BillingPaymentRequest*`; Credit Balance → `BillingCreditBalance`. Query `?tab=` persists selected tab.
- **Payment requests**: `api.postPaymentRequest`, `api.updatePaymentRequestStatus` (expiry), `CompanyPaymentRequestForm`.
- **Credit balance**: `walletApi.updateWalletBalance` from `CompanyCreditBalanceForm`.
- **Breadcrumb**: `setBillingBreadcrumbTitle` for company name + billing context.

### `src/views/admin/company-overview/billing-subscription.js` (`BillingSubscription`)

- **Loads**: `getPlatformConfig()`, `getCompanyTransactionHistory(company._id)`, `getXeroItemsForPaymentRequest()` for create flow; `isMember({ group_name: SLEEK_GROUP_NAMES.CSS_ADMIN })` for auto-renewal and auto-upgrade toggles.
- **View mode**: Card table of subscriptions (`display_in_admin`), columns for service type/name, dates, status, optional auto-renewal switch; row opens **Transaction history** per subscription.
- **Edit mode**: `updateSubscriptions(company._id, …)` for status/date fields; may call `changeCompanyStatus` when all subscriptions move to a new status and company status must follow; `updateAutoRenewal` for per-subscription auto charge toggle with confirm dialog.
- **Create mode**: Xero item select + subscription from/to dates + external ID (`INV-…`); either `reconcileInvoice` first if invoice not in list, or `postInsertSubscriptionToCompany`.
- **Other**: `postManageCustomerAppAccess` toggles `is_customer_app_disabled`; `reconcileInvoice` used from create flow; `getUpDownGradeById` enriches transaction rows for compare-plans dialog; `toggleAutoUpgrade` → `updateSubscriptions` for accounting auto-upgrade flag.

### `src/views/admin/company-overview/billing-invoice.js` (`BillingInvoice`)

- **Loads**: `api.getCompanyInvoices(companyId)`, `api.getCompany(companyId)`, `getPlatformConfig()`.
- **List**: Paginated `CardTable` of invoices/credit notes with amounts, status, payment date; row actions — open Xero URL, `deleteInvoice`, and when `superAdminControl=true` query param: void (`updateInvoice` status voided) and update issue/due dates (`updateInvoice` with `date` / `dueDate`).
- **Create invoice**: Company lookup (`NewCompanyLookup`), type select (Sleek vs managed-service patterns from `INVOICES_CONSTANTS`), external ID validation, optional “Do not Notify Client” for Sleek invoice; submit calls `api.reconcileInvoice` with `company_id`, `external_id`, `invoice_type`, `do_not_notify`. On success, may redirect to company overview billing tab or to `/admin/invoices/update-services/` when `refresh_subscriptions` billing flag is on and conditions match.

### Related wiring

- **Parent**: `src/views/admin/company-overview/index.js` imports `./billing` and renders it within the company overview shell (same entry as other company-overview tabs).

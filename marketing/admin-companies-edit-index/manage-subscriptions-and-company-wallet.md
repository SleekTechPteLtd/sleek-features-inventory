# Manage subscriptions and company wallet

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage subscriptions and company wallet |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Sleek Admin); some actions require **CSS Admin** (`SLEEK_GROUP_NAMES.CSS_ADMIN`) for auto-renewal toggles, **customer_app_access** permission (`full`) for creating subscriptions, toggling customer app access, and payment-request tooling |
| **Business Outcome** | Operations staff can align service subscriptions, payment requests, and prepaid wallet credits with the commercial relationship so billing state, access, and balances match what was agreed with the client. |
| **Entry Point / Surface** | **sleek-website** admin: **Company edit** page (`/admin/companies/edit/?cid=<companyId>`, webpack entry `admin/companies/edit/index`). On the main company view: **Company's Invoices & Credit Notes**, **Company's Payment Request** (when `payment_request` feature is enabled), **Company's Credit Balance** (when `credit_balance` is enabled), and **Company Subscriptions** (shown when the company has at least one subscription row). |
| **Short Description** | Loads admin subscription data and, beside invoicing, exposes payment-request listing/creation, wallet balances and transaction history via the credit-balances API, and a **Company Subscriptions** table to change status (with prompts that can cascade to **company status**), expiry and activation dates, auto-renewal, activate/deactivate service, customer app access, and optional new subscription creation—calling the platform REST API and `v2` admin subscription routes. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Platform API** (`api.js` `getBaseUrl()`): `GET /v2/admin/companies/:id/subscriptions`, `PUT /v2/admin/company-subscriptions/:id/change-status`, `PUT /admin/company-subscriptions/:id/change-expiry`, `PUT /admin/company-subscriptions/:id/change-activation-date`, `PUT /admin/company-subscriptions/:id/change-auto-renewal`, `PUT` activate/deactivate, `POST` manage customer app access, `GET /admin/:id/payment-requests`, `updatePaymentRequestStatus`. **Credit balances microservice** (`api-wallet.js`): `GET/PUT /v2/credit-balances/api/company/:id/wallet-balance`, `GET .../transactions`, `update-wallet-balance`. **CMS** feature flags: `payment_request`, `credit_balance`, `credit_balance_wallets`, `revamped_company_subscriptions`, `companies.billing.toggle_auto_renewal`, etc. Related: **Admin → Company Billing** (Sleek Billings) for the newer consolidated billing UI (`marketing/admin-company-billing/`). |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/index.js`, `src/views/admin/companies/edit/company-subscriptions.js`, `src/components/company-payment-request-form.js`, `src/components/company-create-subscription-form.js`, `src/components/company-credit-balance-form.js`, `src/utils/api.js`, `src/utils/api-wallet.js`. **Backend**: platform API and credit-balances service (not in this repo). |
| **DB - Collections** | Unknown |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Long-term split vs **Company Billing** / Sleek Billings: which UI is canonical for subscription edits per market; exact MongoDB collections behind `/v2/credit-balances` and admin subscription routes. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/edit/index.js` (`AdminCompaniesEditView`)

- **Load**: `getPaymentRequests(company._id)` → `GET ${getBaseUrl()}/admin/${companyId}/payment-requests`. When `credit_balance` enabled: `walletApi.getWalletBalance`, `getWalletTransactions`; on failure sets `companyWalletAccessible: false` and surfaces support copy.
- **Credit balance UI**: `renderCreditBalancesTable` shows per-wallet totals (accounting, corpsec, generic/general, optional balance_credit) and transaction list; **Edit Credit Balance** opens `CompanyCreditBalanceForm` via `handleClickEditCreditBalances`.
- **Submit wallet adjustment**: `formHandleSubmit` → `handleSubmitCreditBalances` → `walletApi.updateWalletBalance(company._id, { body })` then refreshes balance and transactions.
- **Payment requests**: `renderPaymentRequestsTable`, `handleClickCreatePaymentRequest`, view/edit flows with `CompanyPaymentRequestForm`; `renderPaymentStatus` may call `api.updatePaymentRequestStatus` when token expired.
- **Subscriptions**: `getCompanySubscriptions` → `api.getAdminCompanyByIdSubscriptions` → `GET /v2/admin/companies/${companyId}/subscriptions`, state `subscriptions`. Passes handlers to `CompanySubscriptions`. `handleDeactivateSubscription` / `handleActivateSubscription` → `api.deactivateSubscription` / `api.activateSubscription` (`PUT` …`/deactivate`, `…/activate`).
- **Placement**: Cards render in the main company edit layout (with invoices, conditional payment request and credit balance blocks, then `CompanySubscriptions`).

### `src/views/admin/companies/edit/company-subscriptions.js` (`CompanySubscriptions`)

- **Config**: Reads `platformConfig` (`SUBSCRIPTION_STATUSES`, `MAPS_CONSTANTS`, `revamped_company_subscriptions`, `toggle_auto_renewal`, etc.).
- **Subscription edits**: `putCompanySubscriptionChangeStatus`, `putCompanySubscriptionChangeExpiry`, `putCompanySubscriptionChangeActivationDate`, `updateAutoRenewal`, `changeCompanyStatus` (when status change should align company status), `postManageCustomerAppAccess`.
- **Permissions**: `api.isMember({ group_name: SLEEK_GROUP_NAMES.CSS_ADMIN })` for auto-renewal dialog; customer app disable/enable gated by overdue/grace rules and `user.permissions.customer_app_access === "full"`.
- **UX**: Table of services with status, optional activation/expiry columns, auto-renewal radios (when enabled), activate/deactivate actions, dialogs for status/expiry/activation/auto-renewal; optional **Create Subscription** when `customer_app_access` is `full`.

### `src/utils/api.js` (selected endpoints)

- Subscriptions: `getAdminCompanyByIdSubscriptions`, `putCompanySubscriptionChangeStatus` (`/v2/admin/company-subscriptions/:id/change-status`), `putCompanySubscriptionChangeExpiry`, `putCompanySubscriptionChangeActivationDate`, `updateAutoRenewal`, `activateSubscription`, `deactivateSubscription`, `postManageCustomerAppAccess`, `changeCompanyStatus`, `getPaymentRequests`, `updatePaymentRequestStatus`.

### `src/utils/api-wallet.js`

- `getWalletBalance`, `getWalletTransactions`, `updateWalletBalance` under `/v2/credit-balances/api/company/:companyId/…`.

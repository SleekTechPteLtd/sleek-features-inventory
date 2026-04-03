# Manage company credit balance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company credit balance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations / billing staff (Sleek Admin users on **Company Billing**; exact permission keys not enforced in these components—rely on route/API auth) |
| **Business Outcome** | Operators can see prepaid credit available to a company, review how it changed over time, and add or deduct credits with reasons so the stored balance matches what the business is owed or owes. |
| **Entry Point / Surface** | **sleek-website** admin: **Company Billing** webpack entry `admin/company-billing` — **`/admin/company-billing/?cid=<companyId>`** (optional **`&tab=2`** opens the **Credit Balance** tab: Subscriptions `0`, Invoices & Credit Note `1`, Credit Balance `2`). `CreditBalanceList` is the third tab inside `AdminBillingConfigurationView`. |
| **Short Description** | Loads balance and transaction list from Sleek Billings (`GET /credit-balances/:companyId`), displays **Available Credits** in platform currency, a table of transactions (date, initiator email, description, reason, linked invoice link, signed amount with add/deduct), and dialogs to **Add credit** or **Deduct credit** that **POST** `{ amount, reason, companyId }` to **`/credit-balances`** (positive amount for add, negative for deduct). |
| **Variants / Markets** | Currency from `store` `platformConfig.currency.code` (tenant-specific). Region markets not encoded in this UI — **Unknown** (typical Sleek tenants SG, HK, UK, AU elsewhere in inventory). |
| **Dependencies / Related Flows** | **`sleek-billings-api`**: **`getCompanyCreditBalance`**, **`updateOrCreateCreditBalance`** → Sleek Billings service base URL from **`getAppCustomEnv().SLEEK_BILLINGS_API`**. Related: same **Company Billing** area for subscriptions, invoices/credit notes, payment requests; invoice links in the table use **`transaction.invoice.externalUrl`** / **`externalNumber`**. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-billing/index.js`, `credit-balance-list.js`, `credit-balance-form.js`, `src/utils/sleek-billings-api.js`. **Sleek Billings** (external payment/billing API): persistence and authorization for credit balances — not in this repo. |
| **DB - Collections** | **Unknown** (credit balance storage lives in Sleek Billings backend; not visible in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether **Company Billing** is always standalone or embedded (e.g. company overview **Billing**); no `AdminLayout` / `secondaryPermissionKey` in `index.js` for this entry—confirm admin auth model. Whether **`tab`** query syncs reliably with **`handleTabChange`** (initial read of `tab` happens inside **`renderTabContent`** during render). Backend validation rules for max deduction vs balance, idempotency, and audit. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/company-billing/index.js` (`AdminBillingConfigurationView`)

- Mounts React at `#root`; loads **`api.getUser`**, **`getPlatformConfig`**, **`api.getCompany(query.cid)`**, **`api.getCompanyProfile`**, users, services, tax, subscriptions; optional **`sleekBillingsAPI.getSleekBillingsConfig`**.
- Tabs: **Subscriptions** (0), **Invoices & Credit Note** (1), **Credit Balance** (2). **`renderCreditBalancePage`** → **`CreditBalanceList`** with **`company`**.
- **`renderTabContent`**: reads **`tab`** from **`URLSearchParams`** and **`setState({ activeTab: parseInt(activeTab) })`**; switch **`activeTab`** case **`2`** → credit balance.

### `src/views/admin/company-billing/credit-balance-list.js` (`CreditBalanceList`)

- **`getCompanyCreditBalance(company._id)`** on mount; stores **`response.data`**, **`filteredTransactions`** from **`data.transactions`**.
- Header: **Available Credits** — **`data.balance`** formatted with **`platformConfig.currency.code`** from **`store`**.
- **Deduct Credit** / **Add Credit** → **`setShowForm("deduct"|"add")`**.
- Table columns: **`createdAt`**, **`userEmail`**, **`description`**, **`reason`**, invoice link (**`invoice.externalUrl`**, **`invoice.externalNumber`**), amount with **`actionType === "add"`** vs deduct.

### `src/views/admin/company-billing/credit-balance-form.js` (`CreditBalanceForm`)

- Dialog form: amount (**`number`**), reason (multiline); validation non-empty and **`amount >= 0`** (client-side; **`0`** passes non-trim check but **`Number(amount) < 0`** guard).
- Submit: **`updateOrCreateCreditBalance({ body: JSON.stringify({ amount: add ? +N : -N, reason, companyId: company._id }) })`**.
- Success: **`TopToaster.show("Credit balance updated.", "success")`**, **`reloadData()`**; error: **`response.data.message`** or Slack channel fallback string.

### `src/utils/sleek-billings-api.js`

- Base URL: **`${await getBasePaymentServiceUrl()}`** where **`getBasePaymentServiceUrl`** resolves **`getAppCustomEnv().SLEEK_BILLINGS_API`** once.
- **`updateOrCreateCreditBalance`**: **`POST ${base}/credit-balances`** via **`postResource`**.
- **`getCompanyCreditBalance(companyId)`**: **`GET ${base}/credit-balances/${companyId}`** via **`getResource`**.
- Shared **`handleResponse`** / **`getDefaultHeaders`** / **`checkResponseIfAuthorized`** for auth errors.

# Administer client business accounts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Administer client business accounts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin) with non-`none` `permissions.business_account` |
| **Business Outcome** | Internal staff can see and adjust a client company’s Sleek Business Account (SBA) setup—virtual accounts, currency accounts, cards, and SBA users—so banking configuration matches operational needs without clients doing it themselves. |
| **Entry Point / Surface** | **sleek-website** admin: **Company overview** (`/admin/company-overview/?cid=<companyId>`) → left nav **Business Account** (`currentPage=Business Account`). The tab renders only when CMS **`business_account`** is enabled and **`companies.onboarding_sba`** is enabled with **`business_account`** (parent sets `isSBADisabled` false); webpack entry `admin/company-overview/index`. In-app sub-routes use a hash router under the tab (`/`, `/account-details`, `/currency-details`, `/create-account`, `/archive`, …). |
| **Short Description** | Loads active and archived business accounts, company users (for SBA user enrichment), and global SBA configs in parallel (`useBusinessAccountData`). Operators browse primary/non-primary accounts, open currency-account detail (status updates), drill into SBA users (personal data, optional cards with block actions when `sba_card` CMS feature is on), create new virtual accounts (vendor/account type), set primary account, migrate dynamic VA to static VA, or close accounts with reason/primary reassignment. All mutations go through **`business-account-utils`** → **`api-bank`** to the bank/SBA service (`sba-api` base, e.g. `/sba/v2/admin/business-accounts/...`). Company user listing uses **`api.getCompanyUsersFind`** → `GET /companies/:id/company-users/find`. |
| **Variants / Markets** | Unknown (tenant/CMS-driven; `localization` and company `tenant` appear elsewhere on the same page — confirm per env). |
| **Dependencies / Related Flows** | **SBA / bank API** (`API_BANK_URL` / `sba-api`): v2 admin business-account and business-account-user routes; v3 **`/sba/v3/admin/vendor-cards/:cardId/block`** for card block; v1 **`/sba/v1/global/configs`** for configs. **Platform API**: **`getCompanyUsersFind`** for company users. **CMS**: `business_account`, `companies.onboarding_sba`, `sba_card`, `business_account` props such as `show_virtual_account_status_in_overview`. **Related inventory**: **Business Account Transactions** (`marketing/admin-transactions/…`) for payment ops; **RFI** admin table links to this overview with `currentPage=Business Account`. |
| **Service / Repository** | **sleek-website**: `src/views/admin/company-overview/business-account-v2/` (entry `index.js`, `business-account-home.js`, list/detail/archive/creation components, hooks), `src/views/admin/company-overview/index.js` (tab gate + `BusinessAccountTab`), `src/utils/business-account-utils.js`, `src/utils/api-bank.js`, `src/utils/api.js`. **External**: SBA/bank API service (not in this repo). |
| **DB - Collections** | Unknown — persistence is in the SBA/bank backend; this repo only calls REST APIs. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High (admin-only, gated tab); Medium for exact permission matrix per action (UI checks `permissions.business_account` in places such as card actions). |
| **Disposition** | Unknown |
| **Open Questions** | Exact backend RBAC for each `/sba/v2/admin/...` route vs `permissions.business_account` READ/EDIT/FULL. Whether `getBusinessAccounts` prefetch in `company-overview/index.js` (gated on `has_SBA`, company status “above LIVE”, etc.) always aligns with tab visibility (`isSBADisabled` rule). MongoDB or document model names in SBA service. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry and gating — `src/views/admin/company-overview/index.js`

- **`PAGES.BUSINESS_ACCOUNT`** → `"Business Account"` (`constants.js`).
- Tab: `isCurrentPage(PAGES.BUSINESS_ACCOUNT) && isBusinessAccountCMSEnabled && !isSBADisabled` → `<BusinessAccountTab …>`.
- `isSBADisabled` defaults `true`; set `false` when CMS `companies.props.onboarding_sba.enabled` and `business_account` CMS feature are both enabled.
- **`getBusinessAccounts`**: optional prefetch when `business_account` CMS on, company `has_SBA`, `permissions.business_account` not `none`/missing, and company status in LIVE-or-later set — calls `getCompanyBusinessAccounts({ company_id })`.

### Shell — `src/views/admin/company-overview/business-account-v2/index.js`

- Wraps **`BusinessAccountHome`** in **`HashRouter`** so sub-pages are hash routes inside the tab.

### Orchestration — `business-account-home.js`

- **`useBusinessAccountData(companyId)`** loads data; **`useEnrichedUsersMap`** merges company users with SBA user rows on accounts (incl. archived).
- Routes: default **`BusinessAccountList`**; **`BusinessAccountUserDetail`**; **`BusinessAccountCreationForm`**; **`CurrencyAccountDetail`**; **`BusinessAccountArchive`**.
- Modals: **set primary** → `useSetPrimaryBusinessAccount` → `setPrimaryBusinessAccount`; **migrate to static VA** → `useMigrateBusinessAccountToStaticVa`; **close account** → `CloseBusinessAccountModal` → `useCloseBusinessAccount` → `closeBusinessAccount` (DELETE with body).
- Breadcrumbs label context `Companies & Clients` / company name / Business account.

### Data load — `hooks/useBusinessAccountData.js`

- `Promise.all`: `getCompanyBusinessAccounts`, `api.getCompanyUsersFind(companyId, { query: { fullName: "" } })`, `getArchivedBusinessAccounts`, `getBusinessAccountConfigs`.

### API wrappers — `src/utils/business-account-utils.js` + `src/utils/api-bank.js`

- **List / archive**: `GET .../sba/v2/admin/business-accounts` (query `company_id`), `GET .../archived`.
- **Create account**: `POST .../sba/v2/admin/business-accounts` with `vendor`, `account_type` (DBS), `business_account_users` built from company users (`SBA_ROLES`, KYC-style fields).
- **Add SBA users**: `POST .../business-accounts/:id/business-account-users`.
- **User lifecycle**: `PUT .../business-account-users/:id/revoke`, `PUT .../make-owner`.
- **Account lifecycle**: `PUT .../:id` (update), `PUT .../set-primary`, `PUT .../migrate-to-static-va`, `DELETE .../:id` (close).
- **Currency**: `PUT .../currency-accounts/:currency_account_id/update-status`.
- **Cards**: `POST .../sba/v3/admin/vendor-cards/:cardId/block`.
- **Configs**: `GET .../sba/v1/global/configs` (vendors list, etc.).

### Platform API — `src/utils/api.js`

- **`getCompanyUsersFind`** → `GET ${base}/companies/${companyId}/company-users/find`.

### Representative child views

- **`business-account-user-detail.js`** / **`components/business-account-user-detail/cards.js`**: optional **Card Information** when CMS `sba_card` enabled; card block flow with `permissions.business_account` edit/full for actions.
- **`currency-account-detail.js`**, **`hooks/useUpdateStatusCurrencyAccount.js`**: currency-account status updates via `updateStatusCurrencyAccount`.

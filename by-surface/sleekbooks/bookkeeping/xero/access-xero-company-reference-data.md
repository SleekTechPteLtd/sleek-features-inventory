# Align bookkeeping with Xero organisation reference data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align bookkeeping with Xero organisation reference data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System, Integrated services (callers that supply company UEN); bookkeepers and finance users indirectly via UIs or services that consume these APIs |
| **Business Outcome** | Chart of accounts, tax rates, currencies, organisation profile, and tenant mapping stay consistent with the connected Xero organisation so downstream posting and reporting match the live ledger. |
| **Entry Point / Surface** | **xero-sleekbooks-service** REST API under `/xero`: `GET /accounts`, `GET /taxRates`, `GET /currencies`, `POST /currencies`, `GET /organisation/:companyUEN`, `GET /company/:companyUEN` (M2M-guarded). Exact Sleek app navigation is not defined in this repo. |
| **Short Description** | Resolves company UEN to a Xero tenant via BigQuery (`xero_tenants`), loads OAuth-backed Xero client configuration, then reads or writes Xero Accounting reference data: accounts (COA with optional bank/non-bank filter), tax rates, currencies (list or create), and organisation details. `getCompanyXeroInfo` returns BQ tenant row for machine-to-machine mapping. Internal helper `addCurrencyIfNotExists` is used when creating bank accounts from BSM so required currencies exist in Xero. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Google BigQuery `xero_tenants` (tenant id by `orgRegistrationNumber` / UEN); stored Xero OAuth tokens (`initializeXeroConfig`). **External:** Xero Accounting API via `xero-node` (`getAccounts`, `getTaxRates`, `getCurrencies`, `createCurrency`, `getOrganisations`). **Dev/staging:** optional `XERO_TENANT_ID` override. **Downstream:** Invoice/bank/credit-note publishing to Xero; bulk bank account creation from BSM (`addCurrencyIfNotExists`). **Related:** OAuth connect/callback (`/xero/consent`, `/xero/callback`) and other Xero flows in the same service. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | MongoDB: `xeroauthtokens` (OAuth token read and refresh on API use; `XeroAuthToken` model). BigQuery dataset `xero_tenants` for tenant mapping (not MongoDB). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Several `GET` routes have no explicit `AuthGuard` in the controller—confirm gateway or network policy. `POST /currencies` shares the same Swagger summary as `GET /currencies` in code (likely a copy-paste error). Whether markets beyond UEN-based registration are supported depends on how BQ is populated. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **HTTP surface** — `src/xero/xero.controller.ts`: `@Controller('xero')`; `GET /accounts` → `getCompanyXeroAccounts` (`companyUen`, optional `type` for `AccountsType`); `GET /taxRates` → `getTaxRates`; `GET /currencies` / `POST /currencies` → `getCurrencies` / `addCurrency`; `GET /organisation/:companyUEN` → `getOrganisationByCompanyUen`; `GET /company/:companyUEN` with `M2MAuthGuard` → `getCompanyXeroInfo`.
- **Tenant mapping** — `src/xero/xero.service.ts` `getCompanyDataFromBQ`: queries BigQuery `` `${PROJECT}.${DATASET}.xero_tenants` `` where `UPPER(orgRegistrationNumber)=companyUEN`; returns `xeroTenantId` (or env override in dev/staging/sit).
- **Chart of accounts** — `getCompanyXeroAccounts` → `getCOAs` → `XeroClient.xero.accountingApi.getAccounts` with optional `whereClause` for bank vs non-bank vs all (`AccountsType` switch).
- **Tax rates** — `getTaxRates` → `accountingApi.getTaxRates(tenantId)`.
- **Currencies** — `getCurrencies` → `getCurrencies`; `addCurrency` → `createCurrency`; `addCurrencyIfNotExists` used by `createNewCompanyBankAccountInXero` in `bulkCreateBankAccountIfNotExists`.
- **Organisation** — `getOrganisationByCompanyUen`: loads multiple BQ rows for UEN, filters active orgs from Xero, returns primary org plus `numberOfActiveAccounts`; `getOrganisationFromXero` → `getOrganisations`.
- **Company / tenant row** — `getCompanyXeroInfo` returns BQ row (tenant mapping payload) for M2M consumers.
- **Auth to Xero** — `initializeXeroConfig`: loads `xeroAuthTokenModel`, refreshes token if expired, `updateTenants`, returns configured `XeroClient`.

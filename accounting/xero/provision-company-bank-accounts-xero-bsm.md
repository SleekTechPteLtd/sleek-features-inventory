# Provision company bank accounts in Xero from BSM

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Provision company bank accounts in Xero from BSM |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Client bank accounts in Xero match Sleek onboarding (BSM) data so bookkeeping and feeds align with the company’s registered banking setup. |
| **Entry Point / Surface** | Internal / M2M — `POST /xero/bulk-create-company-bank-accounts-from-bsm` on xero-sleekbooks-service (`M2MAuthGuard`); not a Sleek App UI route in this codebase. |
| **Short Description** | Accepts a payload with `sleek_company_id`, `company_uen`, and a list of BSM bank accounts. Resolves the Xero tenant via BigQuery (`xero_tenants` by UEN), loads existing ACTIVE bank accounts from Xero, and creates any missing accounts (matched by `account_name`) via the Xero Accounting API. Returns each row’s `identifier`, `account_name`, `account_id`, and `account_number` for downstream use. |
| **Variants / Markets** | SG (UEN-based tenant lookup implies Singapore; other markets not stated in code). |
| **Dependencies / Related Flows** | Upstream: BSM / Sleek onboarding payloads. BigQuery `xero_tenants` for tenant resolution. Xero OAuth (`initializeXeroConfig`). Xero `getAccounts`, `createAccount`, `getCurrencies` / `createCurrency` (currency ensured before account create). |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | MongoDB: `xeroauthtokens` (Xero OAuth token store — read/refresh during Xero client init; no direct writes from this flow beyond existing token refresh path). BigQuery: `xero_tenants` (read). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `bank_name` is in `BulkCreateAccountfromBsmPayloadBankAccount` but is not passed into the Xero account create call — confirm whether intentional or future use. Exact calling system (internal tool name) is not named in-repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/xero/xero.controller.ts`: `POST /xero/bulk-create-company-bank-accounts-from-bsm`, `@UseGuards(new M2MAuthGuard())`, `@ApiOperation({ summary: 'Bulk create new bank account from BSM, if does not exists' })`, body `BulkCreateAccountfromBsmPayload`; validates `sleek_company_id`, `company_uen`, non-empty `bank_accounts`; delegates to `xeroService.bulkCreateBankAccountIfNotExists`.
- **Service** — `src/xero/xero.service.ts`: `bulkCreateBankAccountIfNotExists` → `getCompanyXeroInfo` / `getCompanyDataFromBQ` (tenant by UEN), `initializeXeroConfig`, `getExistingCompanyBankAccountsFromXero` (`Status=="ACTIVE" AND Type=="BANK"`), loop matches existing by `account_name` or `createNewCompanyBankAccountInXero` (`Xero.AccountType.BANK`, `bankAccountNumber`, `currencyCode`, `addCurrencyIfNotExists`), builds `BulkCreateAccountfromBsmResponse`.
- **Types** — `src/xero/interface/bank-account.interface.ts`: `BulkCreateAccountfromBsmPayload`, `BulkCreateAccountfromBsmPayloadBankAccount` (`identifier`, `account_name`, `bank_name`, `account_number`, `currency`), response types with `account_id` / `account_number` echo.

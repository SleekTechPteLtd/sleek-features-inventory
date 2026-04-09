# View company bank accounts from the connected ledger

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View company bank accounts from the connected ledger |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User; authenticated API clients and workflows that need bank accounts aligned to the active ledger |
| **Business Outcome** | Users and automations load the correct bank account list for a company from SleekBooks or Xero according to ledger and publish preference, so accounting workflows use the right chart of bank accounts. |
| **Entry Point / Surface** | Coding Engine REST API `GET /bank/accounts` (`@Controller('bank')`), consumed by bookkeeping experiences; exact app navigation is not defined in this repo. |
| **Short Description** | Resolves ledger source from optional query `publishPreference` or the company’s stored `ledger_type`, loads company by `companyId` to obtain `uen`, then fetches bank accounts from SleekBooks (ERPNext-backed API) when the ledger is SleekBooks, otherwise from Xero filtered to bank accounts and mapped to a unified `BankAccount` shape. No application-side cache on this path (unlike COA). Requires company `uen` and rejects missing company/UEN. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Company master in MongoDB (`uen`, `ledger_type`). **Integrations:** `SleekbooksService.getBankAccounts(uen)` → `SLEEKBOOKS_BASE_URL/erpnext/get-bank-accounts/{uen}`; `XeroService.getAccounts(uen, AccountsType.BANK_ACCOUNT)` via `XERO_SLEEKBOOKS_BASE_URL/xero/accounts`. **Related:** Chart of accounts (`GET /coa`) uses the same publish-preference pattern for non-bank accounts. **Downstream:** UIs or jobs that present bank pickers, reconciliation, or publish flows needing `BankAccount` fields (`name`, `account_name`, `account_number`, `account_id`, `bank_account_number`, `currency_code`). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | companies (MongoDB connection `CODING_ENGINE`; read by `company_id` to resolve UEN and default ledger when `publishPreference` is omitted) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/bank/bank.controller.ts`: `GET /bank/accounts` with `@UseGuards(AuthGuard)`; `@ApiOperation({ summary: 'Get Bank Accounts from SleekBooks/Xero' })`; query `GetCompanyBankAccountsParamsDto` → `bankService.getCompanyBankAccounts(companyId, publishPreference)`; success code `SUCCESS_CODES.BANK.GET_BANK_ACCOUNTS`.
- **Query DTO** — `src/bank/dto/bank.dto.ts`: `companyId` (required), `publishPreference` optional (`DocumentPublishPreferenceType`: `XERO` / `SLEEKBOOKS`, string values aligned with `CompanyLedgerType`).
- **Service logic** — `src/bank/bank.service.ts`: `companyModel.findOne({ company_id: ObjectId(companyId) })`; error if missing company or `uen`. Ledger: `publishPreference ?? companyRes.ledger_type`. If `ledgerType === CompanyLedgerType.SLEEKBOOKS`, returns `sleekbooksService.getBankAccounts(companyRes.uen)` (passthrough of HTTP response data). Else `xeroService.getAccounts(companyRes.uen, AccountsType.BANK_ACCOUNT)` then `xeroBankAccountsMapping` to `BankAccount[]` (display `name` as `code - name` when both present); empty array if Xero returns no rows.
- **Types** — `src/bank/interface/bank.interface.ts`: `BankAccount` (core fields plus optional identifiers for Xero/SleekBooks alignment).
- **Module** — `src/bank/bank.module.ts`: registers `BankController`, `BankService`, `XeroService`, `SleekbooksService`, `Company` Mongoose feature on `CODING_ENGINE`; exports `BankService`.
- **Auth** — `AuthGuard` (`src/common/auth/auth.guard.ts`): same pattern as other Coding Engine controllers requiring `Authorization`.

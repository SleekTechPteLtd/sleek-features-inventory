# View company chart of accounts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View company chart of accounts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User; authenticated API clients and workflows that need account lists for coding |
| **Business Outcome** | Users and automations can load the correct account list for a company from the active ledger (SleekBooks or Xero) so documents and transactions can be coded and booked against real accounts without repeated upstream calls. |
| **Entry Point / Surface** | Coding Engine REST API `GET /coa` (`@Controller('coa')`), consumed by bookkeeping and document-coding experiences; exact app navigation is not defined in this repo. |
| **Short Description** | Resolves ledger source from query `publishPreference` or the company’s stored `ledger_type` (default Xero), optionally bypasses cache with `forceRefresh`, fetches accounts from SleekBooks or Xero (Xero path returns non-bank accounts mapped to a unified shape), and caches successful results for 30 minutes in the common cache service. Requires company `uen` and rejects missing company/UEN. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Company master in MongoDB (`uen`, `ledger_type`). **Integrations:** `SleekbooksService.getAccounts(uen)` for SleekBooks; `XeroService.getAccounts(uen, AccountsType.NON_BANK_ACCOUNT)` for Xero. **Infrastructure:** `CommonCacheService` Redis-backed cache with keys `coa:{companyId}:{ledgerType}`. **Downstream:** Any UI or job that lists accounts for coding against `CoaData` (name, account_name, account_number, account_id, account_type). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | companies (MongoDB connection `CODING_ENGINE`; read by `company_id` to resolve UEN and ledger preference) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether any callers rely on `publishPreference` enum string matching exactly `CompanyLedgerType` / `DocumentPublishPreferenceType` values beyond `xero` and `sb`; confirm production cache backend and TTL expectations if multi-region. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/coa/coa.controller.ts`: `GET /coa` with `@UseGuards(AuthGuard)`; `@ApiOperation({ summary: 'Get Coa from SleekBooks/Xero' })`; query `GeCompanyCoaParamsDto` → `coaService.getCompanyCoa(companyId, publishPreference?, forceRefresh?)`; success code `SUCCESS_CODES.COA.GET_COA`.
- **Query DTO** — `src/coa/dto/coa.dto.ts`: `companyId` (required), `publishPreference` optional (`DocumentPublishPreferenceType`: `XERO` / `SLEEKBOOKS`), `forceRefresh` optional boolean (default false in Swagger).
- **Service logic** — `src/coa/coa.service.ts`: `companyModel.findOne({ company_id })`; error if missing company or `uen`. Ledger: `publishPreference ?? companyRes.ledger_type ?? CompanyLedgerType.XERO` (warns when both missing). Cache key `coa:${companyId}:${ledgerType}`; on miss (or `forceRefresh`), SleekBooks branch calls `sleekbooksService.getAccounts(uen)`; else `xeroService.getAccounts(uen, AccountsType.NON_BANK_ACCOUNT)` then `xeroNonBankAccountsMapping` to `CoaData[]` (display `name` as `code - name` when both present). `setCacheWithTTL` 30 minutes (`COA_CACHE_TTL_MS`) when `coaData.length > 0`.
- **Types** — `src/coa/interface/coa.interface.ts`: `CoaData` fields (`name`, optional `account_name`, `account_number`, `account_id`, `account_type`, `is_populated_by` with `CoaPopulatedBy`); `SALES_CATEGORY_NAME` constant — not used in controller/service paths above but part of COA domain types.
- **Auth** — `AuthGuard` (`src/common/auth/auth.guard.ts`): requires `Authorization` header and validates via cache/Sleek Back pattern used across the app.

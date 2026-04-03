# View Xero chart of accounts for a company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View Xero chart of accounts for a company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User; internal services that power bookkeeping UIs |
| **Business Outcome** | Bookkeeping can see the connected Xero ledger’s accounts (by bank vs non-bank or all) for a company identified by UEN so coding, categorisation, and publishing stay aligned with Xero. |
| **Entry Point / Surface** | Coding Engine REST API: `GET /xero/accounts` (`companyUen`, `type` query params). Swagger operation summary: “Get Accounts from Xero”. Exact Sleek app navigation is not defined in this repo. |
| **Short Description** | Returns a company’s Xero chart accounts from the connected ledger. Callers pass the company UEN and an account filter: bank accounts only, non-bank accounts only, or all accounts. The service delegates to the SleekBooks Xero integration service and maps the `companyXeroAccounts` payload into typed account rows. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Company must be linked to Xero via SleekBooks (`XERO_SLEEKBOOKS_BASE_URL`). **Downstream:** Chart data supports document line categorisation, bank account selection, and Xero publish flows that reference account codes/IDs (`XeroService` invoice/bank transaction builders use line item categories tied to accounts). **Related in repo:** `getTaxRates`, `getCurrencies`, `createCurrency` are separate Xero/SleekBooks reads and writes. |
| **Service / Repository** | acct-coding-engine; SleekBooks (HTTP: `/xero/accounts`) |
| **DB - Collections** | None for this path — `getAccounts` does not read or write MongoDB; account data is returned from SleekBooks. The `XeroModule` registers `Company` and `Document` models for other Xero flows, not for this endpoint. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Controller has no explicit `AuthGuard` in code—confirm whether API gateway or network policy enforces auth. Swagger marks `type` as required while the handler types `type` as optional; confirm expected behaviour when `type` is omitted (URL may include `type=undefined`). Whether markets beyond SG are supported depends on SleekBooks/Xero connection rules, not visible here. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **HTTP surface** — `src/xero/xero.controller.ts`: `@Controller('xero')`, `@Get('/accounts')`, `@ApiOperation({ summary: 'Get Accounts from Xero' })`, query `companyUen` (required per `@ApiQuery`), `type` (`AccountsType`, described as required in Swagger). Handler calls `xeroService.getAccounts(companyUen, type)` and wraps the result with `successResponseHandler` / `SUCCESS_CODES.XERO.GET_ACCOUNTS` on success, `errorResponseHandler` on failure.
- **Integration** — `src/xero/xero.service.ts` `getAccounts(companyUen, type?)`: `GET ${XERO_SLEEKBOOKS_BASE_URL}/xero/accounts?companyUen=${companyUen}&type=${type}` via `HttpService`; on HTTP 200 and presence of `response.data.companyXeroAccounts`, returns `companyXeroAccounts` as `XeroAccountsData[]`; otherwise logs and throws.
- **Filter enum** — `src/xero/enum/xero.enum.ts` `AccountsType`: `BANK_ACCOUNT` (`bank_account`), `NON_BANK_ACCOUNT` (`non_bank_account`), `ALL` (`all`).
- **Response shape** — `src/xero/interface/xero.interface.ts` `XeroAccountsData`: `code`, `name`, `accountID`, `type`, `status`, `description`, `taxType`, reporting fields, optional bank fields (`bankAccountNumber`, `bankAccountType`, `currencyCode`), etc.
- **Module wiring** — `src/xero/xero.module.ts`: registers `XeroController`, `XeroService`; Mongoose features for `Document` / `Company` are for other service methods, not `getAccounts`.

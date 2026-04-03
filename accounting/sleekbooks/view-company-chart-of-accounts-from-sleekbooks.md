# View company chart of accounts from SleekBooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View company chart of accounts from SleekBooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User; internal API clients and automations that need the SleekBooks ledger account list for coding |
| **Business Outcome** | Users and systems can load a company’s chart-of-accounts list from SleekBooks (ERPNext) so categorisation and accounting workflows use the same account names, numbers, and IDs as the live ledger. |
| **Entry Point / Surface** | Coding Engine REST API `GET /sleekbooks/accounts/company/:companyId` (Swagger summary: “Get Accounts from SleekBooks”). No `AuthGuard` on `SleekbooksController` in code—auth may be enforced only at gateway or by deployment; contrast with `GET /coa` which uses `AuthGuard`. |
| **Short Description** | Proxies to the SleekBooks integration service: HTTP GET `{SLEEKBOOKS_BASE_URL}/erpnext/get-accounts/{companyId}?limit=500`, maps each account to a display `name` (preferring `account_number` + `account_name` when present), and returns `original_name`, `account_number`, `account_name`, `account_id`, and `account_type`. Does not read MongoDB or use the COA Redis cache. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** SleekBooks ERPNext API via `SLEEKBOOKS_BASE_URL` (`HttpService`). **Related:** `CoaService` / `GET /coa` can call `SleekbooksService.getAccounts(uen)` with caching and ledger selection—this route is the direct, uncached SleekBooks-only path. **Downstream:** Same account shape feeds `categoryMapping` / invoice payloads that post categories to SleekBooks. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | none (read path is HTTP to SleekBooks only) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Route param is named `companyId` but `getAccounts` passes it to `get-accounts/{companyUEN}`—confirm whether callers pass `company_id`, UEN, or another company key. Whether the lack of `AuthGuard` on this controller is intentional (internal-only network) or should align with `GET /coa`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/sleekbooks/sleekbooks.controller.ts`: `@Controller('sleekbooks')`; `GET accounts/company/:companyId`; `@ApiOperation({ summary: 'Get Accounts from SleekBooks' })`; `getAccounts` → `sleekbooksService.getAccounts(params.companyId)`; success `SUCCESS_CODES.SLEEKBOOKS.GET_ACCOUNTS`; no `@UseGuards` on controller or method.
- **Params DTO** — `src/sleekbooks/dto/sleekbooks.dto.ts`: `GetAccountsParamsDto` with required `companyId` (`@IsNotEmpty()`, Swagger string).
- **Service** — `src/sleekbooks/sleekbooks.service.ts`: `getAccounts(companyUEN)` builds URL `${SLEEKBOOKS_BASE_URL}/erpnext/get-accounts/${companyUEN}?limit=${limit}` (default `limit` 500); on HTTP 200 calls private `getFilteredAccounts` to map `response.data` array: builds `name` from `account_number` / `account_name` / `name`, keeps `original_name`, `account_number`, `account_name`, `account_id`, `account_type`; filters nullish entries. Public `categoryMapping` (lines 27–34) aligns `CoaData`-like fields for invoice flows—related shape, not used inside `getAccounts` response path.
- **External system** | ERPNext accounts exposed through SleekBooks service (`/erpnext/get-accounts/...`).

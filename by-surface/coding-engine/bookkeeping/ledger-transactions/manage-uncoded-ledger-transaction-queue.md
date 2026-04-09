# Manage uncoded ledger transaction queues (supporting documents)

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage uncoded ledger transaction queues (supporting documents) |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Operations User, Customer |
| **Business Outcome** | Teams and customers can see which unreconciled bank transactions still need supporting documents, prioritize work with totals and bank-level counts, work in the right financial year and filing-period context, and export lists—so the coding and document workflow can be completed efficiently. |
| **Entry Point / Surface** | Sleek App / Coding Engine flows consuming API tag `ledger-transaction` (`GET /ledger-transactions`, related read endpoints); requires `Authorization` and `app-origin` (`admin`, `customer`, `coding-engine`) on company-scoped routes |
| **Short Description** | Lists unreconciled ledger transactions in a selected financial year (from FY options or explicit dates), excluding fully coded “in books” items from customer-facing views unless using the internal app origin. Supports search, bank account, date and amount filters, unread-comment and AI-match filters, pagination, and enriched rows (comments, matched document context for internal users). Exposes eligible vs pending amount totals (functional currency), upcoming filing period, FY dropdown data, per–bank-account filter counts, whether cash coding applies for supporting documents, and CSV (or configured format) download of the same filtered set. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek FYE** (`sleekFyeService`) for FY options and filing-period windows; **company** service for company profile and accounting tool; **bank-statement-engine** for bank accounts / ledger bank account names (cached in **Redis** via `CommonCacheService`); **CMS / App features** (`AppFeatureService`, `@sleek-sdk/sleek-cms`) for subscription service codes on FY options and supporting-document cash coding whitelist; **FX** (`FxrateCacheService`, `getConversionRate`) to convert multi-currency totals to company functional currency; **SleekBack** for commenter display names; **reconciliations** collection and **documents** (`documentdetailevents` on Sleek Receipts DB) for AI-match and matched-document enrichment; related **reconciliation** flows when unreconciling from this surface (controller delegates to `ReconciliationService`). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `ledger_transactions` (coding-engine MongoDB); `reconciliations` (aggregation lookups for match-review / AI paths); `documentdetailevents` (Sleek Receipts connection for linked documents) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `getCompanyUpcomingFilingPeriodAndSubscription` sets `has_subscription` to `true` with a comment about a temporary billing bypass—confirm behaviour once billing checks are restored. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/ledger-transaction/ledger-transaction.controller.ts`

- **Base route**: `@Controller('ledger-transactions')`, `@ApiTags('ledger-transaction')`, `@ApiSecurity('Authorization')`.
- **List (queue)**: `GET /ledger-transactions` → `getLedgerTransactionsForCompany` — `AuthGuard`, `CompanyAccessGuard`, required `app-origin` header; query `GetLedgerTransactionsParamsDto` (`cid`, pagination, `start_date` / `end_date`, `bank_account_id`, `search`, `date_from` / `date_to`, amount bounds, `has_unread_comments`, `has_ai_match`). `@ApiOperation` states transactions exclude `document_upload_status` of `in_books` and require document attachment (aligned with supporting-doc workflow).
- **Totals**: `GET /ledger-transactions/totals/:company_id` → `getEligibleAndPendingTotalTransactionAmount` — same guards; optional `start_date`, `end_date`.
- **Filing period**: `GET /ledger-transactions/upcoming-filing-period/:company_id` → `getCompanyUpcomingFilingPeriodAndSubscription`.
- **FY options**: `GET /ledger-transactions/fy-options/:company_id` → `getFyOptionsForCompany`.
- **Filter counts (bank pills)**: `GET /ledger-transactions/filter-counts/:company_id` → `getFilterCounts` — query `GetFilterCountsParamsDto` (same filters as list minus `cid`).
- **Cash coding flag**: `GET /ledger-transactions/:company_id/should-supporting-document-cash-coding-enabled` → `shouldSupportingDocumentCashCodingEnable` — uses `app-origin` + `company_id` path.
- **Export**: `GET /ledger-transactions/download` → `downloadLedgerTransactions` — `DownloadLedgerTransactionsDto` (extends list filters, adds `format`); `@ApiOperation` describes CSV columns Date, Description, Amount, Document Status.

### `src/ledger-transaction/ledger-transaction.service.ts`

- **FY resolution**: `resolveFinancialYearInfo` uses explicit `start_date`/`end_date`, else default FY from `getFyOptionsForCompany`, else `getCompanyUpcomingFilingPeriodAndSubscription`.
- **Shared filter (list / counts / download)**: `buildLedgerTransactionMatchQuery` — scopes to company, FY date range, `accounting_tool`, `reconciliation_status: UNRECONCILED`, document statuses in `allowedStatuses` (includes `UNDER_REVIEW` and `IN_BOOKS` only when `appOrigin === CODING_ENGINE`), plus `$or` for null status; **customer** origin adds hide filter for `is_hidden_from_customer`. Applies bank, date range, amount, and search filters via helpers.
- **List pipeline**: `fetchPaginatedTransactions` — sorts with status priority (e.g. rejected first), unread comment counts per user, optional reconciliation lookup when customer match-review feature flag is on; returns `transactions_with_unread_comments` and `ai_match_count` where implemented.
- **Totals**: `getEligibleAndPendingTotalTransactionAmount` — aggregation sums `eligible_total` and `pending_total` by currency with business rules in `$group` (e.g. pending: unreconciled, no `document_id`, no comments, excludes certain statuses and hidden-from-customer rows); converts to functional currency via FX helpers.
- **FY options**: `getFyOptionsForCompany` — `getAccountingSubscriptionServiceCodes` from CMS; `sleekFyeService.getCompanyFYsBasedOnSubscriptions`.
- **Filing period**: `getCompanyUpcomingFilingPeriodAndSubscription` — `companyService.findCompanyById`, `sleekFyeService.findCompanyFyInfoByCompanyId`, derives window with `LEDGER_TRANSACTION_CONSTANTS.FILING_PERIOD.MAX_GAP_MONTHS`; `has_subscription` currently forced `true` in code with comment about billing bypass.
- **Filter counts**: `getFilterCounts` — same `matchQuery` as list; aggregates by `ledger_bank_account_name` with `pending_count` vs `transaction_count`; enriches bank display names via bank-statement path (see method continuation).
- **Cash coding**: `shouldSupportingDocumentCashCodingEnable` — requires `coding_engine` general feature enabled, `supporting_documents` prop with company in `whitelisted_companies`, and valid filing period from `getCompanyUpcomingFilingPeriodAndSubscription`.
- **Download**: `downloadLedgerTransactions` — same `resolveFinancialYearInfo` + `buildLedgerTransactionMatchQuery` as list; `generateContentForFormat` / `generateFilename`.
- **Bank accounts**: `retrieveLedgerBankAccounts` for SleekBooks uses cached ledger bank account names from `getCachedLedgerBankAccountNames` (bank-statement-engine + Redis).

### `src/ledger-transaction/dto/ledger-transaction.dto.ts`

- **List params**: `GetLedgerTransactionsParamsDto` — validates `cid` as ObjectId, pagination 1–100, optional filters as documented on the controller.
- **Response**: `GetLedgerTransactionsResponseDto` — `ledgerTransactions`, `financial_year`, `pagination`, `applied_filters`, `transactions_with_unread_comments`.
- **Download**: `DownloadLedgerTransactionsDto` — omits `page`/`limit`, adds optional `FileFormat`.
- **Filter counts query**: `GetFilterCountsParamsDto` — extends list filters without `cid` (company in path).
- **FY / filter count response DTOs**: `GetFyOptionsResponseDto`, `GetFilterCountsResponseDto` / `BankAccountFilterCountDto`.

### `src/ledger-transaction/models/ledger-transaction.schema.ts`

- **Collection**: `@Schema({ collection: 'ledger_transactions', timestamps: true })` — fields include `company_id`, `ledger_transaction_id`, `ledger_bank_account_name`, dates, amounts, `document_upload_status`, `document_id`, `ledger`, `reconciliation_status`, `comments` (with `read_by`), `accounting_tool`, `is_hidden_from_customer`, etc.

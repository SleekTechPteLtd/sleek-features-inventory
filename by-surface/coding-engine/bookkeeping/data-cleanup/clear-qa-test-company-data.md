# Clear QA test company data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Clear QA test company data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | SDET / QA automation (authenticated API caller; not a standard end-user flow) |
| **Business Outcome** | Shared test environments can be reset after automated runs by deleting data tied to designated test companies, so QA pipelines stay reliable and do not pollute staging with leftover questionnaires, receipts, accounting-tool state, bank-statement-engine data, or coding-engine company rows. |
| **Entry Point / Surface** | Coding Engine REST API: `DELETE /data-cleanup` under `@ApiTags('Data Cleanup')`, guarded for SDET automation only (`X-Sleek-Sdet`, `X-QA-Name` headers). Not a Sleek app navigation path. |
| **Short Description** | Accepts a company ID and one or more cleanup types (or `all`). For company deletion in this service, the company name must match the `Autotestcom -` prefix (case-insensitive). Orchestrates hard delete of the company document in MongoDB when requested, delegates questionnaire/receipt/accounting-tools/receipt-system cleanup to Sleek Back, and bank-statement-engine cleanup to the in-repo bank statement engine service (SG/HK only per `COUNTRY`). |
| **Variants / Markets** | SG, HK (bank statement engine cleanup runs only when `COUNTRY` is `sg` or `hk`; other cleanup types are not market-gated in this module) |
| **Dependencies / Related Flows** | **Upstream:** Valid SDET secret (`SDET_SECRET_KEY`) and QA name header. **Downstream:** `SleekBackService` (`cleanupQuestionnaire`, `cleanupReceiptUser`, `cleanupAccountingTools`, `cleanupReceiptSystem`); `BankStatementEngineService.deleteCompanyAndRelatedData` (company ID + QA name). **Data safety:** Company hard-delete path requires company name prefix `Autotestcom -` via `validateCompanyName`. |
| **Service / Repository** | acct-coding-engine (orchestration); Sleek Back (questionnaire, receipt user/system, accounting tools); bank statement engine module within acct-coding-engine for BSM teardown |
| **DB - Collections** | `companies` on coding-engine Mongo connection (`DBConnectionName.CODING_ENGINE`) — `deleteOne` by `company_id` when type `company` or `all` is used; other stores touched indirectly via Sleek Back and bank statement engine |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether this route is exposed outside trusted QA networks in any environment; exact Sleek Back collections/APIs behind each cleanup method are defined outside this repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** — `src/data-cleanup/data-cleanup.controller.ts`: `DELETE /data-cleanup` → `cleanup(@Body() CleanupRequestDto, @Headers('X-QA-Name'))` → `DataCleanupService.performCleanup`. `@UseGuards(QaCleanupGuard)`. Swagger: `X-Sleek-Sdet`, `X-QA-Name` required; responses 200 / 401 / 400.
- **Guard** — `src/data-cleanup/guards/qa-cleanup.guard.ts`: `validateSdetSecret` compares header `x-sleek-sdet` to config `SDET_SECRET_KEY`; logs QA name, method, path, body on success.
- **DTO** — `src/data-cleanup/dto/cleanup.dto.ts`: `CleanupRequestDto` with `types: CleanupType[]` and `companyId: string`. Enum: `all`, `company`, `questionnaire`, `receipt_user`, `accounting_tools`, `receipt_system`, `bank_statement_engine`.
- **Service** — `src/data-cleanup/data-cleanup.service.ts`:
  - Prefix constant `CLEANUP_COMPANY_PREFIX = 'Autotestcom -'`; `validateCompanyName` / `isCompanyAllowedCleanup` regex (case-insensitive) before `cleanupCompanyData`.
  - `cleanupCompanyData`: `companyModel.deleteOne({ company_id: companyId })`.
  - `cleanupQuestionnaire`, `cleanupReceiptUser`, `cleanupAccountingTools`, `cleanupReceiptSystem`: delegate to `sleekBackService` counterparts.
  - `cleanupBankStatementEngine`: no-op success if `COUNTRY` not `sg`/`hk`; else `bankStatementEngineService.deleteCompanyAndRelatedData(companyId, qaName)`.
  - `cleanupAll`: `Promise.allSettled` of company, questionnaire, receipt_user, accounting_tools, receipt_system, bank_statement engine; maps rejections to failed `CleanupResult` entries.
  - `validateCompanyId`: requires non-empty valid Mongo ObjectId.

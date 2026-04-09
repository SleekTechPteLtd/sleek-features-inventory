# Manage expense claim reports

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage expense claim reports |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Claim User (employee), Company Admin (batch / cut-over notifications) |
| **Business Outcome** | Organizations and claimants can maintain period-based expense claim reports whose windows align to each company’s expense-claim cut-off day, so claims can be listed, created (including backfills and company-wide batch builds), updated, and removed consistently with downstream review and publishing. |
| **Entry Point / Surface** | Coding engine REST API under `/claim-report`; consumer UIs (e.g. Sleek expense claims) not defined in this repo |
| **Short Description** | APIs list reports with filters and company cut-off metadata, create single reports or date-range creates (with overlap rules), update and delete reports, and batch-create per-user reports for a company and date range from receipt documents. Cut-off alignment uses `Company.ec_cut_off_day` via `getStartEndDateFromCutOffDay`, `createECReportByDocDocumentDate`, and `getNewOrRecentClaimReport`. A daily cron runs `ecCutOver` to advance open reports toward review and optionally email admins. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | MongoDB `claimreports`, `companies`, `documents` (Sleek receipts connection), `useractivities`, `feedbacks`; SleekBack (`getCompanyUsersFromSleekBack`, `getReceiptUsersFromSleekBack`); `EventUtils` / `ECReportEventType` (CREATED, UPDATED, DELETED); optional mailer for review notifications; document pipeline and publishing flows for items attached to reports |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | claimreports, companies, documentdetailevents |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Several routes (`GET/POST/PUT/DELETE` core CRUD, `createCompanyReports`, `updateItems`, `ecCutOver`) are not wrapped with `AuthGuard` in the controller—intended public/internal surface vs oversight is unclear. Exact product navigation for “Sleek App” is not in-repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`claim-report.controller.ts` (`@Controller('claim-report')`):**
  - `GET /` — `findAll` → `ClaimReportService.findAll` (query: company, pagination, claim user, status, currency, date range, search).
  - `POST /` — `create`; if `?byDateRange` then `createClaimReportByDateRange` from body fields, else `create`.
  - `PUT /:id` — `update`; `DELETE /:id` — `delete`; `GET /:id` — `findById`.
  - `POST /createCompanyReports` — `createCompanyReports` (batch per company date range).
  - `PUT /updateItems/:id` — `addOrRemoveReportItemsRows` then `update` (no `AuthGuard`).
  - Other routes (`addReportItem`, publish, confirm, unpublish, export, bulk migrate, currency/item updates) use `AuthGuard` where noted in controller; omitted from narrow CRUD/batch scope but same module.
- **`claim-report.service.ts`:**
  - `findAll`: aggregation on `claimReportModel`; includes `company_ec_cut_off_day` in `meta` when company has `ec_cut_off_day`.
  - `create` / `update` / `delete` / `findById`: `claimReportModel` CRUD; create/update/delete publish `ECReportEventType` events.
  - `createCompanyReports`: `getUserDocuments` (document aggregate by `receipt_user`), then `findOneAndUpdate` upsert per user with `report_items`, `report_id`, `report_title`, totals.
  - `createClaimReportByDateRange`: overlap check against open statuses; blocks overlapping current month per error messages; `createCompanyReportWithoutLineItem` with `TOREVIEW`.
  - `getStartEndDateFromCutOffDay`: derives `[reportStartDate, reportEndDate]` from cut-off day (`0` = last day of month) and reference date.
  - `createECReportByDocDocumentDate`, `getNewOrRecentClaimReport`, `getECReportByDocDocumentDate`: bind reports to cut-off-derived periods and existing open reports.
  - `ecCutOver` + `@Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT) handleCron`: companies matching yesterday’s cut-off or month-end; moves `NEW` → `TOREVIEW`; optional admin email via `sendReviewExpenseClaimsReportEmail`.
- **`claim-report.schema.ts`:** `ClaimReport` with `report_id`, `report_title`, `company_id`, `claim_user`, `start_date`, `end_date`, `status` (`ClaimReportStatus`), `report_items`, amounts, currency, comments, approval fields; embedded line-item shape in `ClaimReportItem` / `report_items`.

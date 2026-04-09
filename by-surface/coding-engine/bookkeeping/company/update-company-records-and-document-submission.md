# Update company records and document submission settings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Update company records and document submission settings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operations staff can correct or adjust company master data and document-submission state in Coding Engine while leaving a traceable audit trail for compliance when submission settings change. |
| **Entry Point / Surface** | Coding Engine API `PUT /company/update` (request body is a full `Company` shape); calling UI or gateway is not defined in this repo — actor identity is taken from the `user` header (JSON). |
| **Short Description** | Persists updates to the company document keyed by `company_id` (including `resource_users` normalization). When the payload includes `document_submission`, writes two audit entries to Sleek Auditor: a company-level “document submission” log and a BSM-oriented log with human-readable previous/new status (including snooze date when applicable). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek Auditor** (`SLEEK_AUDITOR_BASE_URL`, `SLEEK_AUDITOR_API_KEY`) — `POST` `/audit-logs`. Related: **company sync** from SleekBack/Platform (`sync`, `updateOrCreateCompany` auto-transition of past snooze dates), **Kafka** `CompanyDataToCEUpdateReceived` for other sync paths (separate from this HTTP update). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (Mongoose `Company` on `DBConnectionName.CODING_ENGINE`; default collection name `companies`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `PUT company/update` has no `@UseGuards(AuthGuard)` unlike `GET company/:companyId`; confirm gateway/middleware or network policy that enforces auth and populates `headers.user`. Whether non–document-submission field updates should also be audited (currently only when `document_submission` is present on the payload). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/company/company.controller.ts`

- **Route**: `PUT company/update` → `updateCompany(@Body() requestBody?: Company, @Request() request?)`.
- **Swagger**: `@ApiOperation({ summary: 'To update Company details by company id' })`.
- **Actor extraction**: Reads `request?.headers?.user` as JSON; builds `UserDetailAuditLog` with `userId`, `email`, `name` / `first_name` / `last_name` for `CompanyService.updateCompany`.
- **Auth**: No `@UseGuards` on this handler (contrast `GET :companyId` which uses `AuthGuard`).

### `src/company/company.service.ts`

- **`updateCompany(company, userDetails)`**: Maps `resource_users` via `mapResourseUsers`; `findOneAndUpdate` with filter `{ company_id }` and `$set` of the full `company` document.
- **Audit trigger**: `if (company.document_submission)` then:
  - **`sendAuditLogCompanyLevel`**: Builds payload with `tags: ['document_submission']`, message/event describing `document_submission_status` and timestamp, `action` “Manual update Document Submission values by {email}”, company id/name/uen; calls `sleekAuditorService.insertLogsToSleekAuditor`. Errors logged, not rethrown.
  - **`sendAuditLogForBSM`**: Maps statuses to labels (`clientSubmittingDocuments`, `noStatementsReceiptsForAGivenPeriod`, `willSubmitStatementsReceiptsLater`, `clientDidNotRespond`); formats previous vs new lines including `submit_statement_later_date` when status is “later”; `tags: ['accounting', 'bsm']`, `event` / `action` for statements reminder snooze; calls `insertLogsToSleekAuditor`. Errors logged, not rethrown.

### `src/sleek-auditor/sleek-auditor.service.ts`

- **`insertLogsToSleekAuditor`**: `HttpService.post` → `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with `actionBy`, `company`, `text` (event), `action`, `newValue.message`, `entryType`, `tags`; `Authorization: SLEEK_AUDITOR_API_KEY`.

### `src/company/models/company.schema.ts`

- **`document_submission`**: Optional embedded object on `Company` (typed as `DocumentSubmission` in interfaces).

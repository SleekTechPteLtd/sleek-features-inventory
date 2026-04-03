# Submit annual return to ACRA and manage outcome

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Submit annual return to ACRA and manage outcome |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations staff (Sleek Admin — Corpsec AR filing). |
| **Business Outcome** | After answers are prepared, staff can push the annual return to ACRA, see whether the bot submission succeeded or failed (including transaction reference and errors), download or preview ACRA output files, and reopen editing to correct data and resubmit when something goes wrong. |
| **Entry Point / Surface** | **Sleek Admin → Corpsec → AR Filing** at `/admin/corpsec/ar-filing/` with `?cid=` and `?processId=` (same page as AGM & AR workflow preparation). Submission details and retry controls render in the left column once a filing record exists; the answers panel (`ARFilingAnswers`) holds **Initiate / Re-initiate AR filing on ACRA** and confirmation using queue status. |
| **Short Description** | The parent view loads `annualReturnFiling` from the corpsec API (including `submission` for the ACRA bot). **ACRASubmissionDetails** shows transaction number, bot status (success / failed / processing), timestamps, submitter email, error text, and response files with preview/download. **ARFilingRetryButton** appears when the filing or bot submission is in a failed state: it sets status back to `staff_reviewing` via `update-status` so staff can edit schema-driven answers and submit again. First-time submit and post-failure resubmit use `submit` vs `retry` endpoints from the answers form when a prior failed transaction id exists. |
| **Variants / Markets** | **SG** (ACRA, annual return). |
| **Dependencies / Related Flows** | **Upstream**: [Prepare annual return filing from AGM and AR workflow](prepare-annual-return-filing-agm-ar-workflow.md) — same `index.js` shell, document selection, and `generate-answers`. **APIs** (`src/utils/api.js`): `GET /v2/corpsec/ar-filing/{companyId}/processes/{processId}` (state + `submission`), `POST .../submit`, `POST .../retry`, `POST .../update-status`, `GET .../queue-status`. **WFE**: `processId` ties to Camunda AGM & AR workflow; **Go to Workflow** from sibling components links to `/admin/sleek-workflow/workflow-task/`. **Backend**: ACRA bot and corpsec services (not in sleek-website). |
| **Service / Repository** | sleek-website (`src/views/admin/corpsec/ar-filing/`); corpsec v2 AR filing backend. |
| **DB - Collections** | Unknown (AR filing and submission state persist behind `/v2/corpsec/ar-filing/...`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact mapping between UI `AR_FILING_STATUSES` and backend enums for edge cases (e.g. `submitted` vs bot `processing`). Whether queue-status polling is required for all operators or only shown in the confirmation dialog. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/corpsec/ar-filing/index.js`

- **Status constants**: `AR_FILING_STATUSES` — `pending`, `staff_reviewing`, `submitted`, `success`, `failed`.
- **Load filing**: `fetchAnnualReturnFiling` → `api.getAnnualReturnFiling(companyId, processId)`; hydrates answers and polling while `pending` for answer generation (separate from ACRA submission pending).
- **Retry to edit**: `handleRetryAndUpdateAnswers` → `api.updateStatusAnnualReturnFiling` with body `{ status: AR_FILING_STATUSES.STAFF_REVIEWING }` (`staff_reviewing`), then `fetchAnnualReturnFiling`. Passed to `ARFilingRetryButton` as `onSubmit`; `isLoading` tied to `isLoadingAnswers`.
- **Render**: `ACRASubmissionDetails` receives `annualReturnFiling`, `AR_FILING_STATUSES`, `onOpenOverlay` for iframe file preview; `ARFilingRetryButton` receives `annualReturnFiling`, `onSubmit`, `isLoading`.

### `src/views/admin/corpsec/ar-filing/components/ACRASubmissionDetails.js`

- **Visibility**: Renders only when `annualReturnFiling.submission` exists and top-level `annualReturnFiling.status` is one of `submitted`, `failed`, or `success` (via `AR_FILING_STATUSES`).
- **Data shown**: `submission.status` → labels (Successfully Submitted / Submission Failed / Processing); `transactionNumber`; `message` (error); `submittedAt` (moment-formatted); `submittedBy.email`; `responseFiles[]` with `onPreviewFile` / `onDownloadFile` from `utils/fileActions` and overlay iframe for preview.

### `src/views/admin/corpsec/ar-filing/components/ARFilingRetryButton.js`

- **Hidden** when `annualReturnFiling.status === "staff_reviewing"`.
- **Shown** when `submission.status === "failed"` **or** `annualReturnFiling.status === "failed"`: **Edit Answers and Retry AR Filing** opens a confirmation dialog; confirm runs `onSubmit` (parent’s `handleRetryAndUpdateAnswers`).

### `src/views/admin/corpsec/ar-filing/ar-filling-answers.js` (submit / retry — same page, not in expand file list)

- **ACRA CTA**: Button label switches to **Re-initiate AR filing on ACRA** when status or `submission.status` is `failed`.
- **POST body**: `submitAnnualReturnFilingAnswers` vs `retryAnnualReturnFilingAnswers` — if `submission.transactionId` exists and either status is failed, uses **retry** with `{ answers: formData }`; else **submit**.
- **Pre-submit**: `getAnnualReturnFilingQueueStatus` loaded when confirming submission (queue awareness before firing submit/retry).

### `src/utils/api.js`

- Endpoints: `POST .../processes/{processId}/submit`, `POST .../processes/{processId}/retry`, `POST .../processes/{processId}/update-status`, `GET .../processes/{processId}/queue-status`.

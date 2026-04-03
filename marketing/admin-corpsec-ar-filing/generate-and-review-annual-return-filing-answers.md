# Generate and review annual return filing answers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Generate and review annual return filing answers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Internal staff (Sleek Admin; corpsec workflow operators) |
| **Business Outcome** | Staff can produce regulator-ready structured answers for Singapore annual return (ACRA) filing by running AI extraction on chosen documents, then review, edit, and attest before submission. |
| **Entry Point / Surface** | Sleek Admin — **Corpsec** → **Annual Return Filing** (`sidebarActiveMenuItemKey` `corpsec`, `sidebarActiveMenuSubItemKey` `ar-filing`; route `/admin/corpsec/ar-filing/` with optional `?cid=` and `processId=`; webpack entry `admin/corpsec/ar-filing` → `src/views/admin/corpsec/ar-filing/index.js`) |
| **Short Description** | Staff pick a company and an **AGM & AR** Camunda workflow, select workflow-linked and/or manually uploaded documents, and click **Generate Answers** to POST extraction; the UI polls until answers are ready, shows a timed progress bar, and renders answers in a JSON-schema form with AI reasoning and confidence. In **staff_reviewing**, staff edit values (tracking `editedBy` / `editedAt`), save drafts, then confirm a statutory declaration and submit or retry to ACRA; queue position and estimated wait appear in the confirmation dialog. |
| **Variants / Markets** | **SG** — ACRA submission copy and workflow integration imply Singapore annual return context. |
| **Dependencies / Related Flows** | **Upstream:** `getCompanyWorkflows` (`api-wfe`) filters workflows titled **AGM & AR**; AGM/AR workflow tasks link to this page (`ar-filing-bot.js`). **CMS:** `ar_filing` platform feature supplies `response_format.schema` for the answer form and optional `document_exclusion_regex_patterns` for auto-selection. **APIs (backend):** `GET/POST …/v2/corpsec/ar-filing/:companyId/processes/:processId` and siblings (`generate-answers`, `update-answers`, `submit`, `retry`, `update-status`, `queue-status`, `documents`, `upload-document`). **Files:** `getFileDetails`, `uploadARFilingDocument`, `deleteFile`. |
| **Service / Repository** | **sleek-website:** `src/views/admin/corpsec/ar-filing/index.js`, `ar-filling-answers.js`, `components/AnswerGenerationActions.js`, `ar-filing-progress-bar.js`; `src/utils/api.js` (corpsec AR filing endpoints). **Backend** for persistence, AI pipeline, and ACRA integration is not in this repo. |
| **DB - Collections** | Unknown — AR filing records and answers are persisted via `/v2/corpsec/ar-filing/…` (no Mongo schemas in sleek-website). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/corpsec/ar-filing/index.js`

- **Layout:** `AdminLayout` with corpsec / ar-filing sidebar; `ARFilingAnswers` + `ARFilingProgressBar` in right column when `showRightCard`.
- **Config:** `getPlatformConfig` → `ar_filing` feature → `answerSchema` from `value.response_format.schema`; `estimatedAnswerGenerationTime` default 120000 ms.
- **Workflows:** `fetchWorkflowsForCompany` → `getCompanyWorkflows({ companyId, includedWorkflows: ["camunda"] })`, keeps workflows whose title includes `AGM_AR_TITLE` (`"AGM & AR"`), labels with financial year end; URL sync `cid`, `processId`.
- **Load filing:** `getAnnualReturnFiling` → if `status === "pending"`, sets `answerGenerationInitiatedAt`, `showRightCard`, `startAnswerPolling` (2s interval after remaining estimated time). `getAnnualReturnFilingDocuments` merges `partiallySignedFileIds`, `signedFileIds`, `financialStatementFileIds` into workflow document list; `fetchSourceDocuments` uses `getFileDetails` per id; `shouldAutoSelectDocument` respects CMS regex exclusions.
- **Generate:** `handleGenerateAnswers` → `generateAnnualReturnFilingAnswers` with body `{ fileIds, manuallyUploadedFileIds }`; polling until status leaves `pending`. `canGenerateAnswers` requires selected docs and status in `staff_reviewing`, `pending`, or undefined.
- **Retry editing:** `handleRetryAndUpdateAnswers` → `updateStatusAnnualReturnFiling` with `status: "staff_reviewing"`, then refetch.

### `src/views/admin/corpsec/ar-filing/components/AnswerGenerationActions.js`

- Renders **Generate Answers** when `canGenerateAnswers`; shows last `answersGeneratedAt` (moment) and optional `annualReturnFiling.ai.payload` model and prompt version badges.

### `src/views/admin/corpsec/ar-filing/ar-filing-progress-bar.js`

- Indeterminate-style bar during `isLoading`: progress from elapsed time vs `duration`, caps at 99% with “Taking longer than expected…”, then 100% / “Complete!” when loading ends.

### `src/views/admin/corpsec/ar-filing/ar-filling-answers.js`

- **Form:** `@rjsf/core` + `validator-ajv8`; schema from CMS.
- **`AnswerObjectField`:** For objects with `value`, `reasoning`, `confidence` — shows AI vs staff-edited badges, collapsible reasoning, confidence styling; edits set `editedAt`, `editedBy` (user email). Array values use Blueprint `TagInput`.
- **Edit gate:** `editable` when `annualReturnFilingData.status === "staff_reviewing"`.
- **Save:** `updateAnnualReturnFilingAnswers` with full `answers` JSON.
- **Submit:** `handleSubmitClick` validates → confirmation dialog with ACRA-style declaration; `getAnnualReturnFilingQueueStatus` shows queue position and `estimatedProcessingTimeMinutes`. Submit: `submitAnnualReturnFilingAnswers` or `retryAnnualReturnFilingAnswers` when prior submission failed and `transactionId` exists.
- **Copy:** Header “Review and edit AI-generated answers for the Annual Return filing” when editable; primary button “Initiate AR filing on ACRA” / “Re-initiate AR filing on ACRA” when submission failed.

### `src/utils/api.js`

- `GET ${getBaseUrl()}/v2/corpsec/ar-filing/${companyId}/processes/${processId}/documents`
- `GET …/processes/${processId}`
- `POST …/generate-answers`
- `POST …/update-answers`
- `POST …/submit`
- `POST …/retry`
- `POST …/update-status`
- `GET …/queue-status`
- `POST …/upload-document`

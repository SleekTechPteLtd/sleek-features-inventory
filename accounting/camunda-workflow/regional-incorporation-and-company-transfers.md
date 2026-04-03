# Regional incorporation and company transfers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Regional incorporation and company transfers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client (company admin), Operations User (Sleek staff completing workflow tasks), System (automations, Camunda callbacks) |
| **Business Outcome** | Clients can form companies in Singapore, Hong Kong, and the UK, or transfer an existing Singapore company to Sleek, with statutory and automated documents generated, signed, and tracked through a guided process to live status. |
| **Entry Point / Surface** | Sleek Back HTTP API under `POST /v2/sleek-workflow/…` with `userService.authMiddleware` (and `getWorkflowMiddleware` where applied): `sg-incorporation`, `hk-incorporation`, `uk-incorporation`, `sg-transfer` (`start`, task completion routes); document listing endpoints for SG pre/post incorporation and automated variants; `GET …/company-workflows/:business_key/automated-documents/:fetch_mode` and `…/circulated-automated-documents/:fetch_mode` for multi-tenant document counts and circulated docs; UK admin-oriented `GET /uk-incorporation/categories` and `POST /uk-incorporation/regenerate-documents`. Client apps and operator tooling consume these routes while users progress Camunda process instances. |
| **Short Description** | Starts and advances region-specific Camunda workflows (`sg-incorporation`, `hk-incorporation`, `uk-incorporation`, `sg-transfer`) via the Camunda Pilot API: persists `CompanyWorkflow`, updates company status and related data on task completion, orchestrates KYC/RAF, document generation (`RequestInstance`), mail, risk rating, and UK Companies House steps. SG handlers expose rich pre/post incorporation document fetch and generation; `automated-documents.js` aggregates document counts and circulated automated documents by workflow and fetch mode (SG, SG transfer, HK). |
| **Variants / Markets** | SG, HK, UK |
| **Dependencies / Related Flows** | Sleek Camunda Pilot (`config.sleekCamundaPilotBaseApiUrl` start/complete-task); KYC and risk assessment (`RiskAssessmentReport`, RAF templates); SleekSign and document analyzer services; mailer; auditor logging; subscriptions and app features; UK `uk-incorporation-service` (Companies House retrieval, document generation, emails); HK e-registry / NNC1 and articles flows; SG ACRA-related steps; SBA onboarding hooks where combined with RAF; `sleek-onboarding` UK accounting questionnaire after CH submission. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyworkflows`, `companies`, `companyusers`, `users`, `requestinstances`, `riskassessmentreports`, `files`; UK dashboard aggregation also joins `companyworkflows` via aggregation pipeline |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | UK `taskAction` completes the Camunda task before `updateCompanyWorkflowTaskToCompleted` and switch side effects (order differs from SG/HK transfer pattern); confirm intentional. Exact customer-app navigation labels for each market are not in these handlers. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/camunda-workflow.js` (routing)

- Base path: `/v2/sleek-workflow` (`app-router.js`).
- SG incorporation: `POST /sg-incorporation/start`, `POST /sg-incorporation/:taskId/:taskName`, `GET /sg-incorporation/:business_key/pre-incorp-documents`, `post-incorp-documents`, `pre-incorp-automated-documents`, `post-incorp-automated-documents`.
- SG transfer: `POST /sg-transfer/start`, `POST /sg-transfer/:taskId/:taskName`.
- HK: `POST /hk-incorporation/start`, `POST /hk-incorporation/:taskId/:taskName`, `POST /hk-incorporation/name-unavailability`.
- UK: `POST /uk-incorporation/start`, `POST /uk-incorporation/:taskId/:taskName`, `GET /uk-incorporation/categories`, `POST /uk-incorporation/regenerate-documents`.
- Automated docs (multi-tenant): `GET /company-workflows/:business_key/automated-documents/:fetch_mode`, `GET /company-workflows/:business_key/circulated-automated-documents/:fetch_mode`.
- Guards: `userService.authMiddleware` on listed routes; UK categories/regenerate use standard authenticated POST/GET (same middleware stack as siblings).

### `controllers-v2/handlers/camunda-workflow/sg-incorporation.js`

- `start` → `initiateIncorporationWorkflow` → `POST ${sleekCamundaPilotBaseApiUrl}/sg-incorporation/start`; creates `CompanyWorkflow` with `workflow_type` SG incorporation, sets company status `PROCESSING_INCORP_TRANSFER`, audit log.
- `taskAction` → maps many `task_name` values to Camunda `complete-task`; side effects include KYC, RAF, ACRA name steps, pre/post incorporation documents and signatures, incorporation step (`triggerIncorporationStepCompletion`), registers, sleek secretaries, `updateCompanyStatus`, emails, `analyzeDocumentForSending`, dashboard launch helpers.
- `fetchPreIncorpDocuments` / `fetchPostIncorpDocuments` / `fetchPreIncorpAutomatedDocuments` / `fetchPostIncorpAutomatedDocuments`: load `CompanyWorkflow` by `business_key`, `CompanyUser`/`User`/`File`, `RequestInstance` with template IDs from config; generate documents via `generateDocumentToSignRequestInstance` where needed; persist `data.generated_documents.pre_incorp_documents` / `post_incorp_documents` on `CompanyWorkflow`.

### `controllers-v2/handlers/camunda-workflow/hk-incorporation.js`

- `initiateIncorporationWorkflow` → `POST …/hk-incorporation/start`; `CompanyWorkflow` with HK workflow type; optional RAF template in data.
- `taskAction`: tasks include `risk_assessment`, `company_members`, `incorporation_raf`, `name_availability`, `share_info`, `ctc_id_documents`, e-registry steps, `form_nnc1_via_e_registry`, `articles_of_association`, `signed_form_nnc1`, `incorporation`, `post_incorp_documents`, `registers`; updates status, emails, `redirectToLiveDashboard`, `analyzeDocumentForSending` with HK-specific entry keys, officer appointment history.

### `controllers-v2/handlers/camunda-workflow/uk-incorporation.js`

- `start` → UK workflow start + `triggerAutomation(…MANUAL_START_OF_UK_INCORPORATION)`; `initiateIncorporationWorkflow` persists `CompanyWorkflow` and links company `incorporation_workflow`.
- `taskAction`: tasks `kyc_verification`, `company_details`, `people_details`, `pre_incorporation_documents`, `submit_to_companies_house`, `post_incorporation_documents`, `emails_and_fraud_protection`; delegates to `ukIncorporationService` for document generation, Companies House retrieval, emails, auto-complete tasks; `sendQuestionnaireWithAccountingSubscription` for UK onboarding questionnaire.
- `companyWorkflowCategories`: aggregates companies with UK incorporation workflow for operator dashboard buckets (AML, CH submission, etc.).
- `regenerateDocuments`: body `document_type` → regenerate pre/post CH documents or retrieve CH documents.

### `controllers-v2/handlers/camunda-workflow/sg-transfer.js`

- `start` / `validateExcludedSubscription`: same sole-prop and subscription guards pattern as SG incorporation.
- `initiateIncorporationWorkflow` → `POST …/sg-transfer/start`; `CompanyWorkflow` with `workflow_type` SG transfer, links `RiskAssessmentReport` to workflow, sets company `PROCESSING_INCORP_TRANSFER`.
- `taskAction`: tasks `company_members`, `transfer_raf`, `collect_details_previous_provider`, `transfer_documents`, `transfer_filing`, `biz_profile_for_transfer`, `registers_for_transfer`; risk rating, RAF completion, `autoAssignSleekSecretaries`, `analyzeDocumentForSending` for SG transfer circulation entrypoint, `updateCompanyStatus` to live on registers.

### `controllers-v2/handlers/camunda-workflow/automated-documents.js`

- `getAutomatedDocuments`: validates `business_key`, `fetch_mode`; `getIncorporationDocumentCount(business_key, fetch_mode)`.
- `getCirculatedAutomatedDocuments`: resolves tracked `RequestInstance` template ID sets from constants by `fetch_mode` (`pre_incorporation_documents`, `post_incorporation_documents`, `sg_transfer_documents`, HK `articles_of_association`, `post_incorp_documents`, `ctc_id_documents`); updates `CompanyWorkflow.data.generated_documents.${fieldKey}` with matching request instance ids; returns `documentsToSign`.

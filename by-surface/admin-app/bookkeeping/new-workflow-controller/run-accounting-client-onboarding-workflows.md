# Run accounting client onboarding workflows

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Run accounting client onboarding workflows |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (staff with `manage_workflows` read/edit); authenticated via `userService.authMiddleware` |
| **Business Outcome** | Staff can start an accounting onboarding process for a client company and advance it through questionnaire approval, Xero setup, Receipt Bank setup, verification, and final onboarding completion—keeping the bookkeeping onboarding pipeline moving in the workflow engine. |
| **Entry Point / Surface** | Sleek Back HTTP API: router mounted at `/v2/admin/workflow` (`app-router.js`). Accounting onboarding: `POST /v2/admin/workflow/api/tasks/accounting-onboarding/start`; `POST /v2/admin/workflow/api/tasks/accounting-onboarding/:processId/:taskName/:taskId`. |
| **Short Description** | Admin-only endpoints proxy to the legacy Sleek Workflow Engine (WFE) at `config.sleekWfeBaseUrl` to start the `accountingonboarding` process and to post step updates that map UI fields to WFE task payloads (questionnaire, Xero, Receipt Bank, verification, onboarding completion). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Sleek WFE** REST API (`/workflow/api/tasks/accountingonboarding/...`); HTTP client `postResource` in `controllers-v2/utlities/request-helper.js` (fixed service token + `origin-country` headers). A separate **Camunda**-backed accounting onboarding path exists under `controllers-v2/handlers/camunda-workflow/accounting-onboarding.js` for environments using Camunda workflow types—related but not the code paths listed for this feature line. Downstream: bookkeeping setup, Xero, Receipt Bank, client verification steps. |
| **Service / Repository** | sleek-back (orchestration); Sleek WFE (workflow execution and persistence) |
| **DB - Collections** | None in these sleek-back handlers; workflow state and task data are owned by the WFE service. Unknown whether WFE shares Mongo collections with sleek-back. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether all regions use WFE vs Camunda for this flow in production. Error paths in handlers only log and may not always send an HTTP response to the client (`catch` blocks). Exact admin UI product name for this surface. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/new-workflow-controller.js`

- Router: **`userService.authMiddleware`** on all routes; **`accessControlService.can("manage_workflows", "read")`** (GET) and **`can("manage_workflows", "edit")`** (POST/PUT).
- Imports **`accountingOnboarding`** from `controllers-v2/handlers/workflow/accounting-onboarding`.
- **`POST /api/tasks/accounting-onboarding/start`** → **`startAccountingOnboarding`**.
- **`POST /api/tasks/accounting-onboarding/:processId/:taskName/:taskId`** → **`updateAccountingOnboardingStep`**.

### `app-router.js`

- **`router.use("/v2/admin/workflow", require("./controllers/admin/new-workflow-controller.js"))`** — full base path for routes above.

### `controllers-v2/handlers/workflow/accounting-onboarding.js`

- **`PROCESS_NAME`**: `accountingonboarding`.
- **`startAccountingOnboarding`**: **`postResource`** to **`${config.sleekWfeBaseUrl}/workflow/api/tasks/${PROCESS_NAME}/start/`** with body **`company_id`**, **`company_name`** from `req.body`.
- **`updateAccountingOnboardingStep`**: **`postResource`** to **`.../workflow/api/tasks/${PROCESS_NAME}/${processId}/${taskName}/${taskId}/`** with **`requestJsonMapping`** keyed by **`taskName`**:
  - **`complete_questionnaire`**: `questionnaire_approved`, `questionnaire_completed_date`
  - **`complete_xero_setup`**: `xero_setup_approved`
  - **`complete_receipt_bank_setup`**: `receipt_bank_approved`
  - **`complete_verification`**: `verification_approved`
  - **`complete_onboarding`**: `onboarding_complete_approved`, `onboarding_choice_selected`, `onboarding_date`
- Common fields: **`approved`** from body; optional **`questionnaireCompletedDate`**, **`choiceSelected`**, **`onboardingDate`**.

### `controllers-v2/utlities/request-helper.js`

- **`postResource`** / **`getDefaultHeaders`**: outbound calls use configured headers including **`Authorization`** token and **`origin-country`** from config (service-to-service integration with WFE).

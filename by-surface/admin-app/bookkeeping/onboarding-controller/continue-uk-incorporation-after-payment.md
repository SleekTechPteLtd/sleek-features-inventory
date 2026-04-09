# Continue UK incorporation after payment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Continue UK incorporation after payment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, System |
| **Business Outcome** | After pre-payment is complete and eligibility holds, the UK incorporation path moves forward with KYC invitation, AML risk and officer checks, and automatic start of the Camunda incorporation workflow so the company is not stuck after payment. |
| **Entry Point / Surface** | API `POST /onboarding/process-post-payment` (authenticated via `userService.authMiddleware`); related admin path `POST /onboarding/:companyUserId/resend-invite` (Sleek Admin) to resend Sumsub KYC invite |
| **Short Description** | The post-payment handler loads the company, checks status `PROCESSING_INCORP_TRANSFER`, microservice onboarding, completed pre-payment (`pre_payment` false), and at least one subscription, then delegates to UK onboarding: for valid UK incorporation origins it sends a Sumsub KYC invite to the company admin when needed, runs `determineCompanyAndOfficersRiskLevel` and `determineCompanyOfficerKYCChecks` at the post-payment entrypoint, and calls `startIncorporationWorkflow` to auto-start incorporation (errors on workflow start are logged, not thrown). |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | App feature `billing_service` / `tenant_config` (country `GBR`) for origin validation; `AUTO_START_INCORP_WORKFLOW` entrypoints; Sumsub invite (`send-invite`); `invitation-service` (invitation status); `uk-incorporation-risk-level-service` (AML risk and officer KYC checks, `POST_PAYMENT` entrypoint); `startIncorporationWorkflow` / Camunda (`services/camunda-workflow/sg-incorporation/incorporation-initiator`); company must be incorporation (not transfer) and `shares` company type per `isIncorporation`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (read/update via services in flow), `companyusers` (owner lookup, risk/officer logic); invitation-related collections touched by `invitation-service` (exact names not enumerated in files reviewed) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `processPostPayment` Joi allows `UK_MANUAL_API_CALL`, but `validateOrigin` in `uk-onboarding.js` only validates LC website payment, CA website payment, and `UK_MANUAL_COMPANY_STATUS_TRANSITION_TO_PIT` for GBR—`UK_MANUAL_API_CALL` never returns true there, so the incorporation branch may not run for that entrypoint unless another path exists. Whether `updateAccountingQuestionnaire` is invoked from this flow is out of scope for the controller path reviewed (not called from `processPostPayment` in `uk-onboarding.js`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router mount:** `app-router.js` mounts onboarding controller at `/onboarding`.
- **Post-payment API:** `POST /process-post-payment` — `userService.authMiddleware`, body `{ company_id, entrypoint }` validated to `AUTO_START_INCORP_WORKFLOW.UK_MANUAL_COMPANY_STATUS_TRANSITION_TO_PIT` or `UK_MANUAL_API_CALL` — `modules/sleek-onboarding/controller/onboarding-controller.js` (`processPostPaymentObj`, `processPostPayment`).
- **Eligibility gate (controller):** `Company.findById`, `loadSubscriptions`; requires `company.status === PROCESSING_INCORP_TRANSFER`, `company.microservice_enabled`, `!company.pre_payment`, `company.subscriptions.length > 0` — same file.
- **UK orchestration:** `ukOnboarding.processPostPayment(company._id, value.entrypoint)` — maps to `processPostPayment(company_id, origin, data)` in `modules/sleek-onboarding/services/uk-onboarding.js` (third arg optional).
- **Origin validation:** `validateOrigin` uses app feature `billing_service` → `tenant_config.countryCode === 'GBR'` and specific `AUTO_START_INCORP_WORKFLOW` values with Beta / `pre_payment` / status / `incorporation_workflow` conditions for CA and manual transition paths — `uk-onboarding.js`.
- **Incorporation vs transfer:** `isIncorporation(company)` requires `!company.is_transfer` and `company.company_type` lowercased `'shares'`.
- **KYC invite:** `sendInvite(companyAdmin)` — optional Sumsub invite via `sumsubService.sendUserSumsubInvite`, auth token, `invitationService.setInvitationStatus` to pending when KYC not in approved/resubmission/rejected — `uk-onboarding.js`.
- **AML / officer checks:** `ukIncorporationRiskLevelService.determineCompanyAndOfficersRiskLevel` and `determineCompanyOfficerKYCChecks` with `DERTERMINE_RISK_LEVEL_ENTRYPOINT.POST_PAYMENT` — `uk-onboarding.js`, implementation in `services/camunda-workflow/uk-incorporation/uk-incorporation-risk-level-service.js`.
- **Workflow auto-start:** `startIncorporationWorkflow(company_id, origin)` in try/catch with error logging — `uk-onboarding.js`, imported from `services/camunda-workflow/sg-incorporation/incorporation-initiator`.
- **Admin resend (related):** `POST /:companyUserId/resend-invite` — `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`, resolves corporate shareholder parent name, `ukOnboarding.sendInvite(companyUser)` — `onboarding-controller.js`.

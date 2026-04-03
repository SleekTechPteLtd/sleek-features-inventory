# Record SBA business account decisions on risk assessment

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Record SBA business account decisions on risk assessment |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Capture whether a Singapore business account (SBA) application was approved or rejected before or after onboarding on the KYC risk assessment record, and notify compliance by email when the product flag is on so AML/KYC oversight stays aligned with account decisions. |
| **Entry Point / Surface** | Sleek admin / operations flows on the KYC risk assessment form — API `POST /v2/risk-assesment-form/sba-application/:companyId` (authenticated); readback via `GET /v2/risk-assesment-form/:companyId` and `sba_pre_onboarding` / `sba_post_onboarding` on `POST /v2/risk-assesment-form/compute-score/:companyId` responses. |
| **Short Description** | Operators submit **pre-onboarding** or **post-onboarding** SBA outcomes (`status`, `reason`, `type`) on the company’s risk assessment form document. The backend stores them under `sba_pre_onboarding` or `sba_post_onboarding` with the acting user as **approver**. When app feature `kyc_raf` has `raf_sba_send_email` enabled, it sends templated emails to compliance and business-account recipients via `sendSBAEmailNotificationToCompliance` (pre-approve/reject, post-revoke, and post-approve when a requestor is supplied in that code path). |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | **Upstream:** App feature `kyc_raf` (`props.raf_sba_send_email`); same `RiskAssesmentForm` document as [complete KYC risk assessment scoring](./complete-kyc-risk-assessment-scoring.md). **Downstream:** `mailer-vendor` with templates `KYC_RAF_SBA_PRE_ONBOARDING_APPROVED`, `KYC_RAF_SBA_PRE_ONBOARDING_REJECTED`, `KYC_RAF_SBA_POST_ONBOARDING_REVOKED`, `KYC_RAF_SBA_POST_ONBOARDING_APPROVED`; `config.compliance.emails`, `config.business_account.emails`; Sleek Admin URLs for company business account and workflow task. **Schema:** `constants/risk-assesment-form.js` enums `SBA_TYPE`, `SBA_STATUS`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `riskassesmentforms` (Mongoose model `riskAssesmentForm` — fields `sba_pre_onboarding`, `sba_post_onboarding` subdocuments with `approver` ref to `User`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `sendSBAEmailNotificationToCompliance` only sets `KYC_RAF_SBA_POST_ONBOARDING_APPROVED` when `requestor` is passed, but `POST .../sba-application/:companyId` does not pass `requestor` — confirm whether post-onboarding approved emails are intentionally unsupported from this route or filled elsewhere. `GET /:companyId` populates only `sba_pre_onboarding.approver`, not `sba_post_onboarding.approver` — intentional or oversight? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/risk-assesment-form.js`

- **`POST /sba-application/:companyId`** — `userService.authMiddleware`; body `type` (`pre-onboarding` → `sba_pre_onboarding`, else `sba_post_onboarding`), `status`, `reason`; builds `payload` with `approver: req.user._id`. Creates `RiskAssesmentForm` with only the SBA subdocument if none exists, else updates `riskAssesment[type]`. Reads `appFeatureUtil.getAppFeaturesByName("kyc_raf", "general")`, `getAppFeatureProp(..., "raf_sba_send_email")`; if `enabled`, calls `kycRAFServices.sendSBAEmailNotificationToCompliance({ companyId, isPostOnboarding, isApproved: status === 'approved', reason })`. Returns updated form with `sba_*` populated.
- **`GET /:companyId`** — returns `RiskAssesmentForm.findOne({ company })` with `populate('sba_pre_onboarding.approver')` only.
- **`POST /compute-score/:companyId`** — response includes `sba_post_onboarding`, `sba_pre_onboarding` from a fresh `RiskAssesmentForm.findOne` with both approver fields populated (lines 153–155, 196–200).

### `services/kyc-risk-assesment-form.js`

- **`sendSBAEmailNotificationToCompliance`**: Loads `Company` with `incorporation_workflow`; builds Sleek Admin `createSBAUrl` (`/admin/company-overview/?cid=...&currentPage=Business+Account`) and `workflowUrl`; selects template by pre/post onboarding and approved/rejected; variables `receiver_name`, `company_name`, `button_url`, `reason`; `mailerVendor.sendEmail` to `config.customer.emails` with BCC `config.business_account.emails` plus optional `requestor.email`.

### `schemas/risk-assesment-form.js`

- **`sbaSchema`**: `approver` → `User`, `status` enum `SBA_STATUS`, `reason` string, `type` enum `SBA_TYPE`; timestamps.
- **`riskAssesmentFormSchema`**: `sba_pre_onboarding`, `sba_post_onboarding` embedded `sbaSchema`.

### `constants/risk-assesment-form.js`

- **`SBA_TYPE`**: `pre-onboarding`, `post-onboarding`.
- **`SBA_STATUS`**: `approved`, `rejected`, `pending`.

### Routing

- **`app-router.js`**: `router.use("/v2/risk-assesment-form", require("./controllers-v2/risk-assesment-form"))`.

### Tests

- **`tests/controllers-v2/risk-assesment-form/sba-application.js`**: covers `POST /v2/risk-assesment-form/sba-application/:companyId`.

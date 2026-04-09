# Complete KYC risk assessment scoring

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Complete KYC risk assessment scoring |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Produce a defensible AML/KYC risk rating for a company from questionnaire answers, keep an audit trail, and surface the result to compliance when policy requires. |
| **Entry Point / Surface** | Sleek App / admin workflows using KYC RAF — API `POST /v2/risk-assesment-form/compute-score/:companyId` (authenticated); questionnaire content and weights from app feature `kyc_raf` |
| **Short Description** | Loads the RAF version for the company, merges manual answers with optional automated answers from `company-raf-service`, computes per-section and total weighted scores, maps the total to a risk band via configurable scales, persists the form and logs when saving, updates `Company.risk_rating`, writes company risk rating history rows, optionally emails compliance, and returns sections, scores, logs, and histories to the client. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | App features: `kyc_raf` (questionnaire, automation flags, email toggles), `risk_assessment_form_standalone` (risk rating scale via `getRiskRatingScale`); `company-raf-service` (subscription/Xero/Comply Advantage/PEP/custom checker automation); mailer vendor and `config.compliance.emails`; `Company` / `CompanyUser` for risk rating sync and pending enhanced logs; adjacent routes in same controller for SBA approval and customer acceptance (out of scope for this capability but same module). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `riskassesmentforms` (Mongoose model `riskAssesmentForm`), `riskassesmentformlogs` (`riskAssesmentFormLogs`), `companyriskratinghistories` (`companyRiskRatingHistory`), `companies` (field `risk_rating` and related company context) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact product navigation path in Sleek App vs admin-only; market-specific rollout is config-driven in app features but not enumerated in code paths reviewed. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **HTTP surface (compute & persist):** `POST /compute-score/:companyId` with `userService.authMiddleware`; query `isSaved=true` controls persistence; body `sections`, `edit_automated_answers`, `not_all_members_verified` — `controllers-v2/risk-assesment-form.js`.
- **Questionnaire & version:** `appFeatureUtil.getAppFeaturesByName("kyc_raf", "general")`, `raf_questionaire` matched to `company.raf_version`; section weights `weightage_percentage`, titles, parent groups from config — same controller + `kyc-risk-assesment-form.js` (`getQuestionaire`, `getWeighedScore`, `getTotalScore`).
- **Automation:** When `raf_automation` is enabled, `companyRafService.getRiskAssesmentFormAutoAnswer(companyId, req.body)` supplies answers; merge logic respects `edit_automated_answers` and `hasPendingUpdate` — `controllers-v2/risk-assesment-form.js`, `services/company-raf-service.js` (`getRiskAssesmentFormAutoAnswer`, checker functions, Comply Advantage, subscriptions, etc.).
- **Persistence:** Create/update `RiskAssesmentForm` with `sections`, `version`, optional `total_weighted_score` and `risk_rating` on save — `schemas/risk-assesment-form.js`.
- **Audit logs:** `kycRAFServices.generateLogs` comparing prior snapshot to computed sections; `RiskAssesmentFormLogs.create` when saving or automation update; optional structured `reason` when popup config enabled — `services/kyc-risk-assesment-form.js`, `schemas/risk-assesment-form-logs.js`.
- **Risk band:** `getRiskRatingFromTotalWeightedScore(total_weighted_score)` uses `getRiskRatingScale` from `constants/company-risk-rating.js` (app feature `risk_assessment_form_standalone`) — `services/kyc-risk-assesment-form.js`.
- **Company rating:** `updateCompanyRiskRating(company, risk_rating)` sets `company.risk_rating` — `services/kyc-risk-assesment-form.js`.
- **History:** `CompanyRiskRatingHistory.create` for score and rating actions; `updatePendingRiskRatingLogs` ties pending rows to approved members — `schemas/company-risk-rating-history.js`, `kyc-risk-assesment-form.js`.
- **Compliance email:** `sendEmailNotificationToCompliance` when new form created with automation + `raf_auto_send_email`, templates `KYC_RAF_AUTO_*` — `kyc-risk-assesment-form.js`.

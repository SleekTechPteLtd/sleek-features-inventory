# Trigger and chase company user KYC refresh

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Trigger and chase company user KYC refresh |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User / Sleek Admin (manual start, chaser sends, workflow); System (risk-based eligibility, CDD batch auto-trigger, chaser ladder timing); Customer (completes refresh via invitation link and submission flow) |
| **Business Outcome** | Customer identity and risk data stay current for AML and periodic compliance by re-verifying individuals linked to a company on a schedule driven by risk and last verification date. |
| **Entry Point / Surface** | Sleek API: `POST` `/v2/sleek-workflow/kyc/startKycRefresh?companyUserId=` (admin-authenticated workflow); `POST` `/v2/company-users/:companyUserId/kyc-refresh` (submission / status update); `POST` `/v2/company-users/:companyUserId/send-kyc-refresh-email-chaser` (manual chaser step); customer email links to Sleek website invitation with `isFromKycRefresh=true` |
| **Short Description** | When the `kyc_refresh` app feature is enabled, the service can trigger a refresh (manual, automated risk-window, or CDD batch), record `kyc_refresh` state and KYC history, snapshot user data source history, notify the customer and compliance by email, and advance a timed chaser sequence (user → company admin → support). Submission updates history, data sources, proof-of-address, and opens a Zendesk ticket for compliance review. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `app-features-util` (`kyc_refresh` general feature; Onfido/MyInfo/manual props); `mailer-vendor` (REFRESH_KYC_* templates); `company-user-kyc-history`; `user-data-source-history`; `kyc-risk-assesment-form` (`computeRiskRatingScore` on non-manual trigger paths); `zendesk-service/zendesk-ticket-service` (`createKYCRefreshSubmittedZendeskTicket`); `user-service` (token for invitation link); `proof-of-address-service`; CDD bulk / `autoTriggerKycRefresh` for company admin after batch processing; Camunda workflow handler for manual start |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers` (`kyc_status`, `kyc_history`, embedded `kyc_refresh` Mixed: status, dates, `userDataSource`, `chaser_email_history`, flags); `users` (invitation token, proof/expiry fields, `last_updated_verify_profile` flags); `userdatasourcehistories`; `companies` (corporate shareholder compare path); `customeracceptanceforms` (PEP compare path) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST` `/v2/company-users/:companyUserId/kyc-refresh` and `send-kyc-refresh-email-chaser` use `authMiddleware` only (not `adminOrLoggedCompanyUserAuthMiddleware`); confirm whether callers are always trusted internal apps or if additional scoping is required. JSDoc on `isValidForKYCRefresh` mentions different day thresholds than `CDD_BATCH_KYC_REFRESH_DAYS` (all 365 in code)—confirm operational intent. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Service** (`services/kyc-refresh-service.js`): `performKYCRefresh` — gated by `getAppFeaturesByName("kyc_refresh","general")`; sets `kyc_status` to refresh-triggered, builds `kyc_refresh` (`TRIGGERED`, `userDataSource`, manual/automation flags); `updateCompanyUserKycHistory`, `addUserDataSourceHistory`; emails customer (`REFRESH_KYC_CLIENT` / `_NEW`) and compliance (`REFRESH_KYC_ADMIN`); `isPerformKYCRefresh` uses risk level and days since last risk/KYC anchor (1y/2y/3y by high/medium/low); `isValidForKYCRefresh` / `getLastKycDateAndSource` / `autoTriggerKycRefresh` for CDD-style batch triggers on company admin; `getRefreshKYCDetails` + `performChaserEmails` + `sendKycRefreshEmailChaser` for chaser ladder (`EMAIL_CHASER_*` from `constants/kyc-refresh-statuses`); `updateKycRefreshStatus` — body `status`, `new_data_source`, optional proof dates; clears `kyc_status` for downstream flow, updates `kyc_refresh.status`, user fields, KYC history with `is_kyc_refresh_submitted`, `updateUserDataSourceHistory`, `updateApplicantAddressCheckProofOfAddress`, Zendesk ticket creation; field-diff helpers for “no changes” detection vs snapshot.
- **Schema** (`schemas/company-user.js`): `kyc_refresh` as `Schema.Types.Mixed`; standard KYC fields `kyc_status`, `kyc_history`, `kyc_risk_level`, `kyc_risk_level_details`, `invitation_token`, etc.
- **Routes** (`controllers-v2/company-user.js`): `buildPostRoute("/:companyUserId/kyc-refresh", updateKycRefreshStatus)` and `buildPostRoute("/:companyUserId/send-kyc-refresh-email-chaser", sendKycRefreshEmailChaser)` — both `userService.authMiddleware` only.
- **Workflow** (`controllers-v2/camunda-workflow.js`, `controllers-v2/handlers/camunda-workflow/kyc.js`): `buildAuthenticatedPostRouteAdmin("/kyc/startKycRefresh", kyc.startKycRefresh)` — loads `CompanyUser` (approved or refresh with final chaser sent), blocks nominee directors, calls `performKYCRefresh(..., true, req.user._id, entrypoint)` and optionally `computeRiskRatingScore` for `MANUAL`.
- **Tests** (`tests/services/kyc-refresh/*`, `tests/controllers-v2/kyc-refresh/update-kyc-refresh.js`) — API paths and chaser status expectations.

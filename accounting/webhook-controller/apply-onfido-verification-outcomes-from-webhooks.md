# Apply Onfido verification outcomes from webhooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Apply Onfido verification outcomes from webhooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Onfido server-to-server webhook) |
| **Business Outcome** | When identity checks complete in Onfido, the platform keeps KYC records, extracted identity fields, and company auto-verification aligned with those results without manual polling. |
| **Entry Point / Surface** | Sleek API (server-to-server): `POST` `/v2/identity-verification/webhook` — body `{ payload: { action, object } }`; `validateWebhookSignature` requires HMAC `x-sha2-signature` over the raw body (`req.bodyPlainText`) using `config.onfido.webhookToken` / `ONFIDO_WEBHOOK_TOKEN`. Swagger documents `webhookAuth` security. Returns `200` `{ message: "OK" }` or `422` on handler error; signature failure returns `401`. |
| **Short Description** | Validates the Onfido callback signature, then dispatches `check.completed` and `report.completed` to `intercept`. For completed checks, loads the check from Onfido, updates change-of-particulars (`user-request`) state when applicable, syncs `kyc_onfido.checks` and webhook flags on the user, and for HK HKID / work-pass paths may chain a follow-up check from uploaded documents. For completed reports, routes proof-of-address vs other reports, merges document extraction into `kyc_onfido`, updates status and optional auto-filled profile fields, uploads reports via Sleek KYC, and when all required document and POA reports are clear runs ComplyAdvantage name checks and `kycAutoVerified` for linked companies. |
| **Variants / Markets** | SG, HK (HKID / work-pass follow-up logic; residential status rules in `verifyUserDocuments`) |
| **Dependencies / Related Flows** | Onfido API (`retrieveCheck`, `retrieveReport` via kyc-onfido handlers); `user-request-service` (`updateUserRequestOnfidoChecks`, `updateUserRequestOnfidoReport`) for change of particulars; `proof-of-address-service.handleProofOfAddressReport`; `sleek-kyc-service.uploadCheckReport`; `kyc-auto-verified-service.kycAutoVerified`; `comply-advantage` name checks; app features `auto_update_user_from_onfido_data`, `sleek_my_info`; `createUserCheck` for chained HK follow-up checks. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (`kyc_onfido`, `kyc_onfido_status`, `kyc_onfido_webhook_status`, `last_updated_onfido_fields`, profile fields updated from extraction); `companyusers` (auto-verify flags and ComplyAdvantage / KYC auto-verified flow); `userrequests` (change-of-particulars branches via `user-request-service`; not every webhook hits persisted user-request updates) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Confirm whether all tenants use the same `/v2/identity-verification/webhook` URL in Onfido dashboard; whether `bodyPlainText` middleware ordering is guaranteed for every deployment path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`kyc-onfido/controllers/webhook-controller.js`): `POST` `/` with `validateWebhookSignature` then async handler — reads `req.body.payload`, calls `intercept(payload.action, payload.object)`, responds `200` `{ message: "OK" }` or `422` `{ message: "Error" }`.
- **Signature middleware** (`kyc-onfido/middleware/validate-webhook-signature.js`): Requires `x-sha2-signature` (hex); HMAC-SHA256 of `req.bodyPlainText` with webhook token; `crypto.timingSafeEqual`; on failure `401` `{ message: ... }`.
- **Dispatch** (`kyc-onfido/handlers/webhook.js`): `intercept` maps `check.completed` → `checkCompleted`, `report.completed` → `reportCompleted`.
- **`checkCompleted`**: If resource `status === "complete"`, `retrieveCheck(resource.id)`; early exit if no `applicantId`; `updateUserRequestOnfidoChecks(check)` — if user request found, returns (compliance review path). Else finds `User` by `kyc_onfido.applicant.id`; `User.updateOne` sets matching `kyc_onfido.checks.$` status/result/resultsUri and `kyc_onfido_webhook_status`. For HK HKID or `WORK_PASS_HOLDERS`, may `createUserCheck` for follow-up documents via `hkidFollowUpDocumentType` and latest documents.
- **`reportCompleted`**: `retrieveReport(resource.id)`; `updateUserRequestOnfidoReport(report)` short-circuits for change-of-particulars; else `handleKYCOnfidoReport` — POA vs `handleOnfidoReport`; reloads user by check id; `verifyUserDocuments` for pending passport/ID/FIN; if all KYC reports complete and latest POA report `result === "clear"`, `autoVerifyCompanyUsers` (ComplyAdvantage + `kycAutoVerified`, clears `is_onfido_delay_kyc_auto_verify`).
- **`handleOnfidoReport`** (document report): Finds user by documents tied to check; writes extracted properties to `user.kyc_onfido[extractedDataKey]`; validates uploaded vs reported document type for failure path; sets `kyc_onfido_status` to success or failed verification; `updateUserDataBasedOnExtractedOnfidoData` when feature flag enabled; `uploadCheckReport`.
- **`verifyUserDocuments` / `findNotLatestDocuments`**: Residential-status–based rules for SG/HK document requirements and pending extraction state.
- **Mount** (`app-router.js`): `router.use("/v2/identity-verification/webhook", require("./kyc-onfido/controllers/webhook-controller"))`.

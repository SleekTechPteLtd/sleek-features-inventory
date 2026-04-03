# Process Sleek KYC verification webhooks

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Process Sleek KYC verification webhooks |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Jumio/Sleek KYC callback to the platform) |
| **Business Outcome** | Identity and address verification results from the Sleek KYC/Jumio flow are persisted with document images in the customer file store so onboarding and compliance can rely on a complete, auditable KYC record. |
| **Entry Point / Surface** | Sleek API (server-to-server): `PUT` `/v2/sleek-kyc/user/webhook/:userId/:companyId` — protected by shared-secret `Authorization` header (matches `config/sleek-kyc` credentials), not end-user session auth; invoked when Jumio/Sleek KYC posts verification results. Verification sessions register this URL via `generateUrlFromSleekKyc` (`webhookUrl` = `${sleekApiBaseUrl}/v2/sleek-kyc/user/webhook/...`). |
| **Short Description** | Validates webhook body (`refId`, `uploadType`, `jumioData`), matches the user’s `kyc_jumio` entry by `reference_id`, records per-step success/failure, downloads files from the Sleek KYC service (`/api/file-request`), uploads binaries into the user’s file root via `file-service`, and updates `kyc_jumio` payloads and aggregate `kyc_jumio_status`. On full success across all Jumio steps, calls `user-service.moveUserFilesToKYC` to file documents under the company Secretary KYC folder structure. |
| **Variants / Markets** | SG (default config `sleekKYC.country` is `SGP`; other deployments may override) |
| **Dependencies / Related Flows** | Sleek KYC microservice (`config.sleekKYC.sleekKYCBaseUrl`, `/api/file-request`, `/api/generate-id-verification-link` / `generate-doc-verification-link`); `file-service` (stored `File` documents, user `root_folder`); `user-service.moveUserFilesToKYC` (post-success filing); customer onboarding / `sleek_kyc` app feature flows that call `generateUrlFromSleekKyc` (same module, `user-service`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (`kyc_jumio`, `kyc_jumio_status`, `passport_files`, `id_files`, `proof_of_residence_files`, `profile_photo_files`); `files` (created uploads); `companyusers` (read to resolve company context for filenames); `companies` (read inside `moveUserFilesToKYC` for Secretary/KYC folder paths) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether non-SG tenants use the same v1 Sleek KYC webhook path in production; confirm rotation and monitoring of the shared webhook `Authorization` secret. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers-v2/sleek-kyc.js`): `PUT` `/user/webhook/:id/:companyId` with `sleekKYCHandler.authMiddleware` then `webHook`.
- **Handler** (`controllers-v2/handlers/sleek-kyc/user-kyc.js`): `webHook` — `validationUtils.validateOrReject` requires `refId`, `uploadType`, `jumioData`; calls `sleekKYCService.updateUserData(req.params.id, req.params.companyId, body)`; responds `200` `"ok"` or `422` on error. `authMiddleware` — `Authorization` header must equal credential `Authorization` from `config/sleek-kyc/{credentialsFile}`.
- **Service** (`services/sleek-kyc-service.js`): `updateUserData` — loads `User` by id and `CompanyUser` for `company`+`user`; finds `kyc_jumio` object by `refId` → `reference_id`. **Document** upload type: sets status from Jumio document extraction (`EXTRACTED` vs failed), downloads `originalDocument` or `images[]` via `downloadFileFromSleekKyc`, pushes file ids to `proof_of_residence_files`. **ID** path: sets status from `verificationStatus` (`APPROVED_VERIFIED` vs failed); passport vs ID card branches download `idScanImage` / `idScanImageBackside` into `passport_files` or `id_files`; optional face image `idScanImageFace` → `profile_photo_files`. Stores `jumio_data`; recomputes aggregate `kyc_jumio_status` when all steps succeed or all resolved; on all successful, `userService.moveUserFilesToKYC(user, companyId)`. `generateUrlFromSleekKyc` registers `webhookUrl` and `webhookToken: Authorization` for the Sleek KYC API. `downloadFileFromSleekKyc` posts to `${sleekKYCBaseUrl}/api/file-request` with shared auth via `request-helper-sleek-kyc`.
- **Constants** (`constants/user-kyc.js`): `STATUS`, `TYPE` (Document vs ID), `PASSPORT`, verification enums used in branching.
- **Schema** (`schemas/user.js`): `kyc_jumio`, `kyc_jumio_status`, file array refs for PoR, ID, passport, profile photo.
- **App mount** (`app-router.js`): `router.use("/v2/sleek-kyc", require("./controllers-v2/sleek-kyc"))`.

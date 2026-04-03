# Manage Sleek Digest settings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage Sleek Digest settings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance user / operations user (authenticated via `AuthGuard`) |
| **Business Outcome** | Companies can align Sleek Digest email reminders with how ready they are to act—by pausing the whole digest for a period or excluding specific fiscal years—so task nudges match real operational and filing readiness. |
| **Entry Point / Surface** | Authenticated HTTP API under tag `sleek-digests`: `GET`/`PATCH /sleek-digests/:companyId/settings`, `PATCH /sleek-digests/:companyId/settings/:fy` (client app or internal UI consuming this API; exact in-app navigation not defined in code). |
| **Short Description** | Authenticated users read and update per-company Sleek Digest snooze settings (reasons, duration, end date, or until FY end), see last digest send time and per-FY snooze list, and add or remove a fiscal year from the FY-level snooze list so digest content and scheduling respect company context. Eligibility for read is enforced via CMS feature flags and Sleek Back company status. |
| **Variants / Markets** | SG, HK (explicit in digest/email logic); deployment may set `COUNTRY` for other regions—full market list not enumerated in these files. |
| **Dependencies / Related Flows** | **Sleek CMS** (`AppFeatureService`): supporting-documents and Sleek Digest feature flags. **Sleek Back**: company record, non-churned/archived status for eligibility, company admin and FY data via `CompanyService`. **Sleek Auditor**: audit logs on settings changes and FY snooze actions. **Downstream**: digest email batch (`sendDigestEmails`, `getCompanyData`) excludes FYs listed in `snooze_fys` and respects global snooze in `shouldSendEmailDigest`. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `companies` (embedded `sleek_digest_settings` including `snooze_fys`); `sleek_digests` (read for `last_sent_date` / latest digest in settings response) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`src/sleek-digest/sleek-digest.controller.ts`)

- **Auth**: All routes use `AuthGuard`; Swagger tag `sleek-digests`, `ApiSecurity('Authorization')`.
- **GET** `/:companyId/settings` → `getSleekDigestSettings` — 200 with data; 404 when company not eligible for Sleek Digest.
- **PATCH** `/:companyId/settings` → `updateSleekDigestSettings` — body `UpdateSleekDigestSettingsDto`; 200, 400 validation, 404 company not found.
- **PATCH** `/:companyId/settings/:fy` → `snoozeFy` — params `SnoozeFyParamsDto` (`companyId` MongoId, `fy` four-digit year), body `SnoozeFyBodyDto` (`snooze_status` enabled/disabled).

### Service (`src/sleek-digest/sleek-digest.service.ts`)

- **getSleekDigestSettings**: `findCompanyById`; `checkEligibilityForBatch` (CMS configs + Sleek Back status); loads `companyService.getSleekDigestSettings`; latest record from `digestModel` for `last_sent_date`; returns `snooze_*`, `snooze_fys`, etc.
- **updateSleekDigestSettings**: Validates enable/disable/partial updates; enable requires exactly one of `snooze_duration`, `snooze_end_date`, or `snooze_until_fy_end`, plus `snooze_reasons` when enabling; bounds snooze end to company FY end; persists via `companyService.updateSleekDigestSetting`; `auditSleekDigestSettingsChange` to Sleek Auditor.
- **snoozeFy**: Validates `fy` against `getCompanyFYsBasedOnSubscriptions` (`serviceFY` list); `addFyToSnoozeFys` / `removeFyFromSnoozeFys` on company; audit log. **Digest generation** uses `snooze_fys` in `getCompanyData` to filter out snoozed FYs from task computation.

### DTOs

- **update-sleek-digest-settings.dto.ts**: Optional `snooze_status`, `snooze_duration` (nested duration + unit), `snooze_end_date`, `snooze_until_fy_end`, `snooze_reasons`, `snooze_reason_other`.
- **snooze-fy.dto.ts** / **snooze-fy-params.dto.ts**: Body `snooze_status`; params `companyId`, `fy` (`YYYY`).

### Schema

- **digest.schema.ts**: Collection `sleek_digests` — used when exposing last sent timestamp and in digest send flow.

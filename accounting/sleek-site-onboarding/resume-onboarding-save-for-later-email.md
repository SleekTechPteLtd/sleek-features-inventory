# Resume onboarding with save-for-later email

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resume onboarding with save-for-later email |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (marketing-site onboarding); Operations / sales (optional lead notification when save-for-later is triggered from the payment step) |
| **Business Outcome** | Recover abandoned incorporation or accounting-transfer sessions by emailing a resume link, and surface high-intent leads to sales when the prospect saves from the payment step. |
| **Entry Point / Surface** | Sleek marketing website — self-serve onboarding (incorporation, accounting transfer, or Australian incorporation per tenant) — backend `POST /v2/sleek-site-onboarding/send-continue-email` (no auth middleware; invoked when the user chooses save-for-later and the front end supplies `token`, `userData`, and optional `saveForLaterBackRedirectTo`). |
| **Short Description** | Accepts an onboarding token and profile fields, builds a `resume_link` to the correct onboarding path on `sleekWebsite2BaseUrl`, normalises display company name with the configured name suffix from app feature `sleek_site_onboarding`, and sends the prospect the `ONBOARDING_FLOW_SAVE_FOR_LATER` template. If `saveForLaterBackRedirectTo` is `payment`, sends sales a separate `BETA_SAVE_FOR_LATER_NEW_INCOMING_LEAD` email with contact details to `config.sales.email`. |
| **Variants / Markets** | SG, HK, AU (resume path switches on `tenant.name === 'au'` for Australian incorporation vs regional incorporation or accounting transfer); other tenants follow non-AU routing. |
| **Dependencies / Related Flows** | **Config**: `mailer.templates.ONBOARDING_FLOW_SAVE_FOR_LATER`, `mailer.templates.BETA_SAVE_FOR_LATER_NEW_INCOMING_LEAD`, `sleekWebsite2BaseUrl`, `sales.email`. **App features**: `sleek_site_onboarding` (`company_name_prefix` for company name in email). **Shared data**: `tenant.name` for AU vs other routing. **Delivery**: `mailerService.sendEmail` → `mailerVendor.sendEmail` (transactional mailer). Token creation and front-end onboarding state are upstream of this handler. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | None for `send-continue-email` (no persistence in this handler). Related route `GET /v2/sleek-site-onboarding/check-existing-email` uses `User`. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Where the onboarding token is minted and validated on resume is not in these files; confirm product copy for each mail template and full list of tenants using each resume path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sleek-site-onboarding.js`

- **`POST /send-continue-email`** — No `authMiddleware`. Reads `req.body.token`, `req.body.userData`. Loads `emailTemplate` from `config.mailer.templates.ONBOARDING_FLOW_SAVE_FOR_LATER`. Reads `sleek_site_onboarding` app feature for `company_name_prefix` (default `LIMITED`). Sets `resumeOnboardingPath`: for `tenant.name === 'au'`, `accounting-transfer` vs `australian-incorporation`; otherwise `accounting-transfer` vs `incorporation` depending on `userData.isAccountingTransfer`. Builds `resume_link` as `` `${config.sleekWebsite2BaseUrl}/onboarding/${resumeOnboardingPath}/?onboarding-token=${token}` ``. Adjusts `company_name` in email variables when it does not already end with the configured suffix and is not the placeholder `"your company"`. **SA-20646**: when `userData.saveForLaterBackRedirectTo === "payment"`, sends sales email via `mailerService.sendEmail` with `config.mailer.templates.BETA_SAVE_FOR_LATER_NEW_INCOMING_LEAD` and variables `first_name`, `last_name`, `email`, `phone` (from `countryCode` + `phone` or `N/A`) to `[config.sales.email]` (default `sales@sleek.sg`). Then sends the prospect email with `mailerService.sendEmail(emailTemplate, emailVariables, [userData.email])`. Returns `200` with `{}` or `422` with `SendingEmailError`.

### `services/mailer-service.js`

- **`sendEmail(templateId, variables, recipients, options)`** — Adds `resource_link` from `tenant.resource_link` when set; delegates to `mailerVendor.sendEmail` with from address from `config.support.emails.from` (unless overridden by `variables` / `options`). Used for both prospect and sales messages from the controller above.

### Unknown columns (reason)

- None — **Disposition** remains Unknown per pipeline default.

# Open and use Sleek business accounts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Open and use Sleek business accounts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User (authenticated Sleek client acting on a company) |
| **Business Outcome** | Clients discover whether their company qualifies for the Sleek partner business banking programme, whether a specific user may proceed to open an account, and receive customer and operations communications when the business account is activated and the tab becomes available. |
| **Entry Point / Surface** | Sleek customer dashboard — business account setup widget and related flows (links use `sleekWebsite2BaseUrl`, e.g. `/business-account` and dashboard consent URLs in related mail flows). **API (sleek-back v1):** `POST /companies/:companyId/validate-sba-eligibility` — `userService.authMiddleware`; `GET /companies/:companyId/user/:userId/check-sba-opening-ability` — `authMiddleware`; `POST /companies/:companyId/send-business-account-activated-email` — `authMiddleware`, body `receiver` email. |
| **Short Description** | **Eligibility:** After the company admin has completed invitation (`CompanyUser` owner with `invitation_status` accepted), `validate-sba-eligibility` runs `setBusinessAccountEligibility` with entrypoint `SBA_SET_ELIGIBILITY_ENDPOINT_NEED_BUSINESS_ACCOUNT_WIDGET`, evaluating CMS-gated business-account setup, prohibited SSIC lists (with accounting-service exceptions), operating countries and owner residence vs red-flag lists, and excluding sole proprietorships; persists `sba_is_eligible` / reasons and onboarding tile state, and writes an auditor log. **Opening ability:** `check-sba-opening-ability` ensures company is live (or live post-incorporation), not already `has_SBA`, SBA onboarding CMS enabled, then reuses director/owner eligibility filtering (KYC, nominee/resigned director rules via company history) with PII and financial-partner TNC checks skipped for this probe, and returns whether the requested `userId` is among eligible users. **Comms:** When the account is active, `send-business-account-activated-email` sends the customer `BUSINESS_ACCOUNT_VIRTUAL_ACCOUNT_ACTIVE` email and notifies operations via `BUSINESS_ACCOUNT_TAB_ACCESS` when admin `companies.business_account` is enabled. |
| **Variants / Markets** | `SG` (SSIC-based rules, Singapore-focused profile exceptions in prohibited SSIC handling; partner banking context aligns with SBA/DBS flows elsewhere). Other markets not evidenced in these paths. |
| **Dependencies / Related Flows** | **CMS:** `customer_onboarding` (`business_account_setup`, `business_account_setup_constants`), `business_account` / `sba_onboarding`, admin `companies.business_account`. **Internal:** `company-business-account-onboarding-service` (`setBusinessAccountEligibility`), `company-profile-service` (SSIC-related profile fields), `business-account-service` (`checkBusinessAccountOpeningAbility`, `getEligibleUsersForBusinessAccountCreation` → `company-history-service`), `company-user-service` (`sendBusinessAccountActivatedEmail`), `company-service` (`sendBusinessAccountAccessTabEmail`), `mailer-service`, `sleek-auditor-node` (`company.business_account.set_eligibility`). **Related:** automated or manual SBA account creation (`requestCreateAccounts`, `SBA_BANK_API_URL` — not invoked by these three routes but same product area). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` — `findById` / `findOneAndUpdate` for `sba_is_eligible`, `sba_is_not_eligible_reasons`, `appOnboardingData.tile_business_account_setup`; reads `status`, `has_SBA`, `name_of_countries`, SSIC fields, `company_type`. `companyusers` — `find` / `findOne` for owners, directors/owners for eligibility and opening-ability checks. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `validate-sba-eligibility` and `send-business-account-activated-email` use `authMiddleware` only (no `canManageCompanyMiddleware` in controller); confirm gateway or client constraints enforce company membership. Whether `check-sba-opening-ability` should align with the same company-access pattern as other `/companies/:companyId/*` routes. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/company-controller.js`

- **`POST /companies/:companyId/validate-sba-eligibility`** — Requires authenticated user; verifies company has an accepted owner `CompanyUser`; otherwise **422** with profile-completion message. Calls **`setBusinessAccountEligibility(companyId, req.user, SBA_ELIGIBILITY_ENTRYPOINTS.NEED_BUSINESS_ACCOUNT_WIDGET)`**; **200** returns updated company JSON; company missing maps to `ERROR_CODES.COMPANY.DOES_NOT_EXISTS`.
- **`GET /companies/:companyId/user/:userId/check-sba-opening-ability`** — **`businessAccountService.checkBusinessAccountOpeningAbility(companyId, userId)`**; **200** JSON `{ isValid, message }`.
- **`POST /companies/:companyId/send-business-account-activated-email`** — Loads `Company`; **`companyUserService.sendBusinessAccountActivatedEmail(company, receiver)`** and **`companyService.sendBusinessAccountAccessTabEmail(company, receiver)`**; **200** success message.

### `services/company-business-account-onboarding-service.js`

- **`setBusinessAccountEligibility(companyId, reqUser, entrypoint)`** — Gates on **`customer_onboarding`** CMS and **`business_account_setup.enabled`** via **`_isBusinessAccountSetupFeatureAvailable`**. Runs **`_checkSSICPassed`** (prohibited SSIC list from `sba_prohibited_ssic` CMS, accounting subscription and profile-based exceptions), **`_checkOperatingCountriesPassed`**, **`_checkCompanyAdminsResidenceCountryPassed`** (owner `CompanyUser` + `user.address.country` vs `REJECT_RED_FLAG_COUNTRIES`), **`_checkCompanyTypePassed`** (not `SOLE_PROPRIETORSHIP`). On full pass: sets **`sba_is_eligible: true`**, **`_auditLog`**. Else: **`sba_is_eligible: false`**, **`sba_is_not_eligible_reasons`** (`PROHIBITED_SSIC` / `PROHIBITED_NATIONALITY_OR_OPERATING_COUNTRY`), **`appOnboardingData.tile_business_account_setup: "NOT_ELIGIBLE"`**, audit. **`_auditLog`** — `action: "company.business_account.set_eligibility"`, tags `business-account-onboarding`.

### `services/business-account-service.js`

- **`checkBusinessAccountOpeningAbility(companyId, userId)`** — Validates company and user ids; rejects if **`has_SBA`** or company status not **`live`** / **`live_post_incorporation`**; requires CMS **`business_account`** → **`sba_onboarding.enabled`**. Builds **`getEligibleUsersForBusinessAccountCreation`** with **`skipFilterSteps`** for PII and financial-partner TNC only; compares **`userId`** to eligible users’ **`user._id`**.
- **`getEligibleUsersForBusinessAccountCreation`** — `CompanyUser` query (director or owner, optional query), KYC/consent/TNC/nominee/resigned-director checks using **`companyHistoryService.getCompanyHistory`**; dedupes by user; returns **`companyUsers`** and **`errorUsers`**.

### `services/company-user-service.js`

- **`sendBusinessAccountActivatedEmail(company, receiver)`** — If admin **`companies.business_account`** enabled, sends **`BUSINESS_ACCOUNT_VIRTUAL_ACCOUNT_ACTIVE`** with company name, **`customer_app_link`** `${sleekWebsite2BaseUrl}/business-account`, help link from accounting onboarding workflow email config, CC from **`config.notification.email_cc_list`**.

### `services/company-service.js` (caller only; not in expand list)

- **`sendBusinessAccountAccessTabEmail`** — Used by the same controller route; **`BUSINESS_ACCOUNT_TAB_ACCESS`** to **`config.notification.emails`** with admin redirect URL when **`companies.business_account`** enabled.

### Constants

- **`constants/sba-eligibility.js`** — `SBA_ELIGIBILITY_ENTRYPOINTS.NEED_BUSINESS_ACCOUNT_WIDGET` string used when validating from the widget endpoint.

### Tests

- `tests/controllers/company-controller/validate-sba-eligibility.js`, `check-sba-opening-ability.js` — route behaviour and CMS stubs.

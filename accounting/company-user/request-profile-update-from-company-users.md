# Request profile updates from company users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Request profile updates from company users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance / Operations (Sleek Admin); intended use is staff requesting follow-up on incomplete or stale company-user profile data |
| **Business Outcome** | Corporate secretarial and compliance teams receive a structured email they can action so a linked company user completes or refreshes their profile, with replies routed to that user. |
| **Entry Point / Surface** | Sleek Admin (or authenticated client) → API `POST /v2/company-users/:companyUserId/send-update-request` — no separate product navigation path encoded in handler |
| **Short Description** | Loads the `CompanyUser` with `user` and `company`, then sends the `USER_PROFILE_UPDATE_REQUEST` template via the mailer: one message per regional corporate secretarial inbox (AU, HK, SG), with sender metadata from the company user and `replyTo` set to their email. Template variables include company name, user display name, and admin base URL. |
| **Variants / Markets** | AU, HK, SG |
| **Dependencies / Related Flows** | Sleek Mailer (`sendEmailNewEngine`) or messaging service when feature flags enable it; Mailgun/CMS template path when mock/debug; company-user KYC and onboarding flows upstream |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `CompanyUser` (read; populate `User`, `Company`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Route uses only `userService.authMiddleware` (not admin-only): confirm whether any authenticated user may call this for arbitrary `companyUserId`, or if callers are constrained elsewhere. `RECIPIENT` has no `gb` (UK) entry — behaviour for UK tenant is undefined at send time. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route:** `POST /v2/company-users/:companyUserId/send-update-request` — mounted in `app-router.js` under `/v2/company-users`; wired with `buildPostRoute` (auth middleware only) in `controllers-v2/company-user.js`.
- **Handler:** `sendUpdateRequestEmail` in `controllers-v2/handlers/company-user/send-request-update-email.js` — `CompanyUser.findOne({ _id: companyUserId }).populate(["user", "company"])`, 422 if missing.
- **Regional routing:** `RECIPIENT` keyed by `tenant.name`: `au` → `corpsec.au@sleek.com`, `hk` → `hkcomsec@sleek.com`, `sg` → `compliance@sleek.com`.
- **Mail:** `mailerVendor.sendEmail(config.mailer.templates.USER_PROFILE_UPDATE_REQUEST, userEmail, userName, variables, recipients, { replyTo: userEmail })` — template id `user_profile_update_request` in multi-platform config (AU/HK/SG defaults).
- **Mailer implementation:** `vendors/mailer-vendor.js` — `sendEmail` branches to Sleek Mailer HTTP API, messaging service, or local template/Mailgun depending on `sleekMailer` and app features; adds tenant branding variables.
- **Schema:** `schemas/company-user.js` — Mongoose model `CompanyUser`; this flow reads only (no writes in handler).

# Resend UK onboarding KYC invitation

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Resend UK onboarding KYC invitation |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Sleek Admin |
| **Business Outcome** | Operations can re-issue a UK onboarding Sumsub verification invite to a company user so identity checks can proceed, with the verification email showing the parent company name when the user is a corporate shareholder of a subsidiary. |
| **Entry Point / Surface** | Sleek API: `POST /onboarding/:companyUserId/resend-invite` — `userService.authMiddleware` plus `accessControlService.isIn("Sleek Admin")`; admin UI path to trigger the call not defined in this module |
| **Short Description** | Loads the target `CompanyUser` with `user` and `company`, optionally overrides the in-memory company display name with the parent company when this user is linked as a corporate shareholder of another company, then calls UK onboarding to send the Sumsub invite and set invitation status to pending. Returns JSON `true` on success and `false` on any error (errors are swallowed in the controller). |
| **Variants / Markets** | UK |
| **Dependencies / Related Flows** | UK onboarding `sendInvite` (post-payment and other flows), Sumsub invite API via `sleekSumsub` (`/api/invite-user`), `userService.getUserAuthToken`, `invitationService.setInvitationStatus`; related corporate-shareholder modelling (`shareholder.corporate` on `CompanyUser`) |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers` (read/update `CompanyUser`, parent lookup by `shareholder.corporate`, `invitation_status` via `setInvitationStatus`); `users` (read/populate; may update `auth_token` via `getUserAuthToken` when missing) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `resendInvitation` returns `false` for all failures without status codes or logging; confirm intended behaviour for users whose `kyc_status` is `RESUBMISSION_REQUIRED` or `REJECTED`, since `uk-onboarding.sendInvite` skips sending when status is in `APPROVED`, `RESUBMISSION_REQUIRED`, or `REJECTED`. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`app-router.js`): `router.use("/onboarding", require("./modules/sleek-onboarding/controller/onboarding-controller"))`.
- **Controller** (`modules/sleek-onboarding/controller/onboarding-controller.js`): `POST /:companyUserId/resend-invite` — `userService.authMiddleware`, `accessControlService.isIn("Sleek Admin")`, handler `resendInvitation`. Loads `CompanyUser` by `_id`, populates `user` and `company`. Finds another `CompanyUser` where `shareholder.corporate` equals the target’s `company` and populates `company`; if found, sets `companyUser.company.name` to the parent’s `name` (comment: send parent company name in Sumsub verification email instead of corporate shareholder name). Calls `ukOnboarding.sendInvite(companyUser)`; responds `res.json(true)` or `res.json(false)` on catch.
- **UK onboarding** (`modules/sleek-onboarding/services/uk-onboarding.js`): `sendInvite(companyUser)` builds `kycData` (`to.email`, `first_name`, `user_id`, `company_id`, `company_name` from `companyUser.company.name`) and, subject to `kyc_status` guards, runs `Promise.all`: `userService.getUserAuthToken`, `sumsubService.sendUserSumsubInvite(kycData)`, `invitationService.setInvitationStatus(..., INVITATION_STATUSES.PENDING)`.
- **Sumsub client** (`modules/sleek-onboarding/services/send-invite.js`): `sendUserSumsubInvite` — `POST ${config.sleekSumsub.baseUrl}/api/invite-user` with payload.
- **Invitations** (`services/invitations/invitation-service.js`): `setInvitationStatus(userId, companyId, status)` — `CompanyUser.updateMany({ user, company }, { invitation_status })`.

# Invite another user to pay

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Invite another user to pay |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (member who can manage the company) |
| **Business Outcome** | Someone else can complete incorporation or transfer checkout and payment when the inviter cannot or should not pay, without sharing the inviter’s credentials. |
| **Entry Point / Surface** | Sleek customer app — flows that call `POST /companies/:companyId/invite-to-pay` with `email` in the body (after authentication). |
| **Short Description** | An authenticated company user sends a transactional email to an address. The backend ensures a `User` exists (creating or updating a pre-registration record with token for new emails), links them to the company via `CompanyUser`, resolves the recipient address (including alternate contact preferences), and emails a deep link to the Sleek site with query params for register vs login and incorporation vs transfer, so the invitee can land on checkout and pay. |
| **Variants / Markets** | SG, HK, UK, AU (mailer template id `charge_invite_to_pay` is configured per tenant in multi-platform config) |
| **Dependencies / Related Flows** | Sleek website checkout (`config.sleekWebsite2BaseUrl`); user registration/login with `ft`, `token`, `cid`; incorporation vs transfer determined by `company.is_transfer`; transactional email vendor via `mailer-service` / `mailer-vendor`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (find/upsert by email or `temporary_email`; `registration_token` for new invites), `companyusers` (upsert link), `companyuserpreferences` (read in aggregate when resolving recipient email) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/payment-controller.js`

- **`POST /companies/:companyId/invite-to-pay`** — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("companyUser")`. Validates `req.body.email` with `isemail` (422 on failure).
- **User resolution** — `User.findOne({ email })`; if missing, `userService.generateToken()`, `User.findOneAndUpdate` on `{ temporary_email: email }` with `temporary_email` + `registration_token` (upsert). If existing user, URL uses `ft=login` and `email`; if new, `ft=register` and `token`.
- **Checkout URL** — `make_payment_url` = `${config.sleekWebsite2BaseUrl}?${querystring.stringify(makePaymentUrlParams)}` with `redirect` = `/{transfer|incorporate}/?cid=` + `companyId` depending on `req.company.is_transfer`.
- **Company link** — `CompanyUser.findOneAndUpdate({ company, user }, { company, user }, { upsert: true })`.
- **Recipient email** — `companyUserService.findCompanyUserWithPreference({ company, user }, true)`; fallback object with `user.email`; maps `temporary_email` to `email` when no primary email.
- **Email** — `mailerService.sendEmail(config.mailer.templates.CHARGE_INVITE_TO_PAY, { user_name, company_name, make_payment_url }, [recipientEmail], { partner })` with `partner` from `partnerService.getPartnerByCompanyId`.

### `services/user-service.js`

- **`authMiddleware`** — Required for the route; attaches authenticated inviter to `req.user`.
- **`generateToken`** — Used to issue `registration_token` for not-yet-registered invitees.

### `services/company-user-service.js`

- **`findCompanyUserWithPreference`** — Aggregation on `companyusers` with `$lookup` to `companyuserpreferences` and `users` so the invite email can follow contact preferences.

### `services/mailer-service.js`

- **`sendEmail`** — Injects `tenant.resource_link` when configured; sets `from` to accounting address when `variables.isFromAccounting` (not set in this call); delegates to `mailer-vendor.sendEmail` for template `CHARGE_INVITE_TO_PAY`.

### Tests

- `tests/controllers/payment-controller/invite-to-pay.js` — Covers successful send, `CompanyUser` creation when user exists but is not yet linked, and template/URL assertions.

### Columns marked Unknown

- **Disposition** — Per skill, left `Unknown` (not determined from code).

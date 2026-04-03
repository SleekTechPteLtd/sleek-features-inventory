# Submit general customer enquiry

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Submit general customer enquiry |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer (authenticated Sleek user submitting contact details) |
| **Business Outcome** | Customers can reach Sleek support with subject, message, and optional attachments; the team receives a templated email and can reply to the customer’s address, with partner-originated submissions directed to the partner inbox instead of the default support queue. |
| **Entry Point / Surface** | Sleek API: HTTP `POST /v2/enquiry/` under Swagger tags `enquiry` and `v2` (`public/api-docs/enquiry.yml`); requires `sleek_auth`. App/CMS references include `/enquiry` and feature flag `new_enquiry_page` (see app features). |
| **Short Description** | After `userService.authMiddleware`, the route accepts multipart form fields (`email`, `subject`, `message`, `name`, optional `company`, optional `id` as company id, optional `fromPartner`) and optional `file` uploads. Files are validated (extension, MIME, buffer check). The handler validates required fields, base64-encodes attachments, and the store command sends mail via `config.mailer.templates.ENQUIRY_EMAIL` to `config.support.emails.enquiryTo`, or to `config.support.partner.to` when `fromPartner` is true. `Company.findById` runs when `companyId` is present to resolve company context for `partnerService.getPartnerByCompany`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Transactional email (`mailerVendor.sendEmail`); partner resolution (`services/partners/partner-service`); support/partner recipient addresses from config. No persistent enquiry record beyond email send. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (read by id when `companyId` supplied) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | OpenAPI `EnquiryRequestSchema` omits `message` and multipart/file semantics while the implementation requires `message` and uses `multer` for `file` — confirm contract vs clients. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/enquiry.js`

- `router.route("/").post(userService.authMiddleware, enquiryRateLimiter, …)` — `enquiryRateLimiter`: 5 requests per 60s, 429 on exceed.
- Multipart `upload` via `multer().array("file")`; `ACCEPTED_FILE_EXTENSIONS` / `ACCEPTED_FILE_MIME_TYPES` filter; `fileUtils.checkFileType` on buffers when files present.
- Body: `email`, `subject`, `message`, `name`, `company`, `fromPartner` (default false), `id` → `companyId`.
- Delegates to `sendEnquiryEmailHandler` → 200 JSON or 422 validation issues.

### `controllers-v2/handlers/enquiry/send-email.js`

- `sendEnquiryEmailHandler`: `parseRequest`, `validateRequest` (requires `email`, `name`, `subject`, `message`).
- Builds `attachments` from uploaded files (base64, filename, contentType, size).
- On success calls `store-commands/enquiry/send-email` `execute`.

### `store-commands/enquiry/send-email.js`

- `config.mailer.templates.ENQUIRY_EMAIL`; variables include subject line, title, name, date, message, email, company, `isPartner` from `fromPartner`.
- Default recipients `[config.support.emails.enquiryTo]`; if `input.fromPartner`, recipients `[config.support.partner.to]`.
- `Company.findById(input.companyId)` when provided; `partnerService.getPartnerByCompany(company)` passed into mailer `options.partner`.
- `replyTo: input.email`; forwards `attachments` to `mailerVendor.sendEmail`.

### `public/api-docs/enquiry.yml`

- `POST /v2/enquiry/`: summary describes email to support; tags `enquiry`, `v2`; `security: sleek_auth`; responses 200 / 422.

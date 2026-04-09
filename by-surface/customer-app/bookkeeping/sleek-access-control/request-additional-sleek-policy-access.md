# Request additional Sleek policy access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Request additional Sleek policy access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company user (requester); company admins with `permissionSettings` (notified); optional flows involve company owner or requester for status emails |
| **Business Outcome** | Users can justify and request extra PBAC policies; the external Sleek Access Control service stores each request, and company admins are notified by email so they can review or act in the customer app. |
| **Entry Point / Surface** | Authenticated API under `POST .../sleek-access-control/...` — client surfaces implied by `edit_url` / `view_settings` pointing at Sleek Customer profile (`/profile`, `/profile/general`); exact in-app navigation not encoded in handlers |
| **Short Description** | Validates user and company, resolves permission/policy context from Sleek Access Control, posts one `admin/request-access` record per selected policy with business justification, then sends `PBAC_REQUEST_ACCESS` to each relevant company admin. Separate routes send status-change emails (`PBAC_REQUEST_ACCESS_STATUS_CHANGE`) to the requester or alternate paths that email the company owner. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Access Control HTTP API (`customer/permission`, `customer/policy`, `customer/company-user`, `admin/request-access`, `admin/permission-section`); Sleek Mailer templates `PBAC_REQUEST_ACCESS`, `PBAC_REQUEST_ACCESS_STATUS_CHANGE`; Sleek Customer base URL for profile links |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `User`, `Company`, `CompanyUser` (read / populate only in these flows; policy state is external) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST /sleek-access-control/web-hook/update-role-templates` calls `sleekAccessControl.setRoleTemplatesCache()`, but `sleek-access-control-service.js` does not define or export that function — confirm dead code vs missing export. Market/tenant behaviour for templates and routing not visible in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Primary route:** `POST /sleek-access-control/request-access/user/:userId/company/:companyId` — `userService.authMiddleware`; body `policies`, `businessJustification` — `controllers/sleek-access-control.js`.
- **Service:** `sendRequestAccess` — `validatePayload` (ObjectIds, non-empty `requestedPolicies`, `businessJustification`); `User.findOne`, `Company.findOne`; `getResource` to Sleek Access Control for permission `permissionSettings` / Full, policy by section, company users with `expandUserInfo`; per policy `postResource` to `{sleekAccessControl.baseUrl}/admin/request-access` with `requested_policy` (policy, section, access), `company`, `user`, `business_justification`; `mailerService.sendEmail(config.mailer.templates.PBAC_REQUEST_ACCESS, ...)` to each `companyUser.user.email` — `services/sleek-access-control-service.js`.
- **Status to requester:** `POST /sleek-access-control/request-access/send-request-change-email/company/:companyId` → `sendRequestStatusChangeEmail` — loads users/company, fetches policy and section from SAC, emails requester with `PBAC_REQUEST_ACCESS_STATUS_CHANGE` for Approved / Rejected / Cancelled.
- **Alternate notify:** `POST /sleek-access-control/send-request-email/user/:userId/company/:companyId` → `sendRequestAccessEmail` — `CompanyUser` for user+company and owner (`is_owner: true`), enriches policy display fields, emails owner with `PBAC_REQUEST_ACCESS`.
- **Updates:** `POST /sleek-access-control/update-request-email` → `sendUpdateRequestAccessEmail` — `CompanyUser` lookups, `PBAC_REQUEST_ACCESS_STATUS_CHANGE` to company user email with `request` payload fields (`request.status`, `requested_policy`, etc.).
- **Schemas:** `schemas/user.js`, `schemas/company.js`, `schemas/company-user.js` — referenced by Mongoose queries above.

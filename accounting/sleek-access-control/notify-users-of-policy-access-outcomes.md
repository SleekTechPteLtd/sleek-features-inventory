# Notify users of policy access outcomes

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Notify users of policy access outcomes |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company User (requester) — receives email; Operations / Admin or integrated services trigger the send via authenticated API |
| **Business Outcome** | Requesters learn whether their policy-based access request was granted, rejected, cancelled, or otherwise updated (including denied) so they know if they gained or lost access without checking the product manually. |
| **Entry Point / Surface** | Backend APIs (authenticated): `POST /sleek-access-control/request-access/send-request-change-email/company/:companyId` and `POST /sleek-access-control/update-request-email` — callers are typically Sleek Customer or internal flows when PBAC request status changes; no standalone app navigation string in controller |
| **Short Description** | Loads requester and company context from MongoDB, optionally enriches policy/section names from the Sleek Access Control service, then sends the `PBAC_REQUEST_ACCESS_STATUS_CHANGE` mailer template to the requester’s email. One path validates Approved / Rejected / Cancelled and maps Approved to a “granted” display status; the other sends updates from a structured body including `request.status` and denial flags for the same template. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Mailer service (`mailerService.sendEmail`); Sleek Access Control HTTP API (`config.sleekAccessControl.baseUrl`) for policy and section metadata; `sleekCustomer.baseUrl` for profile links in payloads; upstream PBAC request approval/rejection flows |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `User`, `Company`, `CompanyUser` (read; populate where used) — no writes in these notification paths |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High (implementation); Medium (which product surfaces call each route in production) |
| **Disposition** | Unknown |
| **Open Questions** | `sendUpdateRequestAccessEmail` uses lowercase `request.status` values such as `denied` and `isDeniedStatus`, while `sendRequestStatusChangeEmail` only accepts `Approved`, `Rejected`, `Cancelled` — confirm all production callers and templates align. Whether markets/tenants vary template or routing is not visible in these handlers. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes:** `controllers/sleek-access-control.js` — `POST .../request-access/send-request-change-email/company/:companyId` → `sendRequestStatusChangeEmail`; `POST .../update-request-email` → `sendUpdateRequestAccessEmail` (both behind `userService.authMiddleware`).
- **Status change email:** `services/sleek-access-control-service.js` — `sendRequestStatusChangeEmail` validates `STATUS_ENUMS` `["Approved", "Rejected", "Cancelled"]`; maps `Approved` → `request_status` `"granted"`, others via `status.toLowerCase()`; fetches policy via `GET .../customer/policy/:policyId` and section via `GET .../admin/permission-section/:sectionId`; builds payload with `user_name`, `company_admin_name`, `company_name`, policy `sectionName`, `name`, `isEditor`, `view_settings` to customer profile; `mailerService.sendEmail(config.mailer.templates.PBAC_REQUEST_ACCESS_STATUS_CHANGE, payload, [requester email])`.
- **Update email:** same service — `sendUpdateRequestAccessEmail(requestedPolicy)` resolves `CompanyUser` by `company` + `user`, loads owner for admin name; reads `request.status`, `request.section_name`, `request.requested_policy.access` (Editor / NoAccess → `isRemove`); sets `isDeniedStatus` when `request_status === "denied"`; same template `PBAC_REQUEST_ACCESS_STATUS_CHANGE` to requester email.
- **Related (not requester outcome):** `sendRequestAccess` and `sendRequestAccessEmail` use `PBAC_REQUEST_ACCESS` to notify **company admins** about new or forwarded requests — distinct from requester outcome notifications documented here.

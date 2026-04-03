# Align KYC metadata timestamps on company users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Align KYC metadata timestamps on company users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Sleek Admin, Company User (the person whose `CompanyUser` record is updated) |
| **Business Outcome** | KYC-related dates stored on a company user stay accurate for audits and compliance when manual correction is required after data fixes or process exceptions. |
| **Entry Point / Surface** | Sleek API: `POST` `/v2/company-users/{companyUserId}/timestamps` (not listed in `public/api-docs/company-user.yml` at time of review); likely invoked from admin tooling or integrations rather than a named in-app screen in this repo |
| **Short Description** | Authenticated callers who are either members of the Sleek Admin group or the same user as the target company user can submit optional ISO-style date fields to overwrite nested KYC timestamps: risk-level details (`kyc_risk_level_details.createdAt`), the approved entry in `kyc_history`, `kyc_refresh.createdAt`, and top-level document `createdAt`. The `CompanyUser` document is saved; Mongoose `save` hooks refresh PBAC default policy when company and user are set. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | `user-service` (`authMiddleware`), `access-control-service` (Sleek Admin membership or self-match on `CompanyUser.user`), broader KYC flows that read `kyc_history`, `kyc_risk_level_details`, `kyc_refresh` (e.g. KYC refresh, risk assessment); `pbac-policy-service` runs on `CompanyUser` save |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No OpenAPI entry for this route; confirm which client surfaces call it. Payload keys use snake_case; `kyc_history` update only mutates the first array element with `kyc_status === "approved"`—confirm that matches all production data shapes. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers-v2/company-user.js`): `buildPostRouteAdminOnly("/:companyUserId/timestamps", updateKYCRiskLevelTimestamps)` — applies `userService.authMiddleware` then `adminOrLoggedCompanyUserAuthMiddleware` (Sleek Admin **or** logged-in user equals `CompanyUser.user` for `req.params.companyUserId`). Mounted at `/v2/company-users` (`app-router.js`).
- **Handler** `updateKYCRiskLevelTimestamps`: loads `CompanyUser` by id; 404-style error if missing (`ERROR_CODES.USERS.DOES_NOT_EXISTS`). For each optional body field, clones nested objects and sets `createdAt` (or root `createdAt`) from `new Date(payload.<field>)`: `kyc_risk_level_updated_at` → `kyc_risk_level_details.createdAt`, `kyc_history` → approved history entry’s `createdAt`, `kyc_refresh` → `kyc_refresh.createdAt`, `createdAt` → document `createdAt`. `companyUser.save()`; success JSON includes updated document. Generic error path uses tenant `INTERNAL_SERVER_ERROR`.
- **Schema** (`schemas/company-user.js`): `kyc_history` (array), `kyc_risk_level_details` (object), `kyc_refresh` (Mixed), global `timestamps: true` for `createdAt`/`updatedAt`; `pre('save')` / `post('save')` including `pbacService.setDefaultPolicy` when `company` and `user` exist.
- **Model**: `mongoose.model("CompanyUser", ...)` → default collection name `companyusers`.

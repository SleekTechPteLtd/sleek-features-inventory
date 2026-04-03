# Manage corporate directors

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage corporate directors |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (create/update/delete gated by admin app feature `corporate-director`); authenticated user for read via standard auth middleware |
| **Business Outcome** | Companies can record when a corporate body—not only an individual—acts as director, with officer-style and KYC-aligned details for compliance and filings. |
| **Entry Point / Surface** | Sleek API: `GET`/`POST` `/v2/company-user-roles/{companyId}/corporate-director`, `DELETE` `/v2/company-user-roles/{companyId}/corporate-director/{companyUserId}` (documented under OpenAPI tag `corporate-director`); exact in-app navigation not defined in handlers |
| **Short Description** | Lists company users with role `corporate-director`, creates or updates the linked user and embedded corporate-entity profile (name, registration identifiers, jurisdiction, incorporation, address), or removes the assignment. Mutations require the `corporate-director` admin feature flag; new users get root folder setup and audit events are sent to Sleek Auditor on insert/update/delete. |
| **Variants / Markets** | SG, HK, UK (schema supports SG-style UEN, HK ID/pass fields, UK-oriented corporate director pattern per code comments) |
| **Dependencies / Related Flows** | `user-service` (auth middleware, sanitize, find/create user), `file-service` (user root folder on new user), `app-features-util` (feature `corporate-director`), Sleek Auditor HTTP API for audit logs, `ltd-onboarding-service` calls this API for corporate director |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies`, `companyusers` (role `corporate-director`, embedded `corporate_director` subdocument), `users`, `groups` (Sleek User group on create) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `getUser` does not check the `corporate-director` admin feature flag while `updateUser` and `deleteUser` do; confirm whether listing should be similarly restricted. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers-v2/company-user-role.js`): `GET`/`POST` `/:companyId/corporate-director`, `DELETE` `/:companyId/corporate-director/:companyUserId`; all routes use `userService.authMiddleware`.
- **Handlers** (`controllers-v2/handlers/company-user-role/corporate-director.js`): Validates `user` (personal/KYC fields including HK/SG-style identity and address) and `corporate_director` (entity name, registration numbers, jurisdiction, legal form, registrar, incorporation date, address, foreign-entity flag); delegates to `CorporateDirectorService`.
- **Service** (`services/company-user-role/corporate-director-service.js`): `getUser` — `CompanyUser.find` with `role: "corporate-director"` and `company`, populate `user`, sanitize via `userService.sanitizeUserData`. `updateUser` — requires `appFeatureUtil.getAppFeaturesByName("corporate-director", "admin").enabled`; finds or creates `User`, updates `CompanyUser` with `corporate_director` embedded object; on new user: `Group` "Sleek User", `CLIENT_TYPE`, partner handling, `fileService.createUserRootFolder`, `auditorService.saveAuditLog`. `deleteUser` — same feature flag; requires `corporate_director` subdocument on the `CompanyUser`; `CompanyUser.deleteOne`, audit log.
- **Schema** (`schemas/corporate-director.js`, embedded in `schemas/company-user.js`): Corporate body fields and address; model export for subdocument reuse.
- **External**: Audit persistence via `controllers-v2/handlers/auditor/all` → Sleek Auditor `PUT /api/log` (not MongoDB).
- **API docs**: `public/api-docs/company-user-roles.yml` — paths and tag `corporate-director`.
- **Tests**: `tests/controllers-v2/company-user-roles/*-corporate-director.js` — base path `/v2/company-user-roles/...`.

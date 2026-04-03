# Manage company platform access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage company platform access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin operator editing a client company) |
| **Business Outcome** | Client company accounts expose the right platform roles: company admins and standard users are provisioned, updated, or removed so only intended people can access the customer-facing company experience. |
| **Entry Point / Surface** | **sleek-website** admin: **Company edit** at `/admin/companies/edit/?cid=<companyId>` — cards **Company's Admins** and **Company's Standard Users** (embedded from `AdminCompaniesEditView`). |
| **Short Description** | Operators manage **company admins** (add from scratch or from existing company users, edit profile, remove by clearing owner flag via `updateCompanyUser`, resend invitations, KYC-related actions via `AdminsSection`, **Transfer ownership** dialog → `transferCompanyOwnership`) and **standard users** (list with invitation status, add/edit/remove, resend invite, optional KYC v2 “REMIND” path). Both surfaces call shared company-user APIs (`createAdmin`/`editAdmin`/`deleteCompanyUser`/`sendInvitation`) backed by `/companies/:id/company-users` and `/company-users/:id`. |
| **Variants / Markets** | Unknown (tenant/CMS feature flags such as `kyc_status`, `invitation_flow_without_kyc` gate behaviour; typical Sleek markets SG, HK, UK, AU — confirm per env). |
| **Dependencies / Related Flows** | **Ownership transfer**: `api.transferCompanyOwnership` → `POST /admin/companies/:companyId/change-owner` (parent `index.js`, not in the two listed view files). **Company user CRUD**: `createAdmin` → `POST /companies/:companyId/company-users`; `editAdmin` / `updateCompanyUser` → `PUT /company-users/:id`; `deleteCompanyUser` → `DELETE /company-users/:id`; `sendInvitation` → `POST /company-users/:id/invite` (query `isResendEmailInvite` for resend). **`api.updateUser`** when the edited company user matches the logged-in admin session. **KYC**: resend path logs `kycRecordAuditLog` with `"kyc-invitation-resent"`; Camunda/KYC helpers passed into `Admins` from parent. **Role constants**: `COMPANY_USER_ROLES.ADMIN` vs standard-user flows. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/admins.js`, `src/views/admin/companies/edit/standard-users.js`, `src/views/admin/companies/edit/admins-section.js` (child of admins), `src/views/admin/companies/edit/index.js` (orchestration, ownership transfer), `src/utils/api.js`, `src/utils/company-user-roles-utils.js`, `src/utils/kyc-audit-log-utils.js`. Backend API implementing `company-users` and admin company routes (not in this repo). |
| **DB - Collections** | Unknown in this repo; backend likely persists `CompanyUser` / user linkage documents — confirm in API service. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High (admin flows); Medium for standard-user **edit** submit path — see Open Questions. |
| **Disposition** | Unknown |
| **Open Questions** | `standard-users.js` `handleSubmit` (edit branch) references `this.state.adminFormId` and `editAdmin(this.state.adminFormId, …)` though state defines `standardUserFormId` only — likely copy-paste defect; verify runtime behaviour for editing standard users. Exact backend RBAC for admin company-user and `/admin/companies/.../change-owner` endpoints. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/views/admin/companies/edit/admins.js` (`Admins`)

- **Remove admin**: confirmation dialog → `api.updateCompanyUser(adminId, { body: JSON.stringify({ user: {}, is_owner: false }) })` → `PUT /company-users/:id`; then `updateCompanyUsers`.
- **Save (add/edit)**: builds `user` payload (salutation, names, email, phone); `body = JSON.stringify({ user: payload, is_owner: true })`.
  - Edit existing: `api.editAdmin(adminFormId, { body })`; if the target is the logged-in user, also `api.updateUser(response.data.user._id, …)`.
  - New admin without linking shareholder/director: `api.createAdmin(company._id, { body })` → `POST /companies/:companyId/company-users`.
  - Promote from company user: `api.editAdmin(shareholder_director_id, { body })` plus optional `updateUser` for self.
- **UI**: “Company's Admins”, “Add Company Admin” (uses `toggleAddCompanyAdminForm` with `COMPANY_USER_ROLES.ADMIN` from parent), “Transfer Ownership” → `handleClickTransferOwnership` (implemented in parent `index.js`).
- **Child**: `AdminsSection` receives admins list, KYC/Camunda props, `handleResendInvitation`, `handleForceInviteAcceptance`, etc.

### `src/views/admin/companies/edit/standard-users.js` (`StandardUsers`)

- **List**: table of standard users — name, email, invitation status (with CMS-driven `invitation_flow_without_kyc` tooltip behaviour).
- **Resend invitation**: `api.sendInvitation(id, { query: { isResendEmailInvite: true } })` → `POST /company-users/:id/invite`; optional `kycRecordAuditLog(company._id, "kyc-invitation-resent")`; may `updateCompanyUsers()` when `invitation_flow_without_kyc` enabled.
- **Remove**: dialog → `api.deleteCompanyUser(standardUserId)` → `DELETE /company-users/:id`.
- **Add/save**: `PersonFormFields` with `formType="standardUser"`; submit builds `JSON.stringify({ user: payload })` (no `is_owner` in body here). New user: `createAdmin` then `sendInvitation(postResponse.data.companyUser._id)` to issue invite.
- **Bug suspicion**: lines 120–126 use `adminFormId` / `this.state.adminFormId` instead of `standardUserFormId` in the edit branch.

### `src/utils/api.js` (endpoints)

- `createAdmin` → `POST ${base}/companies/${companyId}/company-users`
- `editAdmin` / `updateCompanyUser` → `PUT ${base}/company-users/:id`
- `deleteCompanyUser` → `DELETE ${base}/company-users/:id`
- `sendInvitation` → `POST ${base}/company-users/:companyUserId/invite`

### `src/views/admin/companies/edit/index.js` (parent)

- **Transfer ownership**: `api.transferCompanyOwnership(company._id, { body: JSON.stringify({ company_user_id: newCompanyOwnerId }) })` → `POST /admin/companies/:companyId/change-owner`.
- Renders `<Admins …>` and `<StandardUsers …>` with company state, `updateCompanyUsers`, and form visibility handlers.

### `src/utils/company-user-roles-utils.js`

- `COMPANY_USER_ROLES.ADMIN` vs `COMPANY_USER_ROLES.STANDARD_USER` (`'standard-user'`) — role model for company-level access.

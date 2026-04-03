# Manage corporate governance and ownership

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Marketing |
| **Feature Name** | Manage corporate governance and ownership |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (Sleek Admin — company edit / corp-sec operations) |
| **Business Outcome** | Statutory and ownership records for a client company stay accurate: officers, share capital, registers, and Sleek-managed secretary arrangements align with reality for compliance and downstream processes. |
| **Entry Point / Surface** | **sleek-website** admin: **Company edit** — `/admin/companies/edit/?cid={companyId}` (`AdminCompaniesEditView`), **Company Information** tab sections for directors, nominee directors, shareholders, share classes / allocation, company secretaries (including Sleek secretary), significant controllers register, registrable controllers, and designated representatives. |
| **Short Description** | Operations staff add, edit, and remove directors and nominee directors; individual and corporate shareholders (with optional document upload); share classes and per-shareholder allocations (`createCompanyShareItems` / `updateCompanyShareItem` / `updateCompanyShares` / `deleteCompanyShareItem`). They maintain company secretaries (natural and corporate, including default Sleek secretary from CMS), SCR entries, registrable controllers (ACRA-oriented validations), and designated representatives. Many flows call **`postCompanyOfficerAppointmentDetails`** to sync officer appointment history; CMS feature flags gate SCR, registrable controllers, designated representatives, corp-sec multi-secretary, and enhanced share allocation. |
| **Variants / Markets** | Multi-tenant CMS (`platformConfig.cmsAppFeatures`, `corpsec_squad` for share payment method column). **SG**-centric copy and ACRA/registrable-controller rules; **`getTenantBasedTextDisplay`** varies SG vs HK labels on registrable controllers table. Typical Sleek markets **SG, HK, UK, AU**; exact gates per tenant — use **Unknown** for unconfirmed per-tenant enablement of every sub-register. |
| **Dependencies / Related Flows** | **KYC** (directors/shareholders: `handleStartKyc`, Camunda workflows, invitations via `sendInvitation`). **Company user** model: `POST/PUT/DELETE` on `/companies/{id}/company-users` and `/company-users/{id}`. **Resource allocation** APIs under `/companies/{id}/company-resource-allocation/*`. **Officer history**: `POST /v2/company/{id}/company-officer-appointment-details`. **Shares**: `POST/PUT/DELETE` share items; `PUT /companies/{id}/shares` bulk shareholder share updates. Parent **`AdminCompaniesEditView`** (`index.js`) orchestrates tab visibility, `getCompany` / `updateCompanyUsers`, and share form submit. **sleek-back** (not in repo): persistence, RBAC, statutory filing side effects. |
| **Service / Repository** | **sleek-website**: `src/views/admin/companies/edit/directors.js`, `nominee-directors.js`, `shareholders.js`, `company-shares.js`, `company-secretaries.js`, `company-significant-controllers.js`, `company-registrable-controllers.js`, `designated-representatives.js`, `company-sleek-secretary.js`, `index.js`; `src/utils/api.js`. **sleek-back** (API host for routes above). |
| **DB - Collections** | **Unknown** — MongoDB collections are not referenced in sleek-website; backend likely uses `Company`, `CompanyUser`, company resource / allocation documents, and history collections for officer appointments. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact RBAC permission names for each sub-section on company edit. Whether all registers are available in every tenant or only SG/HK. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Parent shell — `src/views/admin/companies/edit/index.js` (`AdminCompaniesEditView`)

- Imports and renders **Directors**, **NomineeDirectors**, **Shareholders**, **CompanyShares** (`shareItems` from `calculateTotalShareItems`, `handleClickEditShare`, `handleClickRemoveShare` → `deleteCompanyShareItem`, `handleSubmitShareForm` → `createCompanyShareItems` / `updateCompanyShareItem` / `updateCompanyShares`).
- **Company secretaries**: `CompanySecretaries`; **Sleek secretary** flow: `CompanySleekSecretary` with `handleSubmit={handleAddDefaultSleekSecretary}` → `postCompanySecretary` with `is_sleek_secretary`, then `postCompanyOfficerAppointmentDetails` with role `SLEEK_SECRETARY`.
- **SCR / registrable / designated**: feature flags `significant_controllers_register`, `registrable_controllers`, `designated_representatives`; conditional render of `CompanySignificantControllers`, `CompanyRegistrableControllers`, `DesignatedRepresentatives`.
- Full-screen switches for “new form” modes (directors, shareholders, secretaries, registers) before returning main layout.

### `src/views/admin/companies/edit/directors.js`

- **Remove**: `updateCompanyUser` (clear `director`); if nominee, `deleteCompanyUser` with `ND_ENTRY_POINTS.COMPANY_INFO_MANUAL_ADD`.
- **Add / edit**: `createDirector` / `editDirector` (`POST /companies/{id}/company-users`, `PUT /company-users/{id}`); `sendInvitation` with `isInviteToAdminApp: true`; `updateUser` when editing self-linked director.
- **CMS**: `active_services.nominee_director`, `invitation.enabled_main_point_of_contact`.

### `src/views/admin/companies/edit/nominee-directors.js`

- Same API pattern as directors (`createDirector` / `editDirector` / `updateCompanyUser` / `deleteCompanyUser`); UI title “Nominee Directors”; parent distinguishes nominee director list vs ordinary directors.

### `src/views/admin/companies/edit/shareholders.js`

- **Remove**: `deleteShareholder` (corporate) or `updateCompanyUser` (clear `shareholder`).
- **Add / edit**: `createShareholder` / `editShareholder`; `sendInvitation`; file upload via `viewUtil.uploadFile` + `getUser().data.root_folder` for corporate business profile files.
- **CMS**: `companies.incorporation_new_pricing.has_shareholder_limit` may disable “Add shareholder”.

### `src/views/admin/companies/edit/company-shares.js`

- Presentational table of `shareItems` (name, class, currency, amounts, optional payment method from `corpsec_squad` CMS). **Edit/remove** delegated to parent via `onEditShare` / `onRemoveShare`.

### `src/views/admin/companies/edit/company-secretaries.js`

- **Add**: `postCompanySecretary` — natural vs corporate (`is_company_corporate_secretary`, `has_multiple_selection`); `postCompanyOfficerAppointmentDetails` for appointment/resignation history; `deleteCompanySecretary` on remove; `sendInvitation` for resend.
- Tables merge `standardUsers`, `companyCorporateSecretaries`, resigned rows; **Add Sleek Secretary** button delegates to parent when `has_default_sleek_secretary` and no active Sleek row.

### `src/views/admin/companies/edit/company-significant-controllers.js`

- Gated by `significant_controllers_register.enabled`.
- **CRUD**: `postCompanySignificantControllers`, `deleteCompanySignificantControllers`; `postCompanyOfficerAppointmentDetails` with role `SIGNIFICANT_CONTROLLER`.
- Form: `scr-form-fields.js` (nature of control, addresses, IDs, dates).

### `src/views/admin/companies/edit/company-registrable-controllers.js`

- Gated by `registrable_controllers.enabled`.
- **CRUD**: `postCompanyRegistrableControllers`, `deleteCompanyRegistrableControllers`; `postCompanyOfficerAppointmentDetails` with role `REGISTRABLE_CONTROLLER`.
- Validations: `confirmation_from_registrable_controller`, `record_filed_with_acra`; payload includes company `uen` from props; tenant-based column header via `getTenantBasedTextDisplay` (SG vs HK).

### `src/views/admin/companies/edit/designated-representatives.js`

- Gated by `designated_representatives.enabled`.
- **CRUD**: `postCompanyDesignatedRepresentatives`, `deleteCompanyDesignatedRepresentatives` (reload after save/remove).
- Form: `designated-representative-form-fields.js` (name, contact, address, capacity).

### `src/views/admin/companies/edit/company-sleek-secretary.js`

- Read-only display of CMS **`unique_sleek_secretary_default_values`** (name, number, address, contact). Submit wired to parent **`handleAddDefaultSleekSecretary`** (`postCompanySecretary` + `postCompanyOfficerAppointmentDetails`).

### `src/utils/api.js` (selected routes)

| Concern | HTTP (via `getBaseUrl()`) |
|---|---|
| Company users (directors/shareholders as users) | `POST /companies/{companyId}/company-users`, `PUT/DELETE /company-users/{id}` |
| Share items / allocation | `POST /companies/{id}/share-items`, `PUT .../share-items/{shareItemId}`, `DELETE ...`, `PUT /companies/{id}/shares` |
| Resource allocation (secretaries, SCR, registrable, designated) | `POST/DELETE .../company-resource-allocation/company-secretaries`, `.../significant-controllers`, `.../registrable-controllers`, `.../designated-representatives` |
| Officer appointment history | `POST /v2/company/{companyId}/company-officer-appointment-details` |

### Constants

- `COMPANY_HISTORY_OFFICER_APPOINTMENT_ROLES` / `STATUSES` in `src/utils/constants` align UI history posts with secretary, significant controller, registrable controller, and Sleek secretary roles.

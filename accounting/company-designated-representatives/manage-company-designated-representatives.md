# Manage company designated representatives

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company designated representatives |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (or operations user) with `companies` read (list, detail) or `companies` full (create, update, soft-remove); CMS admin feature `designated_representatives` must be enabled for all routes |
| **Business Outcome** | Designated representative records for a company stay accurate (identity, contact, capacity, address, appointment context), supporting corporate and compliance workflows that depend on who is appointed and whether they have resigned. |
| **Entry Point / Surface** | Sleek App / admin — company resource allocation for **Designated Representatives** (`/companies/:companyId/company-resource-allocation/designated-representatives`) |
| **Short Description** | Lists active or resigned appointees (`?isResigned=true`), loads one `CompanyResourceUser` by resource id, creates or merges profile and address fields under `data.designated_representative` for role type `designated-representative`, or soft-removes an entry via `is_removed`. All behaviour is gated on the `designated_representatives` admin app feature. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Sleek CMS app features (`appFeatureUtil.getAppFeaturesByName("designated_representatives", "admin")`); `Company` lookup; other company resource allocation roles sharing `CompanyResourceUser` / `ResourceAllocationRole` |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyresourceusers` (Mongoose `CompanyResourceUser`); `resourceallocationroles` (aggregate `$lookup` `from`, role type `designated-representative`; auto-created “Designated Representative” role if missing); `companies` (`Company.findById`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether product copy still refers to “company secretary” in one error path (`GET` by id); whether `cessation_date` is set anywhere outside this controller for DR rows (delete path only sets `is_removed`) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** (`controllers/company-designated-representatives.js`): Logger `designated-representatives-register`. Constant `DESIGNATED_REPRESENTATIVE = "designated-representative"`.
  - `GET /companies/:companyId/company-resource-allocation/designated-representatives/:resourceId` — `userService.authMiddleware`, `accessControlService.can("companies", "read")`; requires `designated_representatives` admin feature enabled (else generic `FORBIDDEN_REQUEST`); `Company.findById`; `CompanyResourceUser.findOne({ company, _id: resourceId }).populate("user")`.
  - `GET /companies/:companyId/company-resource-allocation/designated-representatives` — same auth and feature gate; ensures `ResourceAllocationRole` with `type: DESIGNATED_REPRESENTATIVE` exists (creates stand-alone role title “Designated Representative”, `order: 15` if missing); `?isResigned=true` sets match on `cessation_date` non-null vs null; aggregates with `$lookup` from `resourceallocationroles`, matches `role.type`, company, `data` ≠ null, `is_removed` ≠ true.
  - `POST` same list path — `can("companies", "full")`; validates optional body fields (`cu_id`, `date_of_entry`, `full_name`, `contact_details`, `remarks_notes`, `capacity`, `capacity_others`, `residential_status`, address lines, etc.); if existing `CompanyResourceUser` has `data.designated_representative`, merges into `data.designated_representative` and clears `is_removed`; otherwise creates new `CompanyResourceUser` with `resource_role` and nested `data.designated_representative`.
  - `DELETE .../:resourceId` — `companies` full + feature gate; sets `is_removed = true` on the resource (soft delete).
- **Schema** (`schemas/company-resource-user.js`): `company`, `user`, `resource_role`, `appointed_date`, `cessation_date`, `is_removed`, flexible `data` (DR payload under `designated_representative` in controller).
- **Schema** (`schemas/resource-allocation-role.js`): `type`, `title`, `order`, `is_stand_alone`, `is_deleted` — used for the designated-representative allocation role.
- **OpenAPI** (`public/api-docs/company-designated-representatives.yml`): Documents the REST paths and tag `company-designated-representatives` for API consumers.

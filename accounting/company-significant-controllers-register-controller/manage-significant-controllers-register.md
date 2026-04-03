# Manage significant controllers register

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage significant controllers register |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user / company staff with `companies` read (list, detail) or `companies` full (create, update, soft-remove) |
| **Business Outcome** | The company’s register of persons with significant control stays accurate (identity, nature of control, office address, appointment and cessation dates), supporting statutory SCR obligations and downstream documents. |
| **Entry Point / Surface** | Sleek App / admin — company resource allocation for **Significant Controllers Register** (`/companies/:companyId/company-resource-allocation/significant-controllers`) |
| **Short Description** | Lists active or resigned PSC rows, loads one entry, upserts SCR fields under `data.significant_controller` on a `CompanyResourceUser` tied to role type `significant-controllers`, or soft-removes an entry (cessation + `is_removed`). Create/update/delete require CMS admin feature `significant_controllers_register` to be enabled. |
| **Variants / Markets** | SG, HK, UK, AU |
| **Dependencies / Related Flows** | Sleek CMS app features (`AppFeatureService` via `getAppFeaturesByName`); `Company` lookup; incorporation / document flows (`automated_significant_controllers_register`, `significant_controllers_registry`) and `request-instance.significant_controllers` refs to `CompanyResourceUser` |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyresourceusers` (Mongoose `CompanyResourceUser`); `resourceallocationroles` (aggregate `from`, role type `significant-controllers`); `companies` (`Company.findById`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Exact product labels for the admin UI path; whether `corporate_name` on new-branch create is reachable (not in validation schema) |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Controller** (`controllers/company-significant-controllers-register-controller.js`): Logger `significant-controllers-register`. `GET /companies/:companyId/company-resource-allocation/significant-controllers/:resourceId` — `userService.authMiddleware`, `accessControlService.can("companies", "read")`; loads `CompanyResourceUser` by company + `resourceId`, populates `user`. `GET /companies/:companyId/company-resource-allocation/significant-controllers` — same auth; optional `?isResigned=true` filters `cessation_date`; ensures `ResourceAllocationRole` with `type: "significant-controllers"` exists (creates stand-alone role “Significant Controllers Register” if missing); aggregates with `$lookup` from `resourceallocationroles`, matches role type, company, non-null `data`, `is_removed` ≠ true. `POST` same base path — `can("companies", "full")`; gates on `appFeatureUtil.getAppFeaturesByName("significant_controllers_register", "admin").enabled`; validates SCR payload (dates, ID, address JSON, `scr_nature_of_control`, etc.); updates existing `CompanyResourceUser` or creates new with `data.significant_controller` and `resource_role` for SCR role. `DELETE .../:resourceId` — `companies` full + feature flag; sets `cessation_date` to now and `is_removed` true.
- **Schema** (`schemas/company-resource-user.js`): `company`, `user`, `resource_role`, `appointed_date`, `cessation_date`, `is_removed`, flexible `data` (SCR nested under `significant_controller` in controller).
- **Schema** (`schemas/resource-allocation-role.js`): `type`, `title`, `order`, `is_stand_alone`, `is_deleted` — used to define the SCR allocation role.
- **App features** (`utils/app-features-util.js`): `getAppFeaturesByName` resolves CMS-backed features (or mock in tests) for gating SCR writes/removes.

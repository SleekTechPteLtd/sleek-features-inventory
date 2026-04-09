# Assign nominee director to a company

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Assign nominee director to a company |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated Sleek user (company context); admin variant exists on a separate controller with `companies:full` |
| **Business Outcome** | A Singapore incorporation (or related) company can have Sleek’s pool-based nominee director attached when capacity rules allow, so statutory roles and downstream incorporation/customer-success tasks can proceed. |
| **Entry Point / Surface** | Sleek API: `POST` `/companies/:companyId/assign_nominee_director` (authenticated); optional body `entrypoint` for logging/counter logic; admin path `POST` `/admin/companies/:companyId/assign_nominee_director` in `controllers/admin/nominee-director-controller.js` |
| **Short Description** | Resolves an available nominee director user (pool ordering and limits when feature `updated_assigning_nd_process` is on; legacy default email/partner path otherwise), creates an accepted director `CompanyUser`, increments nominee-director assignment counters, then wires customer-success workflow: may add incorporation document tasks and pre-filing tasks, and runs user-validation helper that **skips** flipping the user-validation task to `available` when the new director is a nominee director. |
| **Variants / Markets** | SG (ACRA/name-reservation–oriented workflow tasks and templates; not evidenced for other markets in these files) |
| **Dependencies / Related Flows** | App feature `updated_assigning_nd_process` (pool, max companies per ND, exempted company statuses); `config.nominee_director` defaults; `autoTriggersNameReservationFiling` after ND `CompanyUser` create; `getPreFilingCheckTasksForUser` for CS workflow section tasks; request instances and document templates for incorporation |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyusers`, `users`, `nomineedirectorcompanycounts`, `companies`, `workflowinstances`, `workflowtasks`, `requestinstances` (when CS workflow tasks and document requests are created) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Product copy implies “unlocks validation”; code explicitly **does not** set the user-validation task to `available` when `companyUser.user.is_nominee_director` — confirm intended UX for incorporation KYC/validation vs other director types. Exact in-app screen that calls `POST /companies/.../assign_nominee_director` not located in these files. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router** (`controllers/nominee-director-controller.js`): `POST` `/companies/:companyId/assign_nominee_director` with `userService.authMiddleware`; body `entrypoint` passed through. Flow: `companyUserService.getNomineeDirector(companyId)` — if falsy, `200` with message that ND limit reached; else `assignNomineeDirector(companyId, userFound, { entrypoint })`; on success reloads `CompanyUser` with `user`, `company` → `cs_workflow_instance` → `presentation.sections.tasks`; `Promise.all([setValidationTaskStatusToAvailable(company, companyUser), addTasksToCSWorkflow(company, companyUser)])`; success `200` with `assigned_nominee_director`; errors `422`.
- **Selection & assign** (`services/company-user-service.js`): `getNomineeDirector(companyId)` — if `updated_assigning_nd_process` enabled, `getNomineeDirectorV2`: loads `NomineeDirectorCompanyCount` sorted by `assigned_companies_as_nd_filtered_by_company_status`, picks partner default or least-loaded ND from `available_nd_for_random_assigning` subject to `max_live_companies_per_nd` (enforced in prod or when test flag enabled); otherwise legacy `User.findOne` using `config.nominee_director.default` / partner default. `assignNomineeDirector(company, user, options)`: rejects duplicate `CompanyUser`; calls `nomineeDirectorService.incrementTotalAssignedCountOfND`; `CompanyUser.create` with `director`, `invitation_status: "accepted"`, `kyc_status: "approved"`; `autoTriggersNameReservationFiling(addedNd, true)`.
- **Counters** (`services/nominee-director/nominee-director-service.js`): `incrementTotalAssignedCountOfND` → `updateNDCounter` `$inc` on `assigned_companies_as_nd` and `assigned_companies_as_nd_filtered_by_company_status` (latter may be exempted for certain company statuses per feature config).
- **CS workflow** (`services/workflow/add-tasks-to-cs-workflow.js`): No-op if no `cs_workflow_instance` or company `status` is `live` / `live_post_incorporation`. Otherwise sequentially adds document-sign tasks (Deed of Indemnity, Form 45, ND service agreement, Notice of Nominee Director, share certificates, Notice of Registrable Controller) via `WorkflowTask` / `RequestInstance` / `WorkflowInstance.updateOne`; then merges `getPreFilingCheckTasksForUser` into presentation section 1 tasks if not already present.
- **User validation task** (`services/workflow/tasks/user-validation.js`): `setValidationTaskStatusToAvailable` sets first task in section 0 to `available` and may move company to `paid_and_incomplete` **unless** `companyUser.user.is_nominee_director` — then returns resolved without changing validation task status.
- **Schema** (`schemas/nominee-director-company-count.js`): `NomineeDirectorCompanyCount` — `user`, `assigned_companies_as_nd`, `assigned_companies_as_nd_filtered_by_company_status`.
- **Tests**: `tests/controllers-v2/nominee-director/assign-nominee-directors.js`, `tests/controllers/nominee-director/assign-nominee-directors.js` (admin base path).

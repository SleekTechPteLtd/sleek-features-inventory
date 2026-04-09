# Configure post-payment onboarding bypass and customer app access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Configure post-payment onboarding bypass and customer app access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (authenticated admin API; `companies` `full` for post-payment bypass; `customer_app_access` `full` for customer app flags) |
| **Business Outcome** | Support and operations can mark post-payment onboarding steps as bypassed for a company when appropriate, and toggle whether the customer app is available and whether admins see the control to disable it—so onboarding and app exposure match each client’s situation. |
| **Entry Point / Surface** | Sleek Admin — authenticated HTTP API on sleek-back: `POST /v2/admin/companies/:companyId/postpayment-onboarding-bypass-status`, `POST /v2/admin/company/:companyID/customer-app-access`. Exact admin UI labels and navigation are not defined in the referenced files. |
| **Short Description** | Updates per-company flags: merged `postpayment_onboarding_bypass_completion_status` (share/compliance and sign-process-documents tiles) and optional `is_customer_app_disabled` and `show_admin_disable_customer_app`. Customer-app changes attempt an audit entry via Sleek Auditor (`customer-app-access` entry type). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware` on both routes. **RBAC**: `accessControlService.can` as above. **Data**: `Company` Mongoose model. **Audit**: `auditorService.saveAuditLog` → Sleek Auditor HTTP API (`config.sleekAuditor.sleekAuditorBaseUrl`) for customer-app updates. **Related**: Post-payment customer onboarding flows (`is_dashboard_launched`, onboarding tickets referenced in `schemas/company.js` comments). |
| **Service / Repository** | sleek-back; external: Sleek Auditor (audit log for customer app changes) |
| **DB - Collections** | `companies` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether the customer-app audit comment is correct when `is_customer_app_disabled` is true—the handler labels that branch `"enabled"` and the other `"temporarily disabled"`, which may be inverted versus the flag name. Exact admin surfaces and regional rollout for these toggles. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/admin.js`

- **`POST /companies/:companyId/postpayment-onboarding-bypass-status`** — `buildPostRoute` → `userService.authMiddleware`, `accessControlService.can("companies", "full")`, `updatePostPaymentOnboardingBypassStatus`.

- **`POST /company/:companyID/customer-app-access`** — `buildPostRoute` → `userService.authMiddleware`, `accessControlService.can("customer_app_access", "full")`, `manageCustomerAppAccess`.

- Router mounted at **`/v2/admin`** in `app-router.js` (`router.use("/v2/admin", require("./controllers-v2/admin"))`).

### `controllers-v2/handlers/company/update-postpayment-onboarding-bypass-status.js`

- **`updatePostPaymentOnboardingBypassStatus`** — Validates body: `postpayment_onboarding_bypass_completion_status` required, type `Object`. `Company.findOne({ _id: params.companyId })`; merges with `lodash.merge` into `company.postpayment_onboarding_bypass_completion_status`; `company.save()`; returns `{ data: company }` on success. Errors: `ERROR_CODES.COMPANY.INVALID_REQUEST`, `DOES_NOT_EXISTS`, generic internal error from tenant config.

### `controllers-v2/handlers/company/customer-app-access.js`

- **`manageCustomerAppAccess`** — Validates optional booleans: `is_customer_app_disabled`, `show_admin_disable_customer_app`. `Company.findOne({ _id: params.companyID })`; sets fields if present; `buildAuditLog` + `auditorService.saveAuditLog` with entry context `"customer-app-access"` (errors in audit path logged, not fatal); `company.save()`; returns `{ id: company._id }`.

### `schemas/company.js`

- **`is_customer_app_disabled`**, **`show_admin_disable_customer_app`** — Booleans, defaults `false`; comment references disabling customer app via admin.

- **`postpayment_onboarding_bypass_completion_status`** — Subdocument: `is_share_and_compliance_bypassed`, `is_sign_process_documents_bypassed` (Tile 2 / Tile 3); related Jira references in schema comments (SA-5779, post-payment onboarding).

- Model: `mongoose.model("Company", companySchema)` → collection **`companies`**.

### `controllers-v2/handlers/auditor/all.js`

- **`saveAuditLog`** — Non-test env: HTTP `PUT` to `${config.sleekAuditor.sleekAuditorBaseUrl}/api/log` with audit payload (not MongoDB).

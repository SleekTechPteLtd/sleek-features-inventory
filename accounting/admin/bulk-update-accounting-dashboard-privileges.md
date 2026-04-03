# Bulk update accounting dashboard privileges

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk update accounting dashboard privileges |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations user (authenticated admin with `companies` full access) |
| **Business Outcome** | Internal staff can align many company users’ accounting dashboard module visibility with a master CSV pair, so each user sees the right dashboard pages without manual per-user configuration in the app. |
| **Entry Point / Surface** | Authenticated admin HTTP API: `POST /v2/admin/update-accounting-dashboard-privileges` (`app-router.js` mounts `controllers-v2/admin` at `/v2/admin`). Multipart form: `files` (array, max 2) — one filename must contain `Pages`, one must contain `User access`; body field `group_name` names the dashboard privilege group. Requires `userService.authMiddleware` and `accessControlService.can("companies", "full")`. Exact internal tool or script UI is not defined in these files. |
| **Short Description** | Accepts two CSV uploads: **Pages** maps human-readable `label` to `siteName` (routing/site path for the dashboard). **User access** lists `companyId`, `userId`, and `hasAccessTo` (comma-space separated labels matching Pages). For each row it validates MongoDB ids, resolves `Company`, `User`, and a `CompanyUser` link, builds a `modules` array from the Pages file (each module: `filter: []`, `label`, `site_name`), and **overwrites** or **creates** a `CompanyUserPrivilege` for that company–user pair and `group_name`. Responds with `newRecords`, `updatedRecords`, and `rejectedRecords` arrays. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: Exported Pages and User access CSVs from operational/accounting tooling (not in this repo). **Same repo**: Accounting dashboard UI and any readers of `CompanyUserPrivilege` (schema documents `group_name` e.g. `general_accounting_dashboard` pattern in comments). **Related**: Other company-user privilege flows that read/write `CompanyUserPrivilege`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `users` (read by id); `companies` (read by id); `companyusers` (read: link for company + user); `companyuserprivileges` (find by company + user + `group_name`, insert or update `modules`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether `hasAccessTo` labels missing from the Pages file still produce modules with `site_name` undefined (handler uses `pageDatum` from `find` — may yield sparse modules). Whether multiple dashboard `group_name` values are used in production beyond the single body value per request. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app-router.js`

- **`router.use("/v2/admin", require("./controllers-v2/admin"))`** — base path for the feature is `/v2/admin/...`.

### `controllers-v2/admin.js`

- **`router.route("/update-accounting-dashboard-privileges").post(userService.authMiddleware, accessControlService.can("companies", "full"), upload.array('files', 2), updateAccountingDashboardPrivilegesV2)`** — POST with up to two CSV files; `multer` destination `tmp/csv/`.

### `controllers-v2/handlers/company-user-privileges/updateAccountingDashboardPrivilegesV2.js`

- **`updateAccountingDashboardPrivilegesV2`**: Requires both files (by `originalname` containing `Pages` and `User access`), CSV MIME check via `verifyFileType`, and non-empty `group_name` (`422` otherwise).
- **CSV shapes**: Pages — headers after skip line 1: `label`, `siteName`. User access — `companyId`, `userId`, `hasAccessTo`.
- **Row processing**: `ObjectId` validation; `Company.findById`, `User.findById`, `CompanyUser.findOne({ company, user })`; split `hasAccessTo` on `", "`; **`buildModules(pagesData, hasAccessToPages)`** maps labels to `{ filter: [], label, site_name }`.
- **`CompanyUserPrivilege.findOne({ company, user, group_name })`**: if found, replaces `modules` and counts as update; else `new CompanyUserPrivilege({ company, user, modules, group_name })` and save.
- **Responses**: `200` JSON `{ message, newRecords, updatedRecords, rejectedRecords }`; `422` for missing files, invalid type, or missing `group_name`; `500` on error.
- **`unlinkFiles`**: temp uploads removed after processing.

### `schemas/company-user-privilege.js`

- **Mongoose model `CompanyUserPrivilege`**: fields `group_name`, `user`, `company`, `modules` (array of objects with `filter`, `site_name`, `label` per schema comments).

### Tests

- **`tests/controllers-v2/admin/update-accounting-dashboard-privileges/import.js`** — integration coverage for upload validation and happy path.

# View company statutory deadlines

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View company statutory deadlines |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (any logged-in user passing `userService.authMiddleware`; no `companies`/`full` gate on these routes) |
| **Business Outcome** | Clients can see their company’s compliance deadline timeline (financial year, AGM, annual return, and related types) in a safe, privacy-conscious form so they know what is due and what is already completed. |
| **Entry Point / Surface** | Sleek client app (or integrated client) — authenticated HTTP API on sleek-back: `GET /deadlines/companies/:companyId`; optional batch helper `POST /deadlines/get-statuses-and-admins-by-ids`. Exact in-app navigation labels are not defined in the referenced files. |
| **Short Description** | Loads all `Deadline` rows for a company, sorts by `completed_at` descending (most recently completed first), and maps each through `sanitizeDeadlineData` so `completed_by`, `createdAt`, and `updatedAt` are omitted for client-safe JSON. A separate POST accepts multiple company IDs and returns each company’s `status`, `name`, `partner`, plus the owner admin’s basic profile fields. |
| **Variants / Markets** | SG, HK, UK, AU (deadline enums and multi-platform `shared-data` include `deadlines.types` across regions; jurisdiction-specific UI copy not verified in these files) |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware` on both routes. **Data creation/maintenance**: Admin flows in `controllers/admin/deadline-controller.js` and `services/deadlines/agm-deadlines.js` populate and evolve deadlines; `DeadlineService` in `services/deadline-service.js` also creates/updates deadlines when FY/AGM/AR dates change (see `getOrCreateCompanyUpcomingDeadlines`, `createCompanyDeadlines`, `updateCompanyUpcomingDeadlines`). **Related read**: this controller only uses `sanitizeDeadlineData` from `DeadlineService`. **Schemas**: `Company`, `CompanyUser` (owner + populated `user`) for the batch status endpoint. **Config**: `config/shared-data.json` → `deadlines.types`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `deadlines` (Mongoose model `Deadline`); `companies` (read `_id`, `status`, `name`, `partner`); `companyusers` / `users` (owner lookup and user profile fields for batch response). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether additional authorization (e.g. company membership) is enforced elsewhere in the stack for `GET /deadlines/companies/:companyId` — only `authMiddleware` appears on this router. Whether the batch POST is still used by current client builds. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/deadline-controller.js`

- **`GET /deadlines/companies/:companyId`** — `userService.authMiddleware`. `Deadline.find({ company: req.params.companyId })`, `.sort({ completed_at: "desc" })`, then `deadlineService.sanitizeDeadlineData` per document. `422` on error.

- **`POST /deadlines/get-statuses-and-admins-by-ids`** — `userService.authMiddleware`. Body validated: `company_ids` array. Loads `Company` by IDs and `CompanyUser` with `is_owner: true`, populates `user` with `first_name`, `last_name`, `email`. Response merges company `status`/`name`/`partner` with `admin` per company. `422` on validation/cast errors.

### `services/deadline-service.js`

- **`sanitizeDeadlineData`** — Sets `completed_by`, `createdAt`, `updatedAt` to `undefined` on the deadline object before JSON serialization (client-safe display).

- Other static methods (`updateCompanyUpcomingDeadlines`, `getOrCreateCompanyUpcomingDeadlines`, `getCompanyUpcomingDeadlines`, `createCompanyDeadlines`) support deadline lifecycle used by admin and company flows; not invoked directly by `controllers/deadline-controller.js` beyond sanitization.

### `schemas/deadline.js`

- Mongoose model **`Deadline`**: fields `type` (enum from `sharedData.deadlines.types`), `deadline_at`, `completed_at`, `company` (ref `Company`), `completed_by` (ref `User`), `timestamps: true`. Default collection name: **`deadlines`**.

### `config/shared-data.json`

- **`deadlines.types`**: `financial_year`, `annual_general_meeting`, `extended_annual_general_meeting`, `date_annual_general_meeting_held`, `annual_return`, `extended_annual_return`, `date_annual_return_filed`.

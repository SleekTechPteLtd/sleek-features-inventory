# Manage company statutory deadlines

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company statutory deadlines |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (authenticated user with `companies` `full` via access control) |
| **Business Outcome** | Internal staff can maintain AGM, annual return, financial year, and related statutory deadline records so corporate compliance timelines stay visible and the financial year can advance when an annual return is filed. |
| **Entry Point / Surface** | Sleek Admin — authenticated HTTP API on sleek-back: `GET/POST /admin/companies/:companyId/deadlines`, `PUT /admin/companies/:companyId/deadlines/:deadlineId`, `DELETE /admin/deadlines/:deadlineId`, `GET /admin/companies/:companyId/get-agm-deadlines`. Exact admin UI labels and navigation are not defined in the referenced files. |
| **Short Description** | Lists upcoming and recent completed deadlines per company; creates deadline rows of configured types; completes or deletes deadlines; when a `date_annual_return_filed` deadline is created, rolls the company financial year forward (after `loadFye`), recreates next AGM and annual-return deadlines, and bulk-completes non–AGM/AR open deadlines; exposes AGM/AR context (last, extended, and in-progress “date held/filed” rows) for review. |
| **Variants / Markets** | SG (deadline types and ACRA-style flows align with Singapore company law concepts); other markets not branched in these files — **Unknown** for full multi-jurisdiction coverage |
| **Dependencies / Related Flows** | **Auth**: `userService.authMiddleware`, `accessControlService.can("companies", "full")`. **Company/FYE**: `Company.loadFye()`, `company.financial_year` updates when annual return filed. **AGM/AR logic**: `services/deadlines/agm-deadlines.js` (`findOrCreateNextAGMDeadline`, `findOrCreateNextAnnualReturnDeadline`, lookup helpers). **Audit**: `auditorService.saveAuditLog` / `buildAuditLog` on create, update, and AGM/AR create/reset paths. **Related (non-admin)**: `GET /deadlines/companies/:companyId` in `controllers/deadline-controller.js` lists company deadlines with sanitization for client surfaces. **Config**: `config/shared-data.json` → `deadlines.types` enum. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `deadlines` (Mongoose model `Deadline`); `companies` (read/update `financial_year` and FYE loading via company instance); `users` (populate `completed_by` on past deadlines; completion attribution). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Whether `DeadlineService.updateCompanyUpcomingDeadlines` is wired to any production company-update flow (repo search finds only unit tests and internal recursion, not admin or company controllers). **PUT** handler validates `deadline_at` but sets `completed_at` to “now” and does not persist `deadline_at` from the body — intended behavior vs. bug? Deprecated `POST /admin/deadlines/:deadlineId/complete-deadline` returns `{}`; confirm no consumers. Whether non-SG companies should use the same deadline rules (code is not jurisdiction-gated in cited files). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/admin/deadline-controller.js`

- **`GET /admin/companies/:companyId/deadlines`** — `authMiddleware`, `can("companies", "full")`. Parallel: `deadlineService.getOrCreateCompanyUpcomingDeadlines(req.company)` and `Deadline.find({ company, completed_at: { $ne: null } }).sort({ completed_at: "desc" }).limit(20).populate("completed_by")`. Response `{ upcoming, past }` with `completed_by` sanitized via `userService.sanitizeUserData`.

- **`POST /admin/companies/:companyId/deadlines`** — Same guards. Body: `type` (required, from `sharedData.deadlines.types`), `deadline_at` (required), optional `completed_at`. Creates `Deadline` with `company`, `type`, `deadline_at`. If `type == "date_annual_return_filed"`: loads company, `loadFye()`, adds 12 months to `financial_year`, `company.save()`, then `findOrCreateNextAGMDeadline(company, true, user)`, `findOrCreateNextAnnualReturnDeadline(company, true, user)`, finds incomplete deadlines and completes all whose `type` is not `annual_general_meeting` or `annual_return`. Audit log `"created deadline"`.

- **`PUT /admin/companies/:companyId/deadlines/:deadlineId`** — Same guards. Validates `deadline_at` required; loads deadline by id, sets `completed_at` and `completed_by`. Audit `"updated deadline"`. (Audit comment references `bodyCleaned.type`, which is not in the validation schema.)

- **`DELETE /admin/deadlines/:deadlineId`** — Same guards; `deadline.deleteOne()`; `204`.

- **`POST /admin/deadlines/:deadlineId/complete-deadline`** — Marked **DEPRECATED**; returns `{}`.

- **`GET /admin/companies/:companyId/get-agm-deadlines`** — Returns JSON: `lastAgmDeadLine`, `extendedAgmDeadLine`, `dateAgmHeld`, `lastAnnualReturnDeadLine` (from `findNextAnnualReturnDeadline`), `extendedAnnualReturn`, `dateAnnualReturnFiled` via `agm-deadlines` helpers.

### `services/deadline-service.js`

- **`getOrCreateCompanyUpcomingDeadlines`** — Delegates to `getCompanyUpcomingDeadlines`; if empty, `createCompanyDeadlines`.

- **`getCompanyUpcomingDeadlines`** — `Deadline.find({ company, completed_at: null })`.

- **`createCompanyDeadlines`** — After `company.loadFye()`: creates three `Deadline` rows — `financial_year` at `company.financial_year`, `annual_general_meeting` at `incorporation_date + 18 months`, `annual_return` at AGM `deadline_at + 30 days`.

- **`updateCompanyUpcomingDeadlines`** — Recursive update when incorporation date, financial year, AGM date, or annual return date change: adjusts FY/agm/ar open deadlines per rules (e.g. first AGM at incorporation + 18 months; subsequent AGM from last completions + 15 months / FY + 6 months with calendar-year cap; AR follows AGM + 30 days when AGM date shifts).

- **`sanitizeDeadlineData`** — Strips `completed_by`, `createdAt`, `updatedAt` for API responses.

### `services/deadlines/agm-deadlines.js`

- **Lookups** — `findLastAGMDeadline`, `findExtendedAGMDeadline`, `findDateAGMHeld`, `findLastAnnualReturnDeadline`, `findExtendedAnnualReturn`, `findDateAnnualReturnFiled`, `findNextAGMDeadline`, `findNextAnnualReturnDeadline` (various `type` filters and `completed_at` / sort by `createdAt`).

- **`findOrCreateNextAGMDeadline` / `resetAGMDeadline`** — Next open AGM or create/reset: new AGM at `financial_year + 9 months` when `financial_year` present; audit logs for create/update.

- **`findOrCreateNextAnnualReturnDeadline` / `resetARDeadline`** — Create/reset annual return at `incorporation_date + 42 days` when `incorporation_date` present; audit logs.

- **Commented legacy** — Older `completeDeadline` chain (AGM → AR → FY roll) is commented out; current annual-return-filed flow is driven from admin controller + company FY update.

### `schemas/deadline.js`

- **Model `Deadline`** — Fields: `type` (enum from `sharedData.deadlines.types`), `deadline_at`, `completed_at`, `company` (ref `Company`), `completed_by` (ref `User`); `timestamps: true`. **Collection**: `deadlines`.

### `schemas/company.js`

- **Relevant fields** — `financial_year`, `incorporation_date`, `last_fye_change_date`, `last_filed_fye`, `current_fye`, `reminder_dates` (AGM deadline slots), `fye_reminders` (per-FYE AGM reminder sent dates). **Method** — `loadFye` (and related FYE sync) used when rolling FY on annual return filed and when computing deadlines in services.

### `config/shared-data.json` (`deadlines.types`)

- `financial_year`, `annual_general_meeting`, `extended_annual_general_meeting`, `date_annual_general_meeting_held`, `annual_return`, `extended_annual_return`, `date_annual_return_filed`.

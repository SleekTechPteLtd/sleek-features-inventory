# Manage company statutory registers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company statutory registers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (admin) |
| **Business Outcome** | Corporate statutory books (allotments, officers, charges, directors and shareholding, member ledgers, transfers, nominee directors, registrable controllers, debentures, and related line types) stay complete and auditable, including soft-deleted lines with a required comment for traceability. |
| **Entry Point / Surface** | Sleek Back **admin** HTTP API: `GET/PUT/DELETE` under `/admin/companies/:companyId/registers` (legacy controller mounted at `/` via `app-router.js` glob). Consumed by authenticated users with company **admin** management rights—not a public surface. |
| **Short Description** | Lists or bootstraps per-company **Register** documents by type, returns a single register with populated line editors, appends new lines with type-specific payload validation, and soft-deletes lines by marking them deleted with a mandatory comment and `updated_by`. |
| **Variants / Markets** | SG, HK, UK, AU (`registers.types` appears in `config/shared-data.json` and `multi-platform/config/*/shared-data.json`); which markets expose the admin UI in production is Unknown. |
| **Dependencies / Related Flows** | `userService.authMiddleware`; `companyService.canManageCompanyMiddleware("admin")`; **Company** and **User** refs on `Register`; separate **registrable controller** / compliance flows may overlap conceptually but are not called from this module. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `registers` (Mongoose model `Register`); `companies` (ref); `users` (ref on `lines.updated_by`). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether the client app is still the primary consumer or only internal ops; no OpenAPI decorators on this legacy controller. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller (`controllers/admin/register-controller.js`)

- **GET** `/admin/companies/:companyId/registers` — `userService.authMiddleware`, `companyService.canManageCompanyMiddleware("admin")`. If no registers exist, `registerService.createAllRegistersForCompany(companyId)`; else returns existing `Register.find({ company })`.
- **GET** `/admin/companies/:companyId/registers/:registerType` — validates `registerType` against `sharedData.registers.types`. `Register.findOne({ company, type }).populate("lines.updated_by")`; if missing, `createAllRegistersForCompany` then picks the requested type; response passed through `registerService.sanitizeRegister`.
- **PUT** `/admin/companies/:companyId/registers/:registerType` — body validated with `registerService.getRegisterTypeValidator(registerType)`; rejects empty body; `registerService.insertNewLine(companyId, body, registerType, req.user._id)`.
- **DELETE** `/admin/companies/:companyId/registers/:registerType/line/:lineId` — body must include `comment` (required string); `registerService.deleteLine(companyId, lineId, registerType, req.user._id, comment)`.

### Service (`services/register-service.js`)

- **getRegisterTypeValidator** — per-type field validators for: `applications_and_allotment`, `officers`, `charges`, `directors_and_shareholding`, `member_and_share_ledger`, `transfers`, `nominee_directors`, `registrable_control`, `debentures`; invalid type rejects.
- **createAllRegistersForCompany** — `Promise.all` over `sharedData.registers.types`, each `Register.create({ company, type, lines: [] })`.
- **insertNewLine** — `findOne` by company + type; `lines.push({ updated_by, data })`; `save()`.
- **deleteLine** — finds line by `_id`; sets `updated_by`, `deleted: true`, `comment`; `save()` (soft delete).
- **sanitizeRegister** — maps `lines[].updated_by` through `userService.sanitizeUserData`.

### Schema (`schemas/register.js`)

- **Register**: `company` → `Company`; `type` enum `sharedData.registers.types`; `lines` array of subdocuments with `updated_by` → `User`, `data` (JSON), `deleted` (default false), `comment`, timestamps.
- Mongoose model name: **`Register`**.

### Config (`config/shared-data.json` → `registers.types`)

- `applications_and_allotment`, `officers`, `debentures`, `charges`, `directors_and_shareholding`, `member_and_share_ledger`, `transfers`, `nominee_directors`, `registrable_control`.

### Routing

- `app-router.js`: `glob.sync("./controllers/**/*.js")` → `router.use("/", require(...))` for legacy controllers including this file.

### Tests

- `tests/controllers/register-controller/` — `get-registers.js`, `get-register.js`, `insert-new-line.js`, `delete-line.js`.

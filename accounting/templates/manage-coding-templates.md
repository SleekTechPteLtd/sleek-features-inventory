# Manage coding templates

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage coding templates |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Bookkeeper, Finance User, Admin |
| **Business Outcome** | Teams can save and reuse named templates so accounting coding setup stays consistent and faster to apply across work. |
| **Entry Point / Surface** | API surface `templates` on acct-coding-engine (`GET/POST/PUT/DELETE`); in-app navigation path Unknown |
| **Short Description** | List templates with optional name filter and pagination; create a template with a unique name; update or delete by id; fetch one by id. Stored in MongoDB on the coding-engine connection. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **MongoDB** connection `sleek_acct_coding_engine` (`DBConnectionName.CODING_ENGINE`); **seeding** via `TemplateSeeder` / `seeder.ts` for bulk insert; no Xero, SleekBooks, or Kafka calls in this module. |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | `templates` (Mongoose default for `Template` schema) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Low |
| **Disposition** | Unknown |
| **Open Questions** | `TemplateModule` is not imported in `app.module.ts`, so the `templates` HTTP routes do not appear mounted in the main Nest bootstrap—confirm whether this API is exposed elsewhere, behind a feature flag, or is legacy. `TemplateController` has no `AuthGuard` (unlike most controllers); if mounted, confirm intended auth. Update error copy references “permission” though the failure is missing/invalid template. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/modules/template/template.controller.ts`

- **Routes** (Swagger tag `template`): `GET /templates` (query `name`, `skip`, `limit`), `POST /templates`, `PUT /templates/:id`, `DELETE /templates/:id`, `GET /templates/:id`.
- **Guards**: none declared on this controller (contrast with `document`, `ledger-transaction`, etc.).

### `src/modules/template/template.service.ts`

- **DB**: `@InjectModel(Template.name, DBConnectionName.CODING_ENGINE)` — `Model<TemplateDocument>`.
- **findAll**: optional case-insensitive regex on `name`; returns `{ total, data }` with `skip`/`limit`.
- **create**: requires `name`; rejects duplicate via `count(template)` on full payload; `save()`.
- **update**: `findOneAndUpdate({ _id: id }, template)`; throws if not found (message mentions “permission”).
- **delete**: `findByIdAndDelete`.
- **findById**: `NotFoundException` when missing.

### `src/modules/template/template.schema.ts`

- **Mongoose** class `Template` with `name` (optional in schema props) and `timestamps: true`. Collection name follows Mongoose default (`templates`).

### `src/modules/template/template.constants.ts`

- DTOs: `FindAllRequest`, `FindAllResponse`, `CreateTemplateRequest` (`name`), `UpdateTemplateRequest` (`name` optional).

### `src/modules/template/template.module.ts`

- Registers `Template` with `TemplateSchema` on `DBConnectionName.CODING_ENGINE`; exports `TemplateService`.

### Deployment note

- **`src/app.module.ts`**: `TemplateModule` is not listed among imports; only `Template` schema/seeders appear in `src/seeder.ts`. The REST surface may not be active in the standard app build unless wiring is added elsewhere.

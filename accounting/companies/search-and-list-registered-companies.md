# Search and list registered companies

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Search and list registered companies |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Integration |
| **Business Outcome** | Operators and integrated systems can resolve which companies exist in the local accounting registry and retrieve identifiers (name, UEN, Sleek id) for review and downstream workflows. |
| **Entry Point / Surface** | `sleek-erpnext-service` HTTP API: `GET /companies/list` with optional query params `name`, `uen`, `sleek_id`, `limit`, `offset`. No `Authorization` check on this route in the controller (contrast with `POST /companies/create-list`). Exact Sleek app navigation path is not defined in this repo. |
| **Short Description** | Returns a paginated slice of company records from MongoDB filtered by exact match on any supplied fields (`name`, `uen`, `sleek_id`). Multiple filters combine as an AND query. Pagination uses query `limit` and `offset`; see Open Questions for a possible parameter wiring issue. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `POST /companies/create-list` (sync/update path) pulls from ERPNext and enriches via SleekBack and BigQuery before upserting into the same `Companies` collection — that flow populates the registry this list reads. **Downstream**: Any process that needs a local registry of company names, UENs, and Sleek ids for accounting tooling. |
| **Service / Repository** | sleek-erpnext-service |
| **DB - Collections** | `companies` (Mongoose model `Companies` / `CompaniesSchema`; default pluralised collection name). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `getCompaniesFromDB` applies `.limit(...)` on the `offset` query param and `.skip(...)` on the `limit` param — confirm whether callers swap params intentionally or this is a bug. Unauthenticated `GET /companies/list` vs token-required `POST /companies/create-list`: intended exposure for the list endpoint? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/companies/companies.controller.ts`

- **`@Controller('companies')`** — base path `/companies`.
- **`GET /list`** → `getAllCompanies`: `@ApiOperation({ summary: 'Get Existing Companies' })`; passes `query.name`, `query.uen`, `query.sleek_id`, `query.limit`, `query.offset` to `CompaniesService.getCompaniesFromDB`. No `@Request()` / authorization header validation on this handler.
- **`POST /create-list`** (`updateCompaniesUEN`): requires non-empty `Authorization` header or throws `401 Invalid Token`; calls `updateCompaniesInDB` (async fire-and-forget in controller — not awaited). **Out of scope** for this capability but shows auth surface difference.

### `src/companies/companies.service.ts`

- **`@InjectModel(Companies.name)`** — Mongo `Companies` model.
- **`getCompaniesFromDB(name, uen, sleek_id, limit, offset)`**: builds `dbQuery` with optional exact-match fields; `companiesModel.find(dbQuery).limit(Number(offset) || 0).skip(Number(limit) || 0).exec()`. **Other methods** in this service (`getCompaniesData`, `updateCompaniesInDB`, ERPNext, `SleekBackService`, `BQService`) support the sync/update pipeline, not the list endpoint.

### `src/companies/schemas/companies.schema.ts`

- **`@Schema({ timestamps: true })`** — `createdAt` / `updatedAt` implied.
- **Fields**: `name` (required string), `sleek_id`, `uen`, `last_sync`, `status` (enum `created` \| `valid` \| `invalid`), `dext_account_ids`, `ledger` (`xero` \| `sb`), `hubdoc_id`, `incorporation_date`, `current_fye`, `sync_start_date`.

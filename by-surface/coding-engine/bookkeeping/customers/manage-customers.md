# Manage customers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage customers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | The supplier-rules customer directory stays searchable and extensible so operators can register and find customers used in downstream rules and workflows, with an audit trail when new customers are added. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API: `GET /customers` (paginated list, optional `name` and `search`), `POST /customers` (create). `AuthGuard` is present in imports but commented on both routes — confirm whether callers rely on network trust, another gateway, or this is technical debt. Exact Sleek app navigation path is not defined in this repo. |
| **Short Description** | Operators browse customers in a paginated list, optionally filtering by case-insensitive regex on `name` or using MongoDB text search on `name`. They register new customers with a required lowercase-trimmed `name` and optional `parent_id`, `potential_duplicate`, `status`, and `created_by`. On create, the service writes an audit entry to Sleek Auditor with user attribution from `req.user` and a tag keyed to the new document id (`CES_<id>`). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `SleekAuditorService` posts to `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with API key auth. **Upstream/downstream**: Customer records support supplier-rules domain data; parent/child and duplicate flags suggest alignment with hierarchy or deduplication flows elsewhere (not wired in this slice beyond persistence). |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | `customers` (Mongoose model `Customer` on MongoDB connection `supplier_rules` / `DBConnectionName.SUPPLIER_RULES`; default pluralised collection name). Text index on `name` for `$text` search. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `AuthGuard` is commented on customer routes — intended exposure? Customer create audit call does not pass `companyId` / `uen` into `insertLogsToSleekAuditor`; confirm whether company-scoped audit is required. `get` and `create` catch blocks return the raw `error` instead of throwing HTTP exceptions (inconsistent error handling). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/customer/customer.controller.ts`

- **`@Controller("customers")`** — base path `/customers`.
- **`GET /`** → `getCustomers`: query `PaginationDto` (`page`, `limit`), optional `name`, `search` → `CustomerService.get`. `@ApiOperation` summary: "Gets customers in paginated list". `AuthGuard` import present but decorator commented out.
- **`POST /`** → `createCustomer`: body `CreateCustomerDto`, passes `req.user` → `CustomerService.create`. `@ApiOperation` summary: "Adds new customers data". `AuthGuard` commented out.

### `src/customer/customer.service.ts`

- **`@InjectModel(Customer.name, DBConnectionName.SUPPLIER_RULES)`** — Mongo `Customer` on connection `supplier_rules`.
- **`get`**: builds `filterQuery` with optional `name` as case-insensitive regex on `name`; optional `search` as `$text` `$search` on the text index; projects `{ _id, name }`; `countDocuments`; if `limit` and `page`, `skip`/`limit` else returns all matches; returns `{ data, totalCount, totalPages? }`.
- **`create`**: `customerModel.create(customerDetails)`; on success calls `sleekAuditorService.insertLogsToSleekAuditor` with `type: "log"`, message/event strings including customer name, `userFirstName` / `userLastName` / `userId` from `user` (`first_name`, `last_name`, `email`), `action`, and `tags: [\`CES_${createdCustomer._id}\`]`.

### `src/customer/customer.schema.ts`

- **Fields**: `name` (required, trim, lowercase), `parent_id`, `potential_duplicate`, `status`, `created_by` (ObjectIds where applicable); `timestamps: true`.
- **`CustomerSchema.index({ name: "text" })`** — enables `$text` search used by `search` query param.

### `src/customer/dto/create-customer.dto.ts`

- **Validation**: `name` required string; optional `parent_id`, `potential_duplicate`, `status`, `created_by` (class-validator + Swagger `@ApiProperty`).

### `src/sleek-auditor/sleek-auditor.service.ts`

- **`insertLogsToSleekAuditor`**: `POST` `${SLEEK_AUDITOR_BASE_URL}/audit-logs` with `Authorization: SLEEK_AUDITOR_API_KEY`; maps `actionBy`, `company`, `text`, `action`, `newValue`, `entryType`, `tags` from caller payload.

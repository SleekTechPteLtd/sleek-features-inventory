# Browse company supplier relationships and metrics

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Browse company supplier relationships and metrics |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Teams can see how many documents and supplier-specific rules are tied to each supplier for a company, with filtering and paging, so they can review coverage and workload without pulling raw data manually. |
| **Entry Point / Surface** | **supplier-rules-service** HTTP API (NestJS, default listen `4002` in `main.ts`): **POST** `/company-supplier` with JSON body `pagination`, optional `filter`, optional `sortBy` / `sortOrder`; **POST** `/company-supplier/update-count` to merge counter deltas. No controller-level auth guards or `@ApiOperation` decorators in these files — caller identity and product UI path are not defined in this repo. |
| **Short Description** | Lists `CompanySupplier` rows with total count and page of results. Filters by `company_id`, `supplier_name`, and/or `supplier_id`. Sorting uses dynamic `sortBy` with `sortOrder` `asc` \| `desc` (mapped to Mongo `1` / `-1`). Each row exposes `document_count` and `specific_rules_count`. A separate endpoint upserts counter fields by `company_id` + `supplier_name`, merging numeric deltas without letting totals go negative. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: Callers that POST document/rule activity to `update-count` (not referenced elsewhere in this workspace). **Data model**: Per-company supplier link with optional resolved `supplier_id`. Downstream UIs or jobs that need supplier-rule metrics are not enumerated in-repo. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection `supplier_rules`: Mongoose model `CompanySupplier` — default collection name `companysuppliers` (no explicit `collection` in schema). Fields: `company_id`, `supplier_name`, `supplier_id`, `document_count`, `specific_rules_count`, timestamps. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Which applications call these endpoints in production, and is ingress protected only by network policy? Should `updateCount` match documents using `supplier_id` when present (current `findOne` uses only `company_id` + `supplier_name`)? `UpdateCountMode` enum is imported in the controller but unused. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/company-supplier/company-supplier.controller.ts`

- **`CompanySupplierController`** — `@Controller("company-supplier")`.
- **POST** `/` (handler `getSuppliers`): body `pagination` → `PaginationDto`, optional `filter` → `FilterOptions`, optional `sortBy` / `sortOrder` strings → `CompanySupplierService.get`.
- **POST** `/update-count` (`updateCount`): body `UpdateCountDto` → `CompanySupplierService.updateCount`.
- **Auth**: No guards on this controller; global `ValidationPipe` only (`main.ts`).

### `src/company-supplier/filter-options.dto.ts`

- **`FilterOptions`**: optional `supplier_name`, `supplier_id`, `company_id` (class-validator / `Types.ObjectId` usage on strings — as written).
- **`SortOptions`**: optional `sortBy`, `sortOrder`.
- **`UpdateCountDto`**: `target` object (required), `company_id`, required `supplier_name`, optional `supplier_id`.

### `src/company-supplier/company-supplier.service.ts`

- **`get(pagination, { company_id, supplier_name, supplier_id }, { sortBy, sortOrder })`**: Builds Mongo query from defined filters; `countDocuments` + `find` with `skip`/`limit` from `pagination.page` (default 1) and `pagination.limit` (default 10); `sort` only when both `sortBy` and `sortOrder` are set; returns `{ total, data }`.
- **`updateCount({ target, company_id, supplier_id, supplier_name })`**: Early exit if missing `target`, `company_id`, or both `supplier_id` and `supplier_name` (actually requires `supplier_name` per DTO); loads document with `findOne({ company_id, supplier_name })`; merges `target` keys into existing counts with `validateAndSumNonNegativeCount`; `updateOne` with `upsert: true` on same `{ company_id, supplier_name }` conditions.

### `src/company-supplier/company-supplier.schema.ts`

- **`CompanySupplier`**: `company_id`, `supplier_name`, optional `supplier_id`, `document_count`, `specific_rules_count` (non-negative defaults).

### `src/company-supplier/company-supplier.module.ts`

- Registers `CompanySupplier` schema on Mongoose connection name **`supplier_rules`**.

### `src/main.ts`

- **`NestFactory.create`**, **`ValidationPipe`** global, Swagger at `/api`, **`listen(4002)`**.

# Sync supplier catalog from coding engine

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Sync supplier catalog from coding engine |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Supplier names that appear on documents in the coding engine are reflected in the supplier-rules master catalog so downstream supplier rules and categorisation stay aligned with real document data. |
| **Entry Point / Surface** | **supplier-rules-service** HTTP API: `POST /suppliers/sync` with optional query `startDate` (string). No `AuthGuard` on this route in code—treat as internal integration or job-triggered surface unless a gateway enforces auth upstream. |
| **Short Description** | Calls the coding engine to list distinct supplier names (optionally since `startDate`), then for each name either returns the existing MongoDB supplier row or creates a new enabled master supplier with default fields when missing. Returns combined results plus error flags if the coding engine request fails. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Coding Engine** HTTP API (`CODING_ENGINE_API_URL` + `GET /document/supplier-sync` with optional `startDate`); **supplier master** CRUD elsewhere in the same service (`SupplierService.create`, listing, rules). Downstream: supplier rules and document workflows that key off supplier names. |
| **Service / Repository** | supplier-rules-service, coding-engine (external HTTP service) |
| **DB - Collections** | `suppliers` (Mongoose model `Supplier` on MongoDB connection `supplier_rules`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | What process or schedule calls `POST /suppliers/sync` in each environment? Should this route be protected (currently unguarded in controller)? Exact semantics of coding engine `/document/supplier-sync` response shape and date filter. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **Route**: `@Controller("suppliers")`.
- **Sync**: `POST /suppliers/sync` → `syncSuppliers(@Query() requestQuery: SimpleSyncQueryDTO)` → `supplierService.syncSuppliers(requestQuery)`. **No** `@UseGuards(AuthGuard)` on this handler (contrast with `POST /`, `PUT /:supplierId`, etc.).

### `src/supplier/supplier.service.ts`

- **`syncSuppliers(requestQuery: SimpleSyncQueryDTO)`** (approx. lines 434–468): loads distinct supplier strings via `this.codingEngineService.getDistinctSuppliers(requestQuery.startDate)`. On HTTP failure sets `hasErrors` and `message` from the error. Otherwise `Promise.all` over each name: `findOne({ name: supplier })`; if none, `create({ name, parent_id: null, potential_duplicate: false, status: "enabled", created_by: null })` (no user on sync-created rows). Returns `{ queryResult, message, hasErrors }`.

### `src/supplier/dto/simpleSyncQueryDTO.ts`

- **`SimpleSyncQueryDTO`**: optional string `startDate` with `class-validator` (`@IsOptional`, `@IsString`).

### `src/utilities/external-services/coding-engine.ts`

- **`CodingEngineService.getDistinctSuppliers(startDate)`**: requires env `CODING_ENGINE_API_URL`. Builds `GET` to `{CODING_ENGINE_API_URL}/document/supplier-sync`, appends `?startDate=${startDate}` when provided. Uses `@nestjs/axios` `HttpService` with `Accept-Encoding: *`.

### `src/supplier/supplier.schema.ts`

- **Model**: `Supplier` — required unique lowercase `name`; optional `custom_display_name`, `parent_id`, `total_children`, `potential_duplicate`, `is_generic`, `status`, `created_by`. Timestamps enabled. Default Mongoose collection name **`suppliers`** (no explicit `collection` in `@Schema`).

# Manage supplier master data

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage supplier master data |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | The accounting supplier catalog stays accurate and usable for downstream categorisation and supplier rules. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API: `GET /suppliers` (paginated list, filters, search), `GET /suppliers/name`, `POST/PUT/DELETE /suppliers` and related routes; mutations and some reads use `AuthGuard` (Bearer / service token / dev bypass). Exact Sleek app navigation path is not defined in this repo. |
| **Short Description** | Operators and integrations create, update, and delete supplier records with unique lowercase names, optional display names, and parent/child relationships. Listing supports pagination (`page`, `limit`), regex filters on name and custom display name, free-text search on name and display name, and exclusions (by parent, child-only views, single id, parents with children). Deletes are guarded by checks against supplier rules, parent/child links, coding-engine document associations, and linked smart rules. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `SupplierRuleService` (block delete if specific rules exist; auto-publish batch touches rules), `SmartRuleService` (delete/reset on unlink/delete), `CodingEngineService` (distinct suppliers for sync, document counts for delete safety, user activity on detail read), `SleekAuditorService` (audit logs on create/update/link/unlink). **Downstream**: Supplier and company-supplier data feeds categorisation and rules elsewhere in supplier-rules-service. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | `suppliers` (Mongoose model `Supplier` on MongoDB connection `supplier_rules`; default pluralised collection name) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Several `GET` routes have no `AuthGuard` while mutations do — confirm network/trust boundaries for production. `get()` builds a `name` filter branch that references `search` inside `$regex` when only `name` is set (possible bug). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **`@Controller("suppliers")`** — base path `/suppliers`.
- **`GET /`** → `getSuppliers`: query `PaginationDto` (`page`, `limit`), optional `name`, `custom_display_name`, `search`, `exclude_children_and_self_by_parent_id`, `exclude_children_of_any_parent`, `exclude_id`, `exclude_parent_which_has_children`, `sortOrder`, `sortProperty` → `SupplierService.get`.
- **`POST /`** → `createSupplier`: `AuthGuard`, body `CreateSupplierDto` → `create`.
- **`PUT /:supplierId`** → `updateSupplier`: `AuthGuard` → `update`.
- **`DELETE /:supplierId`** → `deleteSupplier`: `AuthGuard` → `remove`.
- **`GET /id/:supplierId`** → `getSupplierById`: `AuthGuard` → `getSupplierById`.
- **`GET /name`** → `getSupplierByName`: query `GetSupplierByNameDto` (`supplier_name`) → `getSupplierByName`.

### `src/supplier/supplier.service.ts`

- **`@InjectModel(Supplier.name, "supplier_rules")`** — Mongo `Supplier` model on connection `supplier_rules`.
- **`create`**: `countDocuments` duplicate name (lowercase); `create(supplierDetails)`; `sleekAuditorService.insertLogsToSleekAuditor`.
- **`update`**: duplicate name check excluding current id; `findByIdAndUpdate` with `$set`; audit log.
- **`remove`**: loads supplier; blocks if `supplierRuleService.findSupplierRuleDetails` has rules; blocks if `parent_id` set; blocks if children exist; `codingEngineService.getAssociatedDocumentCountBySupplierName`; may `smartRuleService.delete`; `findByIdAndRemove`.
- **`get`**: builds `$and` of filters (custom display regex, name/search regex on `name` and `custom_display_name`, parent/child exclusions, `exclude_id`, `exclude_parent_which_has_children` via `total_children`); optional sort by `name`/`createdAt`; `countDocuments` + `find` with skip/limit; enriches rows with `getSpecificRulesCountAndSpecialty` (`noOfSpecificRules`, `specialty`).
- **`getSupplierByName`**: `findOne({ name: supplier_name })`.
- **Other controller routes** (sync, children, link/unlink, speciality, etc.) extend the same master data domain but are not in the expand file list; core CRUD + list + get-by-name are above.

### `src/supplier/dto/createSupplierDTO.ts`

- **`CreateSupplierDto`**: `name` (required), optional `custom_display_name`, `parent_id`, `potential_duplicate`, `is_generic`, `status`, `created_by` — class-validator + Swagger `@ApiProperty`.

### `src/shared/dto/pagination.dto.ts`

- **`PaginationDto`**: optional `page`, `limit` (integers ≥ 1) via `class-transformer` / `class-validator`.

### `src/supplier/dto/getSupplierByNameDTO.ts`

- **`GetSupplierByNameDto`**: `supplier_name` (string).

### `src/supplier/supplier.schema.ts`

- **`Supplier`**: `name` (unique, lowercase), `custom_display_name`, `parent_id`, `total_children`, `potential_duplicate`, `is_generic`, `status`, `created_by`; timestamps; indexes on `name` (including text), `custom_display_name`.

### `src/shared/auth/auth.guard.ts`

- **`AuthGuard`**: in `development`/`test` allows all; otherwise requires `authorization` header; accepts `SUPPLIER_SERVICE_AUTH_TOKEN` or forwards to external validation (commented Sleek-back path).

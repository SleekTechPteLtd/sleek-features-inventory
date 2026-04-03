# Review supplier specialty and rule coverage

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review supplier specialty and rule coverage |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators and integrated UIs can see each supplier’s role in the hierarchy (generic, standalone main, or child under a parent) alongside how heavily configured supplier-specific rules are—so publishing, linking, and rule decisions use full context. |
| **Entry Point / Surface** | Supplier Rules Service (NestJS): `POST /suppliers/specific-rule-count-and-specialty` (AuthGuard); paginated `GET /suppliers` enriches each row with the same metrics; `POST /suppliers/names/get-custom-display-name` returns batch `custom_display_name` by name. Product UI routes that call these APIs are not defined in this repo. |
| **Short Description** | Combines aggregate “specific rule” counts per supplier name (enabled rule fields across active `SupplierRule` documents) with specialty derived from supplier records (`is_generic`, `parent_id`). Supports batch requests by supplier name list. Supplier listing reuses this merge so list views show `noOfSpecificRules` and `specialty` without a second round trip per row. A separate endpoint resolves custom display names in bulk for labels in UIs. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream**: Supplier master data and `SupplierRule` documents in the same Mongo connection. **Related in repo**: `identifySupplierSpeciality` (`POST /suppliers/identify-supplier-speciality`) uses the same specialty logic; auto-publish batch updates (`update-auto-publish-settings-for-all-main`) and parent/child linking enforce rules about children and local rules. **Cross-service**: Coding Engine and other callers may supply `Authorization` for guarded routes. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection `supplier_rules`: `suppliers` (Mongoose model `Supplier`), `supplierrules` (Mongoose model `SupplierRule`; default pluralized collection name unless overridden) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Specialty for child suppliers is not set to a named enum value—`identifySupplierSpeciality` leaves `speciality` as `""` when `parent_id` is set and the supplier is not generic; confirm consumers treat empty string as “child”. The batch specific-rule count aggregates enabled fields across all companies for each supplier name, not per company. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **`POST /suppliers/specific-rule-count-and-specialty`** (`@UseGuards(AuthGuard)`): body `getSpecificRulesCountAndSpecialtyDTO` → `supplier_names: string[]` → `SupplierService.getSpecificRulesCountAndSpecialty`.
- **`GET /suppliers`**: paginated list; implementation in `SupplierService.get` enriches results (see below).
- **`POST /suppliers/names/get-custom-display-name`**: `{ supplier_names }` → `getSupplierCustomDisplayNameByNames` — returns documents with `name` and `custom_display_name` for batch display labels.
- **`POST /suppliers/identify-supplier-speciality`**: same underlying specialty resolution as used in the merge (different endpoint).

### `src/supplier/supplier.service.ts`

- **`get`**: After loading a page of suppliers, maps `supplierNames` and calls `getSpecificRulesCountAndSpecialty(supplierNames)`, then merges `noOfSpecificRules` and `specialty` onto each `toObject()` row for the supplier listing UI.
- **`getSpecificRulesCountAndSpecialty`**: Calls `SupplierRuleService.getSpecificRulesCountBySupplierNames`, then `identifySupplierSpeciality` for the same names, and zips rows by `supplier_name` so each result includes `no_of_specific_rules` (from rules service) and `specialty` (from supplier records).
- **`identifySupplierSpeciality`**: Loads suppliers by name with `name`, `total_children`, `parent_id`, `is_generic`; sets `SupplierSpeciality.GENERIC` if `is_generic`, else `SupplierSpeciality.MAIN` if no `parent_id`, else leaves specialty empty.

### `src/supplier/dto/getSpecificRulesCountAndSpecialtyDTO.ts`

- Validates `supplier_names` as an array (class-validator + Swagger).

### `src/supplier/services/supplier.interface.ts`

- **`IdentifySupplierSpeciality`**: `supplier_name`, optional `speciality` — shape returned to callers and merged into combined payloads.

### `src/supplier-rules/supplier-rules.service.ts`

- **`getSpecificRulesCountBySupplierNames`**: `$match` active rules where `supplier_name` ∈ list; aggregation unwinds document keys, counts fields with `is_enabled: true`, groups by `supplier_name`; maps every requested name to `{ supplier_name, no_of_specific_rules }` (zero if no rules).

### `src/supplier/enum/supplier.enum.ts`

- **`SupplierSpeciality`**: `MAIN = 'main'`, `GENERIC = 'generic'` — explicit values; child is not an enum member in code.

# Maintain company supplier document and rule counts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Maintain company supplier document and rule counts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (backend callers applying incremental count changes) |
| **Business Outcome** | Aggregated document and supplier-specific rule counts per company–supplier pair stay current and never drop below zero, so downstream listing and supplier rule statistics remain trustworthy. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API: `POST /company-supplier/update-count` (merge deltas); `POST /company-supplier` (paginated list with filters). No route-level auth decorators in code; global `ValidationPipe` only. |
| **Short Description** | Callers send incremental deltas in a `target` object; the service loads the existing row for `company_id` + `supplier_name`, adds each keyed delta to the stored value, clamps at zero, and `updateOne` with upsert so aggregates stay consistent over time. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: processes that emit document or supplier-rule changes and call this endpoint with deltas. Downstream: `POST /company-supplier` returns `document_count` and `specific_rules_count` for filtered company–supplier rows. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection `supplier_rules`; Mongoose model `CompanySupplier` (default collection name `companysuppliers` unless overridden). Fields: `company_id`, `supplier_name`, `supplier_id`, `document_count`, `specific_rules_count`. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `UpdateCountDto` includes optional `supplier_id`, but `updateCount` matches only `{ company_id, supplier_name }`; confirm whether callers must always send `supplier_name` and whether `supplier_id` should participate in the key. `UpdateCountMode` enum exists but is unused in the controller. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** — `company-supplier.controller.ts`: `POST /company-supplier` → `CompanySupplierService.get` (pagination, optional `filter`, `sortBy`, `sortOrder`); `POST /company-supplier/update-count` → `CompanySupplierService.updateCount` with `UpdateCountDto` body.
- **Merge logic** — `company-supplier.service.ts` `updateCount`: validates `target`, `company_id`, and `supplier_id` or `supplier_name` presence; builds conditions `{ company_id, supplier_name }`; `findOne` then `validateAndSumNonNegativeCount` sums each key in `target` with the existing document, using `0` for missing fields and capping each result at `0`; `updateOne(conditions, update, { upsert: true })`.
- **Schema** — `company-supplier.schema.ts`: `CompanySupplier` with `document_count` and `specific_rules_count` (`Number`, default `0`, `min: 0`), plus `company_id`, `supplier_name`, `supplier_id`.
- **DTOs** — `filter-options.dto.ts`: `FilterOptions` for list filters; `UpdateCountDto` with `target` (object), required `company_id` and `supplier_name`, optional `supplier_id`.
- **Tests** — `test/company-supplier/service/updateCount.spec.ts` exercises `updateCount` with `target.document_count` and `target.specific_rules_count` deltas.

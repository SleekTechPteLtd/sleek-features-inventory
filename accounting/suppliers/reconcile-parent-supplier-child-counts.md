# Reconcile parent supplier child counts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Reconcile parent supplier child counts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System |
| **Business Outcome** | Parent suppliers’ stored child counts stay consistent with real parent–child links so listing filters and hierarchy behaviour do not rely on stale `total_children` values. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API: `POST /suppliers/update-total-children-count-for-all-parent` returns `"success"` immediately while reconciliation runs asynchronously; **no** `AuthGuard` on this route — treat as operational/maintenance only and protect at network or gateway level. Not exposed as an end-user Sleek app screen in this repo. |
| **Short Description** | A maintenance job walks parent suppliers (records with `parent_id` null) in batches, aggregates actual child counts per parent from the supplier collection, and bulk-updates each parent’s `total_children` to match. Normal link/unlink flows already increment or decrement `total_children`; this job repairs drift after bulk edits, imports, or inconsistencies. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `linkChildSupplierByParentSupplierId` / `unlinkChildSupplierByParentSupplierId` maintain `total_children` on link and unlink; `get` list filtering uses `total_children` for `exclude_parent_which_has_children`. **Upstream**: Any process that changes `parent_id` without updating `total_children` creates the need for this reconciliation. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | `suppliers` (Mongoose model `Supplier` on MongoDB connection `supplier_rules`; default pluralised collection name) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Aggregation only emits parents that currently have at least one child; parents whose true count is zero may not receive a `$set` in a given run unless covered elsewhere — confirm whether a separate pass zeroes `total_children` for parents with no matching children. `bulkWrite` is invoked without `await` — confirm intentional fire-and-forget. Route has no auth — confirm deployment restricts who can call it. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **`POST /suppliers/update-total-children-count-for-all-parent`** → `updateTotalChildrenCountForAllParent`: calls `this.supplierService.updateTotalChildrenCountForAllParent()` and returns the string `"success"` (no `AuthGuard`).

### `src/supplier/supplier.service.ts`

- **`updateTotalChildrenCountForAllParent(circuit_break?: number)`** (comment: circuit_break × 1000 batch size ≈ max parent suppliers processed): loops with `skip`/`limit` 1000; loads parents where `parent_id` is null (`_id` only); builds **`aggregate`**: `$match` children whose `parent_id` is in the current parent id batch, `$group` by `parent_id` with `$sum: 1`; **`bulkWrite`** `updateOne` per group to `$set: { total_children: count }` on the parent `_id`. Loop stops when no more parent pages or when inner loop counter exceeds `circuit_break` (default 100).

### `src/supplier/supplier.schema.ts`

- **`Supplier`**: `parent_id`, **`total_children`** (number) — denormalised count maintained by link/unlink and reconciled by this job.

### Related maintenance context (same service)

- **`linkChildSupplierByParentSupplierId`**: `$inc: { total_children: 1 }` on parent after linking.
- **`unlinkChildSupplierByParentSupplierId`**: `$inc: { total_children: -1 }` when `total_children > 0`.
- **`get`**: filter branch `exclude_parent_which_has_children` uses `total_children` (`$exists: false` or `$lte: 0`).

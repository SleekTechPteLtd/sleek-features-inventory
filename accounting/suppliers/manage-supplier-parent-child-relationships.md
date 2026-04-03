# Manage supplier parent-child relationships

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage supplier parent-child relationships |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Child suppliers inherit parent behaviour (rules and smart‑rule defaults) so bookkeeping stays consistent when variants are grouped under one brand, while operators can still inspect hierarchy and resolve a parent from a child name. |
| **Entry Point / Surface** | **supplier-rules-service** HTTP API under `/suppliers`: link and unlink require `AuthGuard` (authenticated user). `GET /suppliers/:supplierId/children` and `GET /suppliers/get-parent-by-child-supplier-name/:supplier_name` have no `@UseGuards` in code — treat as internal/API surface unless a gateway adds auth. **Product UI path** (e.g. Sleek App navigation) is not defined in this repo. |
| **Short Description** | Operators link a child supplier to a parent (sets `parent_id`, increments `total_children`) or unlink (clears `parent_id`, decrements count). Link validates no self‑link, parent/child exist, child is not generic, child is not already a parent of others, and the child has no local supplier rules; on success the child’s smart rule is reset to default for inheritance. Read endpoints list children by parent id or resolve the parent document from a child’s name. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Supplier rules** — `SupplierRuleService.findSupplierRuleDetails` blocks linking if the child has specific/local rules. **Smart rules** — `SmartRuleService.resetSmartRuleToDefaultIfExists` after link. **Sleek Auditor** — audit logs for link/unlink. **List/get** filters (`exclude_children_*`, `total_children`) support supplier pickers elsewhere in the same service. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection **`supplier_rules`**, Mongoose model `Supplier` — default collection name **`suppliers`** (plural); `supplier_rules` documents also read via `SupplierRuleService` during link validation. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Are child listing and parent-by-name routes intended to be public/internal-only? Should they be guarded like link/unlink? Which Sleek product screen calls these endpoints? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **`GET /suppliers/:supplierId/children`** → `getAllChildSuppliersByParentId` → `SupplierService.getAllChildSuppliersByParentId`.
- **`POST /suppliers/:parentSupplierId/link-child/:childSupplierId`** + **`AuthGuard`** → `linkChildSupplier` → `linkChildSupplierByParentSupplierId`.
- **`POST /suppliers/:parentSupplierId/unlink-child/:childSupplierId`** + **`AuthGuard`** → `unlinkChildSupplier` → `unlinkChildSupplierByParentSupplierId`.
- **`GET /suppliers/get-parent-by-child-supplier-name/:supplier_name`** → `getParentSupplierInfoIfExistsByChildSupplierName` → `getParentSupplierInfoIfExistsByChildSupplierName` (param `GetSupplierByNameDto`).

### `src/supplier/supplier.service.ts`

- **`getAllChildSuppliersByParentId`**: `find({ parent_id: parentSupplierId })`, sort by `name`.
- **`linkChildSupplierByParentSupplierId`**: validates parent ≠ child; both IDs exist; child not already linked to this parent; child not `is_generic`; child has no descendants (`cannot add parent as child`); **`SupplierRuleService.findSupplierRuleDetails`** — rejects if child has any local rules (`total > 0`); **`findByIdAndUpdate`** child with `$set: { parent_id }`; **`$inc: { total_children: 1 }`** on parent; **SleekAuditor** log; **`smartRuleService.resetSmartRuleToDefaultIfExists(childSupplierId)`**.
- **`unlinkChildSupplierByParentSupplierId`**: validates child exists, has `parent_id`, and it matches `parentSupplierId`; **`$unset: { parent_id }`**; conditional **`$inc: { total_children: -1 }`** on parent when `total_children > 0`; **SleekAuditor** log.
- **`getParentSupplierInfoIfExistsByChildSupplierName`**: find child by `name`, require `parent_id`, load parent by id or throw.

### `src/supplier/dto/linkChildSupplierDTO.ts`

- **`LinkChildSupplierDto`**: `parentSupplierId`, `childSupplierId` (`Types.ObjectId`), Swagger `@ApiProperty`.

### `src/supplier/supplier.schema.ts`

- **`Supplier`**: `parent_id` (ObjectId, default null), `total_children` (number), `is_generic`, unique `name`, etc.

### Related (not exclusive to this capability)

- **`get`**: query filters `exclude_children_and_self_by_parent_id`, `exclude_children_of_any_parent`, `exclude_parent_which_has_children` support UI that hides children or parents-with-children when picking suppliers.

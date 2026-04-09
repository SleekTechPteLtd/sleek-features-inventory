# Bulk set auto-publish on main supplier rules

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Bulk set auto-publish on main supplier rules |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators set auto-publish for many suppliers for one company in a single run so per-company supplier rules stay consistent without editing each supplier separately. |
| **Entry Point / Surface** | **supplier-rules-service** HTTP API: `POST /suppliers/update-auto-publish-settings-for-all-main` with `AuthGuard` (Bearer / service token / dev bypass). Body: `supplier_names` (string array), `company_id` (string), `auto_publish` (boolean). Exact Sleek app navigation path is not defined in this repo. |
| **Short Description** | Processes supplier names in batches of ten: loads the company-specific supplier rule per name; updates `auto_publish` when it differs from the requested value (string `"true"` / `"false"` semantics); if no rule exists (`NotFoundException`), creates a new active rule with defaults for other fields and the requested `auto_publish`. Returns aggregate `failedCount` and `successFullCount`. Skips Mongo updates when the stored value already matches the target. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `SupplierRuleService.findSupplierRule`, `create`, `update` (Mongo + Sleek Auditor audit logs on create/update; optional `CodingEngineService.setUserActivity` when `user` is present — bulk flow does not pass `user` through). **Reads** `Supplier` documents when creating a missing rule (`findOne` by name). Downstream: any bookkeeping flow that honours per-company supplier rule `auto_publish` for publishing behaviour. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection **`supplier_rules`**: Mongoose model **`Supplier`** — default collection **`suppliers`**; Mongoose model **`SupplierRule`** — default collection **`supplierrules`** (no explicit `collection` in schema; default pluralised names). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `SupplierService.updateAutoPublishingSettingsForAllMain` calls `supplierRuleService.update` / `create` without the authenticated `user` from `AuthGuard`, so audit logs and coding-engine activity from `SupplierRuleService` may not attribute this bulk action to the caller. Product UI entry point and market-specific behaviour are not evidenced in-repo. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **`@Controller("suppliers")`** — base path `/suppliers`.
- **`POST /update-auto-publish-settings-for-all-main`** → `updateAutoPublishSettingsForAllMain`: `@UseGuards(AuthGuard)`, body `updateAutoPublishingSettingsForAllMainDto` → `SupplierService.updateAutoPublishingSettingsForAllMain`.

### `src/supplier/dto/updateAutoPublishingSettingsForAllMainDTO.ts`

- **`updateAutoPublishingSettingsForAllMainDto`**: `supplier_names` (`string[]`), `company_id` (`string`), `auto_publish` (`boolean`) — `class-validator` + `@ApiProperty`.

### `src/supplier/supplier.service.ts`

- **`updateAutoPublishingSettingsForAllMain`**: `batchSize = 10`; slices `supplier_names` and calls **`processBatch`** per slice; aggregates **`failedSupplierIds`** / **`successFulSupplierIds`**; returns `{ failedCount, successFullCount }` (note typo `successFullCount` in code).
- **`processBatch`**: for each name, **`getSupplierRuleDetails`** (`supplierRuleService.findSupplierRule` by `supplier_name` + `company_id` as `ObjectId`); if **`shouldUpdateAutoPublish`** then **`updateSupplierRule`**; else logs skip; on success pushes name to `successfulIds`. On **`NotFoundException`**, **`createSupplierRule`** then success. Other errors → `failedIds`.
- **`getSupplierRuleDetails`**: `supplierRuleService.findSupplierRule({ supplier_name, company_id })`, returns `toObject()`.
- **`shouldUpdateAutoPublish`**: compares `supplierRuleDetails.auto_publish.value` (`"true"` / `"false"` / other); returns whether an update is needed; non-true/false defaults to treating update as required (`return true`).
- **`createSupplierRule`**: `supplierModel.findOne({ name })`; builds `CreateSupplierRuleDto`-shaped object with `auto_publish: { value: auto_publish.toString(), is_enabled: true }` and disabled placeholders for other fields; **`supplierRuleService.create(supplierRule)`**.
- **`updateSupplierRule`**: **`supplierRuleService.update(supplierRuleId, { ...supplierRuleDetails, is_active: true, auto_publish: { value, is_enabled: true } })`**.

### `src/supplier-rules/supplier-rules.service.ts`

- **`findSupplierRule`**: `findOne({ supplier_name, company_id })`; throws **`NotFoundException`** if missing — triggers create path in bulk flow.
- **`create`**: validates `supplier_id`; Sleek Auditor log; optional user activity via Coding Engine; **`new this.model(supplierRule).save()`**.
- **`update`**: `findByIdAndUpdate` with `$set`; **`formatAuditLogForUpdateSupplierRule`** + Sleek Auditor; optional user activity.

### `src/supplier/supplier.schema.ts` / `src/supplier-rules/supplier-rules.schema.ts`

- Injected with **`@InjectModel(..., "supplier_rules")`** — both models share the **`supplier_rules`** Mongo connection name.

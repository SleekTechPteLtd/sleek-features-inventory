# Manage supplier smart rules

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage supplier smart rules |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Per-supplier defaults for currency, tax, publishing, and automation stay correct and reviewable so downstream coding and bookkeeping behave as the business intends. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API: `POST /smart-rules` (create/update, `AuthGuard`), `GET /smart-rules/supplier/:supplier_id` and `GET /smart-rules/:id` (read, `AuthGuard`), `DELETE /smart-rules/:id` (`AuthGuard`). Integration: `POST /smart-rules/search/:supplierName` and `GET /smart-rules/combination-list/:supplierName` (no `AuthGuard` in controller). Exact Sleek app navigation path is not defined in this repo. |
| **Short Description** | Operators upsert per-supplier smart rule documents (currency, category, tax rate, publish-as, description, auto-publish toggles and values). Reads can enrich combination lists from the ML smart-rules service. Successful creates and updates emit structured change summaries to Sleek Auditor (tagged with `CES_<supplier_id>`) for traceability. Deletes remove the smart rule document by id. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Same repo**: `MLSmartRuleService` / `ml_db` (`fetchSmartRuleCombinationList` for combination lists on read), `Supplier` model (lookup for generic search and populated supplier on fetch), `SleekAuditorService` (HTTP to `SLEEK_AUDITOR_BASE_URL` for audit logs on create/update path; `resetSmartRuleToDefaultIfExists` also audits). **Related**: Coding Engine uses `POST /smart-rules/search/:supplierName` per `@ApiOperation`. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection `supplier_rules`: `smartrules` (Mongoose model `SmartRule`, default pluralised collection name), `suppliers` (model `Supplier`, for search and populate). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `CreateSmartRuleDTO` nested type uses property `enabled` while persisted schema and diff logic use `is_enabled` — confirm client payload shape and whether validation aligns with stored documents. `delete` does not write an audit log (only create/update and reset-to-default paths use `SleekAuditorService`). |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/smart-rules/smart-rules.controller.ts`

- **`@Controller('smart-rules')`** — base path `/smart-rules`.
- **`POST /search/:supplierName`** → `genericSmartRuleSearch`: `@ApiOperation` — search by supplier name for Coding Engine smart rule integration → `SmartRuleService.genericSmartRuleSearch`.
- **`GET /supplier/:supplier_id`** → `findSmartRule`: `AuthGuard`, `@ApiOperation` — fetch by supplier id → `findSmartRuleBySupplier`.
- **`GET /combination-list/:supplierName`** → `getSmartRuleCombinationList`: combination list by supplier name → `getSmartRuleCombinationList`.
- **`POST /`** → `createOrUpdateSmartRule`: `AuthGuard`, body `CreateSmartRuleDTO`, passes `req.user` → `createOrUpdate`.
- **`DELETE :id`** → `delete`: `AuthGuard` → `SmartRuleService.delete`.
- **`GET :id`** → `findById`: `AuthGuard` → `findById`.

### `src/smart-rules/smart-rules.service.ts`

- **`@InjectModel(SmartRule.name, "supplier_rules")`** — `SmartRule` on connection `supplier_rules`; **`@InjectModel(Supplier.name, "supplier_rules")`** for supplier lookups.
- **`findSmartRuleBySupplier`**: `findOne({ supplier_id })`, `populate("supplier_id")`; clears `comb_list` then fills from `mlSmartRuleService.fetchSmartRuleCombinationList` + `parseSmartSupplierRules` when supplier has a name; if no rule doc, returns synthetic rule with combination list only when supplier exists.
- **`getSmartRuleCombinationList`**: ML fetch + `parseSmartSupplierRules`.
- **`createOrUpdate`**: loads existing rule by `supplier_id`; `_.reduce` over `originalSmartRules.toJSON()` compares keys (skips `_id`, `supplier_id`, `__v`, timestamps) using nested `value` / `is_enabled` vs incoming DTO fields; builds human-readable change strings; **`sleekAuditorService.insertLogsToSleekAuditor`** with `action` “updated smart rules” or “succesfully created smart rule settings”, `tags: [\`CES_${supplier_id}\`]`, user from `req.user` (`first_name`, `last_name`, `email`); **`findOneAndUpdate`** `{ supplier_id }`, `{ $set: smartRuleRequest }`, `{ new: true, upsert: true }`.
- **`delete`**: `findByIdAndDelete`; no auditor call.
- **`findById`**: `findById` or `NotFoundException`.
- **`genericSmartRuleSearch`**: case-insensitive exact name match on supplier, then `findSmartRuleBySupplier`.
- **`resetSmartRuleToDefaultIfExists`** (not exposed in listed controller file): `$set` default disabled empty values for rule fields; **`insertLogsToSleekAuditor`** for reset.

### `src/smart-rules/dto/createSmartRuleDTO.ts`

- **`CreateSmartRuleDTO`**: `supplier_id` (required); optional nested **`SmartRuleSubValues`**: `enabled`, `value` per field — **note**: class uses `enabled`; see schema.
- Fields: `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish`.

### `src/smart-rules/smart-rules.schema.ts`

- **`SmartRule`**: `supplier_id` ref `Supplier`; each of `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish` as `{ is_enabled: boolean; value: string }`; `comb_list` array; `@Schema({ timestamps: true })`.

### `src/sleek-auditor/sleek-auditor.service.ts`

- **`insertLogsToSleekAuditor`**: posts audit payloads to external Sleek Auditor API (used from smart rule create/update and reset flows).

### `src/shared/auth/auth.guard.ts`

- **`AuthGuard`**: guards authenticated routes on controller (development/test may bypass — same pattern as other inventory docs).

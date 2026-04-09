# Supplier smart rules for coding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Supplier smart rules for coding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System (Coding Engine and related automation); Bookkeeper / Finance User / Admin for rule configuration (authenticated API) |
| **Business Outcome** | Transaction coding can resolve a supplier, retrieve persisted rule preferences, and surface ML-derived account-code combinations so categorisation stays consistent across flows. |
| **Entry Point / Surface** | Coding Engine and integrations call `POST /smart-rules/search/:supplierName` and `GET /smart-rules/combination-list/:supplierName` without auth; Sleek apps or internal tools use guarded routes to fetch, create, update, or delete rules by supplier or rule id. |
| **Short Description** | The service matches suppliers by name or id, loads stored smart-rule settings from MongoDB, and enriches responses with combination lists from an ML-backed collection. It supports create/update with audit logging to Sleek Auditor and exposes combination data parsed for downstream coding use. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: supplier master data (`Supplier`), ML training outputs in `ml_db`. Downstream: Coding Engine (documented on controller); Sleek Auditor for change and reset events. Related: `resetSmartRuleToDefaultIfExists` and other supplier flows may invoke the exported service. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | `supplier_rules` connection: `smartrules` (Mongoose default for `SmartRule` schema), `suppliers`; `ml_db` connection: `smart_supplier_rules` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Whether market-specific behaviour exists elsewhere (not visible in these files); legacy `sync-ml-smart-rules` and bulk ML sync are commented—confirm whether combination data is maintained only via ML DB reads now. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/smart-rules/smart-rules.controller.ts`**: `SmartRuleController` under `@Controller('smart-rules')`. `POST /search/:supplierName` — `genericSmartRuleSearch` (`@ApiOperation`: search for smart rule by supplier name, used in Coding Engine). `GET /supplier/:supplier_id` — `findSmartRule` with `AuthGuard`. `GET /combination-list/:supplierName` — `getSmartRuleCombinationList` (no guard in code). `POST /` create/update with `AuthGuard`; `DELETE :id`, `GET :id` with `AuthGuard`. Sync ML endpoint commented out.
- **`src/smart-rules/smart-rules.service.ts`**: `SmartRuleService` uses `SmartRule` model on `supplier_rules` and `Supplier` model; injects `MLSmartRuleService`, `SleekAuditorService`. `findSmartRuleBySupplier` loads rule by `supplier_id`, clears `comb_list` then fills via `mlSmartRuleService.fetchSmartRuleCombinationList` + `parseSmartSupplierRules`; if no rule document, builds empty rule with combinations from ML only. `getSmartRuleCombinationList` delegates to ML fetch and parse. `createOrUpdate` upserts by `supplier_id`, diffs fields for audit, calls `sleekAuditorService.insertLogsToSleekAuditor`. `genericSmartRuleSearch` regex-matches supplier name then `findSmartRuleBySupplier`. `resetSmartRuleToDefaultIfExists` resets fields and audits. Private `parseSmartSupplierRules` maps ML `codes` tuples to `CombinationObjectDTO` (`code`, `name`, `total_documents`).
- **`src/ml-smart-rules/ml-smart-rule.service.ts`**: `MLSmartRuleService` reads `SmartRule` model on `ml_db`. `fetchSmartRuleCombinationList` finds document by regex on `supplier`, returns `codes` array or `[]`. `fetchSmartRules` returns all ML smart rules.
- **`src/ml-smart-rules/ml-smart-rule.schema.ts`**: Collection `smart_supplier_rules`, fields `supplier`, `supplier_frequency`, `codes`.
- **`src/smart-rules/smart-rules.schema.ts`**: Stored rule fields per supplier (`currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish`, `comb_list`).

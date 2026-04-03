# View supplier rule coverage and counts

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | View supplier rule coverage and counts |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, integrated clients (HTTP API consumers); authenticated users for company-scoped counts |
| **Business Outcome** | Operators and integrated systems can see how many active supplier rules apply to a supplier and how many company-specific rule dimensions are enabled for configuration and reporting. |
| **Entry Point / Surface** | `supplier-rules-service` HTTP API (no global prefix in `main.ts`): `GET /supplier-rules/suppliers` and `GET /supplier-rules/suppliers/count` (no route-level `AuthGuard`); `GET /supplier-rules/:companyId/count` (`AuthGuard`); `POST /supplier-rules/suppliers/:supplierId/count-specific-rules-by-company-id` (body: `company_ids`). |
| **Short Description** | Exposes counts of active supplier-rule documents for a supplier (optional filter by name or supplier id), a second metric that sums enabled per-dimension flags across matching documents, total rule documents per company, and per-company totals of enabled dimensions for a supplier across selected companies. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: supplier rule documents maintained via create/update/delete on the same service. Downstream: UIs or services that need coverage metrics; `CodingEngineService` is used elsewhere in this module (e.g. find-by-company-supplier) but not on these read-count paths. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | MongoDB connection name `supplier_rules`; Mongoose model `SupplierRule` (`supplier-rules.schema.ts`) — default collection name per Mongoose pluralization (`supplierrules` unless overridden). Queries use `is_active`, `supplier_name`, `supplier_id`, `company_id`, and dimension objects with `is_enabled` (e.g. `display_name`, `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish`, `document_type`, `bank_account`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `GET /supplier-rules/suppliers/count` derives enabled-field counts by iterating `Object.keys` on each document’s `_doc` (see `getSupplierRulesCount`), while `getSpecificRulesCountBySupplierIdAndCompanyId` uses a fixed list of nine dimensions; confirm whether both metrics should align and whether unauthenticated access to `/suppliers` and `/suppliers/count` is intentional. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Routes** — `supplier-rules.controller.ts`: `GET /suppliers` → `findSupplierRuleDetails` (`ApiOperation`: amount of rules tied to this supplier); `GET /suppliers/count` → `getSupplierRulesCount`; `GET /:companyId/count` with `AuthGuard` → `getSpecificRulesCountByCompanyId`; `POST suppliers/:supplierId/count-specific-rules-by-company-id` with `countSpecificSupplierRuleRequestDTO` body → `getSpecificRulesCountBySupplierIdAndCompanyId`.
- **Active rule document count** — `supplier-rules.service.ts` `findSupplierRuleDetails`: `countDocuments` with `is_active: true` and optional `supplier_name` (from decoded `name` query) or `supplier_id` from `findSupplierRuleDetailsQueryDTO`.
- **Enabled-dimension sum (list path)** — `getSupplierRulesCount`: same filter as above, then `find` and reduce over results counting keys where `cur[key]?.["is_enabled"]` is truthy (per-document keys summed).
- **Per-company document count** — `getSpecificRulesCountByCompanyId`: `countDocuments({ company_id })`.
- **Per-company enabled dimensions for supplier** — `getSpecificRulesCountBySupplierIdAndCompanyId`: `$match` on `supplier_id` and `company_id` in `$in`, `$group` by `company_id`, `$sum` of `$add` with `$cond` per dimension in `specific_rules_key_list` (display_name, currency, category, tax_rate, publish_as, description, auto_publish, document_type, bank_account) when `*.is_enabled === true`; maps to `countSpecificSupplierRuleDTO` (`company_id`, `total`).
- **DTOs** — `findSupplierRuleDetailsDTO.ts`: response shape `{ total }`; query `name` and `id` optional. `countSpecificSupplierRuleDTO.ts`: `countSpecificSupplierRuleRequestDTO` with `company_ids`; `countSpecificSupplierRuleDTO` with `company_id` and `total`.

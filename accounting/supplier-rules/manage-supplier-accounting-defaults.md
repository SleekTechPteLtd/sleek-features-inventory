# Manage supplier accounting defaults

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage supplier accounting defaults |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Finance User, Operations User |
| **Business Outcome** | Each supplier–company pair can carry persisted bookkeeping defaults (chart-of-account category, tax, currency, publishing, document type, bank account, and related toggles) so downstream coding and posting stay consistent without re-keying the same choices. |
| **Entry Point / Surface** | HTTP API on `supplier-rules-service` under `/supplier-rules` (NestJS). Authenticated routes use `AuthGuard` (`Authorization` header; in non-dev/test optionally `SUPPLIER_SERVICE_AUTH_TOKEN` or validation via forwarded auth to Sleek back end with `app-origin`). Several read/count routes are **not** guarded in code (see Evidence). End-user app navigation path is not defined in this repo. |
| **Short Description** | Creates, reads, updates, and deletes `SupplierRule` documents keyed by supplier and company. Each rule stores optional enabled/value pairs for display name, currency, category (COA-style data), tax rate, publish-as, description, auto-publish, document type, and bank account. Emits audit logs on create/update (Sleek Auditor) and records Coding Engine user activity on find-by-supplier/company, create, and update. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Internal**: `SleekAuditorService.insertLogsToSleekAuditor` (create/update); `CodingEngineService.setUserActivity` (supplier detail and supplier rule update flows). **Data**: MongoDB `supplier_rules` connection, `SupplierRule` model. **Related inventory**: company-level accounting settings and supplier master data in other services complement but do not replace per-supplier rules. |
| **Service / Repository** | supplier-rules-service |
| **DB - Collections** | `supplierrules` (Mongoose default collection for model `SupplierRule`; database connection name `supplier_rules`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `CreateSupplierRuleDto` validates through `auto_publish` only; schema also defines `document_type` and `bank_account` — confirm whether class-validator / `ValidationPipe` strips those fields on create/update or they are set only via other paths. Several endpoints omit `AuthGuard` (public read/count by supplier and by id; POST count-specific-rules); confirm intentional exposure for internal callers only vs oversight. `console.log` left in update path. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier-rules/supplier-rules.controller.ts`

- **GET** `/supplier-rules/suppliers` — `findRuleDetails`: total rule documents for supplier (`name` / `id` query); **no** `AuthGuard`.
- **GET** `/supplier-rules/suppliers/count` — `getSupplierRulesCount`: counts enabled “specific rule” fields across matching active documents; **no** `AuthGuard`.
- **GET** `/supplier-rules` — `findSupplierRule` (query `supplier_name`, `company_id`): **AuthGuard**; returns one rule or 404.
- **POST** `/supplier-rules` — `create`: **AuthGuard**; body `CreateSupplierRuleDto`.
- **PUT** `/supplier-rules/:id` — `update`: **AuthGuard**; body `CreateSupplierRuleDto`.
- **DELETE** `/supplier-rules/:id` — `delete`: **AuthGuard**.
- **GET** `/supplier-rules/:id` — `findById`: **no** `AuthGuard`.
- **GET** `/supplier-rules/:companyId/count` — `getSpecificRulesCountByCompanyId`: **AuthGuard**.
- **POST** `/supplier-rules/suppliers/:supplierId/count-specific-rules-by-company-id` — body `company_ids`; **no** `AuthGuard`; returns per-company counts of enabled specific-rule fields.

### `src/supplier-rules/supplier-rules.service.ts`

- **`findSupplierRule`**: `findOne({ supplier_name, company_id })`; optional `CodingEngineService.setUserActivity` with `last_activity: "supplier_detail"`.
- **`create`**: requires `supplier_id`; audit log “Created supplier rules…”; `setUserActivity` `supplier_rule_update`; `new this.model(supplierRule).save()`.
- **`update`**: `findByIdAndUpdate` with `$set`; `formatAuditLogForUpdateSupplierRule` → Sleek Auditor; `setUserActivity` `supplier_rule_update`.
- **`delete`**: `findByIdAndDelete`.
- **`findSupplierRuleDetails` / `getSupplierRulesCount`**: filter `is_active: true` and optional `supplier_name` / `supplier_id`; count documents or sum nested `*.is_enabled` keys.
- **`getSpecificRulesCountBySupplierIdAndCompanyId`**: aggregation counts enabled fields among `display_name`, `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish`, `document_type`, `bank_account` per `company_id`.

### `src/supplier-rules/supplier-rules.schema.ts`

- **Model** `SupplierRule`: `supplier_name`, `supplier_id`, `company_id`, `company_name`, `is_active`, and object fields `display_name`, `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish`, `document_type`, `bank_account` — each `{ is_enabled, value }` pattern (value typed per field: `CoaData` / arrays for category, `BankAccount` for bank account).
- **Index**: `{ supplier_name: 1, is_active: 1 }`.

### `src/supplier-rules/dto/createSupplierRuleDTO.ts`

- **`CreateSupplierRuleDto`**: validated fields include `supplier_name`, optional `supplier_id`, `company_id`, `company_name`, `is_active`, and optional objects for `display_name`, `currency`, `category`, `tax_rate`, `publish_as`, `description`, `auto_publish` (no `document_type` / `bank_account` in DTO).

### `src/supplier-rules/supplier-rules.constants.ts`

- **`FindSupplierRuleRequest`**: `supplier_name`, `company_id`.
- **`CoaData`**: `name`, `account_name`, `account_number`, `account_id`.
- **`BankAccount`**: `name`, optional Xero-aligned account identifiers.

### `src/supplier-rules/supplier-rules.module.ts`

- **`MongooseModule.forFeature([{ name: SupplierRule.name, schema: SupplierRuleSchema }], "supplier_rules")`**.

# Configure bulk auto-publish for main suppliers

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Configure bulk auto-publish for main suppliers |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can turn automatic publishing on or off for every main supplier at a company in one step and keep the company-level auto-publish flag aligned so receipt posting behaviour matches policy. |
| **Entry Point / Surface** | Coding Engine API `POST /supplier/toggle-auto-publish/:companyId` (authenticated); exact in-app navigation for operators not defined in these files |
| **Short Description** | For a company, discovers suppliers from receipt documents, classifies them as main via Supplier Rules, calls Supplier Rules to update auto-publish for all main suppliers, then sets `Company.disabled_auto_publish` on the coding-engine company record when the remote update succeeds. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Supplier Rules service** (`VITE_APP_SUPPLIER_RULES_API`): `POST /suppliers/identify-supplier-speciality`, `POST /suppliers/update-auto-publish-settings-for-all-main`; **MongoDB** Sleek Receipts `documentdetailevents` (aggregation to list suppliers per company); **MongoDB** coding-engine **companies** ( `disabled_auto_publish` ); downstream receipt publish flows that read company or supplier-rule auto-publish settings |
| **Service / Repository** | acct-coding-engine (orchestration); supplier-rules service (authoritative supplier rules and bulk auto-publish) |
| **DB - Collections** | `documentdetailevents` (read/aggregate by `company`); `companies` (Mongoose default for `Company` schema—update `disabled_auto_publish` by `company_id`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Confirm where `disabled_auto_publish` is enforced for receipt posting (readers not in the cited files); confirm product UI path and whether all regions use the same Supplier Rules speciality model. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `src/supplier/supplier.controller.ts`

- **Route**: `POST supplier/toggle-auto-publish/:companyId`
- **Auth**: `AuthGuard` on `toggleAutoPublishForMainSuppliers` (body: `SupplierToggleAutopublishSettingsDto`)
- **Delegation**: `supplierService.toggleAutoPublishForMainSuppliers(companyId, dto)`

### `src/supplier/supplier.service.ts`

- **`toggleAutoPublishForMainSuppliers`**: Aggregates `documentModel` (Sleek Receipts) for distinct `supplier` values where `company` matches `companyId`; errors if no suppliers or none classified as main.
- **`identifySupplierSpeciality`**: `POST` to `${VITE_APP_SUPPLIER_RULES_API}/suppliers/identify-supplier-speciality` with `supplier_names`; filters results where `speciality === SupplierSpeciality.MAIN`.
- **`updateAutoPublishSettingsForAllMain`**: `POST` to `${VITE_APP_SUPPLIER_RULES_API}/suppliers/update-auto-publish-settings-for-all-main` with `supplier_names`, `company_id`, `auto_publish` (service token `SUPPLIER_SERVICE_AUTH_TOKEN`).
- **Company alignment**: If API response `status !== 'error'`, `companyModel.findOneAndUpdate({ company_id }, { $set: { disabled_auto_publish: !auto_publish } })` so company flag mirrors enabled auto-publish (`disabled_auto_publish` is inverse of `auto_publish`).

### `src/supplier/dto/supplier.dto.ts`

- **`SupplierToggleAutopublishSettingsDto`**: `auto_publish: boolean`

### `src/company/models/company.schema.ts`

- **`disabled_auto_publish`**: boolean, default `false` — company-level flag updated in tandem with successful bulk main-supplier update.

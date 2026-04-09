# Review supplier activity and document footprint

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Review supplier activity and document footprint |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Teams can see how suppliers show up on receipt documents, how many companies and rules apply, and resolve counts when names differ from custom display labels—so usage and configuration stay visible and governable. |
| **Entry Point / Surface** | Sleek Admin (bookkeeping / receipts operations; supplier listing and related tooling backed by `acct-coding-engine` supplier APIs) |
| **Short Description** | Authenticated listing aggregates receipt documents by supplier with pagination, optional company filter, and sort by document count, company count, or supplier name. Each row merges document and company counts from MongoDB with specific-rule counts and supplier specialty from the supplier-rules service. Search by name matches the supplier field and expands to canonical names when the query matches a custom display name. A separate endpoint returns total document count for a supplier name using the same name and custom-display resolution. Successful list loads record user activity as `supplier_listing`. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Supplier rules HTTP API (`VITE_APP_SUPPLIER_RULES_API`): `GET /suppliers?custom_display_name=…`, `POST /suppliers/specific-rule-count-and-specialty`; user activity service for activity logging; receipt document data in MongoDB (`documentdetailevents`). |
| **Service / Repository** | `acct-coding-engine`; supplier-rules service (external API) |
| **DB - Collections** | `documentdetailevents` (MongoDB connection `SLEEK_RECEIPTS`) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `POST /supplier/document-count` has no `AuthGuard` while `GET /supplier` is authenticated—confirm whether omitting auth is intentional. `GetSupplierDto` exposes `custom_display_name` in Swagger but listing resolution uses `name` and the custom-display lookup service; clarify intended client contract. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`supplier/supplier.controller.ts`)

- **`GET /supplier`** — `AuthGuard`; query `GetSupplierDto` (`page`, `limit`, `name`, `custom_display_name`, `companyId`, `sortProperty`, `sortOrder`). Returns `SuppliersResponseDto` (`data`, `pagination`).
- **`POST /supplier/document-count`** — body `{ name }`; returns `{ documentCount }`. **No `AuthGuard`** on this route.

### Listing and aggregation (`supplier/supplier.service.ts` — `getSuppliers`)

- Filters documents where `supplier` exists, is non-empty, and has non-whitespace; optional `company` ObjectId from `companyId`.
- **Search / filter by name:** builds `$or` on case-insensitive regex on `supplier` and, when the supplier-rules lookup returns matches, `$in` on resolved canonical `name` values from **`getSupplierNamesByCustomDisplayNameFromSupplierRules`** (`GET …/suppliers?custom_display_name=…`).
- **Sort:** maps query `sortProperty` `doc_count` | `supplier_name` | `company_count` to aggregation fields `docCount`, `supplierName`, `companyCount`; default sort by `doc_count` descending.
- **Aggregation:** `$match` → `$group` by `supplier` with `$addToSet` of `company`, `$sum` for document count → `$addFields` for `companyCount` (`$size` of companies) → optional `$sort` → `$facet` for total count and paginated slice (`$skip` / `$limit`).
- **Enrichment:** **`getSpecificRulesCountAndSpecialtyBySupplierNames`** — `POST …/suppliers/specific-rule-count-and-specialty` with service token — merges `no_of_specific_rules`, `specialty`, with `docCount` and `companyCount` per supplier name.
- **Activity:** `UserActivityService.createOrUpdateUserActivity` with `last_activity: 'supplier_listing'` when `user._id` is present.

### Document total by name (`getDocumentCountBySupplierName`)

- Same custom-display resolution path as listing; **`countDocuments`** on the combined `$or` filter (regex on supplier + optional `$in` of names from supplier-rules).

### DTOs (`supplier/dto/supplier.dto.ts`)

- **`GetSupplierDto`** — pagination, `name`, `custom_display_name`, `companyId`, `sortProperty`, `sortOrder`.
- **`SuppliersResponseDto`** — `data` rows align with merged supplier info (counts + rules + specialty); **`PaginationDto`** — `totalData`, `totalPages`.

### Related code not in the expand file list

- **`GET /supplier/similar-suppliers`**, **`POST /supplier/toggle-auto-publish/:companyId`**, and other supplier-service helpers (rules CRUD, auto-publish) live in the same module but are separate user journeys from this listing-and-count footprint capability.

# Inspect user resource roles and company assignments

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Inspect user resource roles and company assignments |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User, Admin |
| **Business Outcome** | Internal staff can see how a user is allocated across client companies and resource roles (e.g. which bookkeeping or leadership roles apply per company) to support support, staffing, and access reviews. |
| **Entry Point / Surface** | Sleek Admin > Users > user context (resource allocation / company assignment views consuming admin user APIs) |
| **Short Description** | Authenticated admin APIs return `CompanyResourceUser` rows for a given user, joined to `ResourceAllocationRole`, `User`, and `Company`. Optional query `company_status` filters by company status; one route filters by `roleType` in the path; the list route supports pagination (`limit`, `offset`) and sorts by recent company activity. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Same data model as assigning resource roles to users per company (`CompanyResourceUser`, `ResourceAllocationRole`); upstream/downstream to company-level resource allocation and staff assignment flows in `company-controller` / company-resource-allocation handlers. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companyresourceusers`, `resourceallocationroles`, `users`, `companies` |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | No explicit `accessControlService.can` on these routes—only `userService.authMiddleware`; whether a stricter permission was intended is unclear. Exact Admin UI screen labels not named in this file. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### HTTP surface (`controllers/admin/user-controller.js`)

- **GET** `/admin/user/:userId/resource-allocation-role/` — `userService.authMiddleware` only (no `accessControlService` capability check in this file). Query: sanitized `company_status` (optional), `limit` (default 10), `offset` (default 0). Aggregation: `$match` user → `$lookup` `resourceallocationroles` → `$unwind` role → `$lookup` `users` → `$lookup` `companies` → `$unwind` → `$sort` by `company.updatedAt` descending → `$facet` for total count + paginated `data`. Returns `companyResourceUserResult[0]` with `metadata` / `data` shape.
- **GET** `/admin/user/:userId/resource-allocation-role/:roleType` — same auth. Path param `roleType` matched against `resource_role.type` after lookups. Optional `company_status` on `company.status`. Returns full aggregation array (no pagination facet).

### Schemas (imports)

- `schemas/company-resource-user.js` — `company`, `user`, `resource_role`, `appointed_date`, `cessation_date`, `is_removed`, `data`.
- `schemas/resource-allocation-role.js` — referenced as `resourceallocationroles` in `$lookup`.

### Notes

- Mongo aggregation collection names match Mongoose defaults: `resourceallocationroles`, `users`, `companies` as used in `$lookup` `from` fields.

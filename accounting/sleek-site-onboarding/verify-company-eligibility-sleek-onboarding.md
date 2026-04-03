# Verify company eligibility for Sleek site onboarding

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Verify company eligibility for Sleek site onboarding |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (website onboarding user) |
| **Business Outcome** | Prospects can confirm Singapore company names or UENs against ACRA data and Sleek’s company records, or Australian ABNs against existing Sleek companies, before continuing incorporation or accounting transfer—reducing duplicate sign-ups and invalid flows. |
| **Entry Point / Surface** | Sleek website onboarding — `GET /v2/sleek-site-onboarding/find-company` (Singapore name/UEN check); `GET /v2/sleek-site-onboarding/accounting-transfer/find-company` (Australia ABN check for accounting transfer). Unauthenticated HTTP surface (no auth middleware on these routes in `sleek-site-onboarding.js`). |
| **Short Description** | **SG**: Resolves `uen` or `name` against the ACRA mirror collection; optionally enforces a second pass against live Sleek `Company` records when ACRA does not match and feature flags allow. Returns whether the entity exists in ACRA, whether a UEN is already used on Sleek, and partner-company hints via `rawName`. **AU**: Returns whether an ABN already matches a Sleek company via `uen` or `business_registered_number`. |
| **Variants / Markets** | SG, AU |
| **Dependencies / Related Flows** | **App features**: `acra_company_name_checker` (customer) — `filter_in_company_collection_enabled`, `ignore_words`, `search_name_enable`; partner path uses `Company.partner`. **Utilities**: `formatWithEquivalentWords` (`sleek-site-onboarding-util`) for name normalization before Sleek DB lookup. Downstream: broader sleek-site-onboarding flows (cart, email, marketing company) live in the same router but are separate capabilities. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `acracompanies` (via `AcraCompany` model); `companies` (via `Company` model for Sleek usage checks and AU ABN match). |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Exact public website URL paths that call these APIs (only API base `/v2/sleek-site-onboarding/...` is evidenced in tests); whether HK or other tenants expose parallel routes beyond SG/AU branches in related flows. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sleek-site-onboarding.js`

- **`GET /find-company`** → `checkIfExistsHandler.execute` (`handlers/acra-company/find`).
- **`GET /accounting-transfer/find-company`** → `checkIfAuCompanyExistByAbnHandler.execute` (`handlers/au-companies/find`).
- No `userService` auth on these two routes (contrast with `/cart-details/` which uses `getUserInfoMiddleWare`).

### `controllers-v2/handlers/acra-company/find.js` (`execute`)

- Loads `acra_company_name_checker` app feature; strips one `ignoreWords` entry that has no letters (legacy quirk).
- Requires `uen` **or** `name` in `req.query`; else `400` with `uen or name is required`.
- Calls `store-queries/acra-company/find.execute(input)`; builds `isExisting` and `company` from result.
- If query has `uen`: `Company.findOne({ uen })` → `isUsedOnSleek` with `_id` and `name` or `false`.
- If `rawName` in query: `Company.findOne({ name: rawName })` → `isPartnerCompany` when `partner` is set.
- When lookup was by **name**, `filter_in_company_collection_enabled` is true, ACRA did not match, and not a partner company: calls `store-queries/company-name-checker/company.execute(name, feature)`; on failure returns `422` `"Invalid Request."`; on success replaces `response` with Sleek company match result.
- Errors: `500` with default error handler.

### `controllers-v2/handlers/au-companies/find.js` (`execute`)

- Reads `abn` from `req.query`; `Company.findOne` with `$or`: `uen` or `business_registered_number` equals `abn`.
- Returns `{ isExisting: boolean }` (200).

### `store-queries/acra-company/find.js`

- **`cleanCompany`**: uppercases, trims, recursively strips `ignore_words` regex segments, normalizes ` & ` → ` AND `.
- **`execute`**: If `input.uen` → query `{ uen: input.uen.toUpperCase() }`. If `input.name` → optional `search_text` `$in` when `search_name_enable`, else `name` regex anchored with `$` and case-insensitive. Uses `AcraCompany.findOne(query)`.

### `store-queries/company-name-checker/company.js`

- **`execute(name, feature)`**: `formatWithEquivalentWords` then `Company.findOne({ name: RegExp(cleanName,'i'), status: { $ne: 'draft' } })`.
- Returns structured `{ isExisting, company: { name, businessDescription } | null }` or `null` if `cleanName` is empty.

### `schemas/acra-company.js` / `schemas/company.js`

- Mongoose models `AcraCompany` and `Company` back the collections referenced above (default pluralized collection names `acracompanies` and `companies`).

### Tests

- `tests/controllers-v2/sleek-site-onboarding/find-company.js` exercises `/v2/sleek-site-onboarding/find-company` with UEN and name scenarios and stubs `acra_company_name_checker`.

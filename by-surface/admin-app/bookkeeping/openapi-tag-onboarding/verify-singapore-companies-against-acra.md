# Verify Singapore companies against ACRA

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Verify Singapore companies against ACRA |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Authenticated user (onboarding / incorporation) |
| **Business Outcome** | Lets users confirm a Singapore entity against the ACRA registry before or during onboarding, compare results to what they entered, see whether a UEN is already used on Sleek, and—when configured—fall back to validating names against existing non-draft Sleek companies. |
| **Entry Point / Surface** | API `GET /v2/acra-company/find` (`userService.authMiddleware`, OpenAPI tags `onboarding`, `v2`); query `uen` and/or `name` (name ignored if `uen` present); optional `rawName` used in handler for partner-company detection (not listed in published OpenAPI parameters). |
| **Short Description** | Looks up `AcraCompany` by UEN or normalized company name (feature flags control ignore-words stripping, regex name match vs `search_text` search). Returns `isExisting`, ACRA `company` payload, and when querying by UEN also `isUsedOnSleek` from `Company`. For name-only lookups, if filtering in the company collection is enabled and ACRA misses and the entity is not a partner match, delegates to the company-name-checker query against live Sleek companies (`status` not `draft`); may respond `422` with plain body `Invalid Request.` |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | App feature `acra_company_name_checker` (customer): `filter_in_company_collection_enabled`, `ignore_words`, `search_name_enable`; `appFeatureUtil.getAppFeaturesByName`; `formatWithEquivalentWords` (`utils/sleek-site-onboarding-util`) for name checker path; shared handler also referenced from `controllers-v2/sleek-site-onboarding.js`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `acracompanies` (read via `AcraCompany` model), `companies` (read via `Company` for UEN/name checks and partner flag) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `rawName` is read in the handler but not documented in `swagger.yml` / `public/api-docs/acra.yml`; 422 response for name-checker failure is plain text, while OpenAPI references JSON error schema. Whether ignore-word list mutation (removing entries without Latin letters) is intentional for all tenants. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Router:** `app-router.js` — `router.use("/v2/acra-company", require("./controllers-v2/acra-company"))`.
- **Route:** `controllers-v2/acra-company.js` — `GET /find` → `checkIfExistsHandler.execute` with `userService.authMiddleware`.
- **Handler:** `controllers-v2/handlers/acra-company/find.js` — `execute`: loads `acra_company_name_checker` feature; validates `uen` or `name`; calls `checkIfAcraCompanyExistsQuery.execute` (`store-queries/acra-company/find.js`); builds `isExisting` / `company`; if `uen`, `Company.findOne({ uen })` → `isUsedOnSleek`; if `rawName`, partner check via `Company.findOne({ name: rawName })`; conditional `checkIfCompanyExistsQuery.execute` (`store-queries/company-name-checker/company.js`) for name path when ACRA miss and not partner; errors `400` (missing params), `422` string body, `500` default.
- **ACRA query:** `store-queries/acra-company/find.js` — `cleanCompany` recursive strip of ignore words; `execute`: UEN uppercased match, or name via `search_text` `$in` vs regex on `name` depending on `search_name_enable`.
- **Name checker:** `store-queries/company-name-checker/company.js` — `Company.findOne({ name: RegExp(cleanName,'i'), status: { $ne: "draft" } })`, returns shaped `isExisting` / `company` or `null` if cleaned name empty.
- **Schema:** `schemas/acra-company.js` — Mongoose model `AcraCompany`: `uen`, `name`, `type`, `uen_issue_date`, `entity_status`, address fields, `search_text` array, `cleaned_name`, timestamps.
- **OpenAPI:** `swagger.yml` and `public/api-docs/acra.yml` — `GET /v2/acra-company/find`, `sleek_auth`, tags `onboarding`, `v2`.
- **Tests:** `tests/controllers-v2/acra-company/find.js` — examples `GET /v2/acra-company/find?uen=…`, `?name=…`.

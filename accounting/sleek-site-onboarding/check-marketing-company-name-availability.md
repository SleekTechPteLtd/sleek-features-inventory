# Check marketing company name availability

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Check marketing company name availability |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Prospect (website onboarding) |
| **Business Outcome** | Prospects see whether a proposed company name is still free for Sleek marketing use before they commit, using the same normalized keys stored on reserved marketing company records. |
| **Entry Point / Surface** | Sleek marketing website onboarding flows that collect a proposed company name; API `GET /v2/sleek-site-onboarding/marketing-company` with query `name`. |
| **Short Description** | The handler sanitizes the proposed name, loads the customer app feature `marketing_company_name_checker` (ignore words and optional HK/Far East normalisation), and runs `formatWithEquivalentWords` to produce a single search string. Spaces are removed and the backend looks up `MarketingCompany` by `search_text`. A match returns 404 (name not available); no match returns 200 with an availability message. Chinese-only input is rejected with 422 (language not supported). |
| **Variants / Markets** | Unknown — route is not tenant-gated in the controller; behaviour depends on shared DB and app feature configuration per deployment. |
| **Dependencies / Related Flows** | `app-features-util.getAppFeaturesByName("marketing_company_name_checker", "customer")`; `string-sanitizer` (`sanitize.keepSpace`); shared `formatWithEquivalentWords` / `cleanCompany` with ACRA-style name checking (`openapi-tag-onboarding` / `acra_company_name_checker` path); scripts such as `scripts/addCleanMarketingCompanyNames.js` for maintaining `search_text`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `marketingcompanies` (Mongoose model `marketingCompany` — fields include `company_name`, `search_text[]`, `cleaned_name`). |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | How `search_text` is populated and kept in sync with marketing campaigns (batch scripts vs live writes); whether the public API should remain unauthenticated long term; OpenAPI YAML coverage for `/marketing-company` vs other sleek-site-onboarding routes. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers-v2/sleek-site-onboarding.js`

- **`GET /marketing-company`** — Registered without auth middleware (same pattern as `check-existing-email`; contrast `POST /cart-details/` which uses `userService.getUserInfoMiddleWare`).
- **Handler** — `sleekSiteOnboarding.findMarketingCompany` from `controllers-v2/handlers/sleek-site-onboarding/sleek-site-onboarding.js`.

### `controllers-v2/handlers/sleek-site-onboarding/sleek-site-onboarding.js`

- **`findMarketingCompany`** — Reads `name` from `req.query`; `stringSantizerService.sanitize.keepSpace(name)`; empty after sanitise → **400** `Invalid Request.`
- **`appFeatureUtil.getAppFeaturesByName("marketing_company_name_checker", "customer")`** — Supplies `value.ignore_words` and optional `value.ignore_chinese_word` for downstream formatting.
- **`formatWithEquivalentWords(sanitizedCompanyName, feature)`** — From `utils/sleek-site-onboarding-util.js`. If falsy → **422** `ERROR_CODES.COMPANY_NAME_CHECKER.LANGUAGE_NOT_SUPPORTED` (e.g. Chinese characters in name cause early `null` in util).
- **Lookup** — Collapses whitespace from formatted name, builds `query = { "search_text": { $in: [cleanCompanyName] } }`, **`MarketingCompany.findOne(query)`**.
- **Responses** — Match → **404** `COMPANY_NAME_IS_NOT_AVAILABLE`; no match → **200** via `successResponseHandler` with uppercased name in message; errors → **500** generic support message.

### `utils/sleek-site-onboarding-util.js`

- **`formatWithEquivalentWords`** — If `/[\u4E00-\u9FCC]/` matches, returns `null` (Chinese not supported on this path). Otherwise **`cleanCompany`** recursively strips configured ignore words (case-insensitive), then normalises ` & ` → ` AND `; if `ignore_chinese_word` on the feature, normalises `(HK|Hong Kong)` and `(Far East|FE)` substrings for search consistency.
- **`cleanCompany`** — Recursive removal of ignore-list tokens from uppercase trimmed name.

### `schemas/marketing-company.js`

- **Model `marketingCompany`** — `company_name` (unique indexed string); `search_text` (array of strings, indexed); `cleaned_name` boolean default `false`; timestamps.

### `constants/error-codes.js`

- **`COMPANY_NAME_CHECKER`** — `LANGUAGE_NOT_SUPPORTED` (422), `COMPANY_NAME_IS_NOT_AVAILABLE` (404).

### Mounting

- Router mounted at `/v2/sleek-site-onboarding` in `app-router.js`; full path **`GET /v2/sleek-site-onboarding/marketing-company?name=...`** (see tests in `tests/controllers-v2/sleek-site-onboarding/get-marketing-company-name.js`).

### Columns marked Unknown

- **Variants / Markets**: No regional branch in the cited handler; tenant-specific behaviour not derived from these files alone.
- **Disposition**: No production analytics in scope for this write.

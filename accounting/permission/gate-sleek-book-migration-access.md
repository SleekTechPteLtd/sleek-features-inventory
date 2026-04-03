# Gate SleekBooks migration access

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Gate SleekBooks migration access |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Only authorized operations staff can use SleekBooks migration tooling, and each company is allowed to migrate only when it meets subscription, partner, Xero, and platform rules—reducing bad migrations and support risk. |
| **Entry Point / Surface** | `xero-sleekbooks-service` HTTP API under `permission` (Sleek Back–authenticated): `GET /permission/migration` (page/feature access), `GET /permission/:userId/:companyId` (per-company migration eligibility). Consumers are back-office / migration UIs calling these endpoints with `Authorization` and optional `app-origin`. |
| **Short Description** | After `SleekBackAuthGuard` validates the caller via Sleek Back `/users/me`, the service requires the user to be in the **Operation Admin** group (Sleek Back `is-member`). For a company, it allows migration if a migration record already exists in certain statuses; otherwise it enforces: no partner-linked company, no active annual Xero subscription package, at least one allowed accounting plan, no blocked e-commerce platforms (questionnaire), no PSG service subscriptions (from admin CMS config), company not already present in SleekBooks (UEN check), and company active on Xero (BigQuery-backed lookup by UEN). |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | **Upstream:** Sleek Back (`users/me`, `users/:id/is-member`, `companies/:id/accounting-questionnaire-answers`, `internal/companies/:id/subscriptions`, `v2/config/admin`). **Platform:** `PlatformService.company.findById`. **Downstream:** Mongo `Migration` presence short-circuits checks; `SleekbooksService.checkCompanyInSB`, `XeroService.getCompanyDataFromBQ`. **Adjacent:** Full migration flows in `migrate/*` that assume these gates were satisfied before work proceeds. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `Migration` (read: `findOne` by `companyId` and status in `completed`, `failed`, `inprogress`, `posted`). `XeroAuthToken` is injected on `PermissionService` but not referenced in `checkPermissionConditions` / `checkIsMember` / `getCompanySubscription`—no collection access from those paths. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | `checkIsMember` has **Accounting** / **Accounting Admin** group checks commented out; only **Operation Admin** grants access—is that permanent product policy? `XeroAuthToken` model is injected but unused in the permission service—dead code or planned use? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`src/common/permission/permission.controller.ts`**
  - `@Controller('permission')`, `@ApiTags('permission')`.
  - `GET /:userId/:companyId` — `getMigrationPermission`: `SleekBackAuthGuard`, `HttpServiceInterceptor`, `@ApiOperation({ summary: 'checks user migration permission' })`. Calls `checkIsMember(userId)` then `checkPermissionConditions(companyId)`; returns `false` with warn logs on failure, else `true`.
  - `GET /migration` — `getUserPermission`: same guard/interceptor, `@ApiOperation({ summary: 'checks user permission to access the page' })`. Uses `req.user._id` with `checkIsMember`; throws `UnauthorizedException` if not a member, else `true`.
- **`src/common/permission/permission.service.ts`**
  - `checkIsMember`: `GET ${SLEEK_BACK_API_BASE_URL}/users/${userId}/is-member?group_name=Operation Admin` (`SLEEK_GROUP_NAMES.OPERATION_ADMIN`); returns `true` only if `operationAdmin.data` is truthy. Prior Accounting / Accounting Admin HTTP checks are commented out.
  - `checkPermissionConditions`: `platformService.company.findById(companyId)`; if `migrationModel.findOne({ companyId, status: { $in: ['completed','failed','inprogress','posted'] } })` exists → `true`. If `company.partner != null` → `false`. Loads subscriptions via `getCompanySubscription` (internal API with service client basic auth), maps active services; denies if `xero_subscription_(1_year)` present; denies if no `ACCOUNTING_PLANS` match. Fetches accounting questionnaire; if any `e_commerce_platforms_v2[].type` is in `ECOMMERCE_PLATFORMS` (`Shopify`, `Wix`, `Amazon Marketplace`) → `false`. Loads admin config CMS feature `admin_constants` → `PSG_SERVICES` → denies if company subscribes to any listed PSG service. `sleekbooksService.checkCompanyInSB(company.uen)` → `false` if already in SB. `xeroService.getCompanyDataFromBQ(company.uen)` → `false` if not active on Xero. Else `true`. Errors in outer try → log and `false`.
  - `getCompanySubscription`: `GET .../internal/companies/${companyId}/subscriptions`, returns `data.companySubscriptions` or `[]`.
- **`src/common/constants/settings.ts`**: `ACCOUNTING_PLANS`, `SLEEK_GROUP_NAMES`, `ECOMMERCE_PLATFORMS`.
- **`src/common/guards/sleek-back.auth.guard.ts`**: Requires `Authorization` header; validates via `GET ${SLEEK_BACK_API_BASE_URL}/users/me`, attaches `request.user` on success.

**Usage confidence rationale:** Controller and service paths are explicit; external dependencies are named (env URLs, group name, plan allowlists).

**Criticality rationale:** This is the authorization and eligibility gate for production migration tooling; incorrect logic would either block valid migrations or allow risky ones.

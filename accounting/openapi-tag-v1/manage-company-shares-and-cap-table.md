# Manage company shares and cap table

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Manage company shares and cap table |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company owner (routes use `canManageCompanyMiddleware` with `owner`, `ownerIncompleteCompany` for admin-style bulk allocation); Sleek Admin bypasses permission checks where implemented |
| **Business Outcome** | Company owners maintain accurate share classes and shareholder positions so incorporation, onboarding, and corporate compliance workflows have correct cap table data. |
| **Entry Point / Surface** | Authenticated HTTP API: `share-controller` routes under `/companies/:companyId/...` for share items and shareholder allocations; new companies receive default share classes via `company-controller` company creation. Exact Sleek app navigation labels are not defined in this repo. |
| **Short Description** | Owners register and edit share classes (`share_items` on the company), bulk-update per-shareholder holdings (including optional `paid_up_amount` and `value_per_share` where features allow), and run client or admin allocation flows with validation, invitations, audit logs, Camunda incorporation triggers, and optional company metrics when onboarding completes. UK Ltd can use a variant route without sending invites. |
| **Variants / Markets** | **SG** (default incorporation and Camunda `AUTO_START_INCORP_WORKFLOW` paths); **UK** (commented path `update-shares-without-invite` for UK Ltd without email invites). Other markets not distinguished in code beyond `is_transfer` and partner toggles. |
| **Dependencies / Related Flows** | **App features**: `corpsec_squad` (share payment method on share items), `enhanced_share_allocation_settings`, `post_payment_onboarding` / onboarding Beta, `MAPS_CONSTANTS` (company metrics). **Services**: `invitationService.inviteCompanyUsers` (share allocation entrypoints), `startIncorporationWorkflow` (Camunda), `companyMetricService.createCompanyMetric` (onboarding share allocation completed), `auditorService.saveAuditLog` (update-shares paths), `accessControlService.isMember` (Sleek Admin extra fields on admin shares PUT). **Upstream data**: company creation seeds `share_items` in `company-controller`. |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (Mongoose `Company`): embedded `share_items`; fields such as `is_transfer`, `partner`, `app_onboarding_version` used in validation. `companyusers` (Mongoose `CompanyUser`): `shareholder.shares` arrays, `has_completed_shares_allocation`, invitation and role fields. `companymetrics` (or equivalent `CompanyMetric` collection) when `completedOnboardingShareAllocation` query triggers metric creation. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `controllers/share-controller.js`

- **`POST /companies/:companyId/share-items`** — Auth + `canManageCompanyMiddleware("owner")`. Builds share item from `type`, `name`, `currency`, optional `payment_method` when `corpsec_squad` enables it. `shareAllocationService.validateNegativeValues`; `companyService.addShareItemToCompany`.
- **`DELETE /companies/:companyId/share-items/:shareItemId`** — Removes subdocument from `company.share_items`, `company.save()`.
- **`PUT /companies/:companyId/share-items/:shareItemId`** — Validates body; duplicate check via `companyService.isShareItemDuplicate`; updates subdocument; may set `CompanyUser.has_completed_shares_allocation` when flag present in body.
- **`PUT /companies/:companyId/shares`** — `canManageCompanyMiddleware("ownerIncompleteCompany")`. Sleek Admin may persist `paid_up_amount`; otherwise field set excluded. Optional `value_per_share` when `enhanced_share_allocation_settings` enabled. Validates share_item ids against company, negative values, invites officers via `invitationService` with `SHARE_ALLOCATION_UPDATED`, `shareAllocationService.setTotalPercentageOfSharesPerShareholder`, updates each shareholder’s `CompanyUser.shareholder.shares`, then `startIncorporationWorkflow(..., SHARE_ALLOCATION_ADMIN_COMPLETED)`.
- **`PUT /companies/:companyId/update-shares`** — `canManageCompanyMiddleware("owner")`. Partner/global toggles for enhanced allocation; validates ordinary shareholders, amounts, decimals, share_item ids; conditional invites (`SHARE_ALLOCATION_COMPLETED`); `setTotalPercentageOfSharesPerShareholder`; replaces `shareholder.shares` per user with audit logs; optional `companyMetricService` + `startIncorporationWorkflow(SHARE_ALLOCATION_CLIENT_COMPLETED)` when `completedOnboardingShareAllocation` query set.
- **`PUT /companies/:companyId/update-shares-without-invite`** — Same validation and persistence as client update-shares without invitation side effects; comment notes UK Ltd.

### `controllers/company-controller.js`

- **`POST /companies`** and **`POST /v2/companies`** — New `Company` documents include default `share_items: [{ name: "Ordinary", type: "ordinary", payment_method: "CASH" }]` so cap table context exists before dedicated share-item APIs.
- **`PUT /companies/:companyId`** — General company update (not share-item CRUD); `canManageCompanyMiddleware("ownerIncompleteCompany")`; loads company context for onboarding flows that interact with shareholders elsewhere.

### `services/company-service.js`

- **`addShareItemToCompany`**, **`isShareItemDuplicate`** — Share class registration and duplicate detection on `type` / `name` / `currency`.
- **`canManageCompanyMiddleware`** — Resolves `owner` vs `companyUser` for draft companies, partner-origin bypass, Sleek Admin bypass, owner validation, locked company handling; used across share routes.

### `services/share-allocation-service.js`

- **`validateNegativeValues`** — Shared guard for negative `nb_of_shares`, `paid_up_amount`, `value_per_share`.
- **`setTotalPercentageOfSharesPerShareholder`** — When `corpsec_squad` admin feature enables `total_issued_shares_percentage_enabled`, annotates payloads with `shares_total_percentage_value_based` using `getTotalIssuedSharesCapital`.
- **`correctValuePerShare`** — Exported helper to derive `value_per_share` from amount and count (commented in some controller paths).

### `schemas/company.js`

- **`shareItemSchema`** and company `share_items` array — Structural source for share class definitions referenced by allocation payloads’ `share_item` ids.

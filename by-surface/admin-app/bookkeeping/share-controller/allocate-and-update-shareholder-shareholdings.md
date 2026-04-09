# Allocate and update shareholder shareholdings

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Allocate and update shareholder shareholdings |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Company owner (primary); Sleek Admin for extended allocation fields; System for conditional Camunda incorporation auto-start |
| **Business Outcome** | Maintain a validated cap table (share classes and per-holder amounts) so corporate onboarding, invitations, incorporation workflows, and compliance audit trails stay aligned. |
| **Entry Point / Surface** | Authenticated REST API on sleek-back: `POST/PUT/DELETE …/companies/:companyId/share-items`, `PUT …/companies/:companyId/shares`, `PUT …/companies/:companyId/update-shares`, `PUT …/companies/:companyId/update-shares-without-invite`. Exact in-app navigation path Unknown. |
| **Short Description** | Owners define share classes on the company and allocate or update each shareholder’s holdings per class, with validation (duplicates, negative values, share_item references, enhanced rules when feature flags allow). Flows can invite pending officers/shareholders, persist share-change audit rows to Sleek Auditor, compute issued-capital percentages when enabled, emit onboarding company metrics, and advance tenant-specific Camunda incorporation workflows. A UK Ltd–oriented route updates holdings without sending invitation emails when emails are absent. |
| **Variants / Markets** | SG, HK, UK, AU (tenant-specific invitation and incorporation routing; UK incorporation uses `gb` tenant mapping) |
| **Dependencies / Related Flows** | **Internal:** `share-allocation-service` (validation, percentage math), `company-service` (share item CRUD, `canManageCompanyMiddleware`, duplicate checks), `invitation-service` (`MULTIPLE_INVITATION_ENTRYPOINT.SHARE_ALLOCATION_*`), `incorporation-initiator` (`startIncorporationWorkflow` → SG/HK/UK Camunda handlers), `company-metric-service` (onboarding completion metric), `auditor` `saveAuditLog` → **External:** Sleek Auditor HTTP API. **Config:** app features (`corpsec_squad`, `enhanced_share_allocation_settings`, `post_payment_onboarding`, `incorp_transfer_workflow`, `MAPS_CONSTANTS`). |
| **Service / Repository** | sleek-back |
| **DB - Collections** | `companies` (embedded `share_items`); `companyusers` (`shareholder.shares`, `has_completed_shares_allocation`); `companymetrics` (onboarding share allocation completed, when query flag set) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`controllers/share-controller.js`**
  - `POST /companies/:companyId/share-items` — `userService.authMiddleware`, `canManageCompanyMiddleware("owner")`; optional `payment_method` from `corpsec_squad` feature; `shareAllocationService.validateNegativeValues`; `companyService.addShareItemToCompany`.
  - `DELETE` / `PUT …/share-items/:shareItemId` — owner guard; `PUT` uses `Validator` schema; duplicate share-item check via `companyService.isShareItemDuplicate`; optional `has_completed_shares_allocation` on `CompanyUser`.
  - `PUT /companies/:companyId/shares` — `canManageCompanyMiddleware("ownerIncompleteCompany")`; Sleek Admin may set `paid_up_amount`; optional `value_per_share` when `enhanced_share_allocation_settings` enabled; validates share_item IDs and negatives; `invitationService.inviteCompanyUsers(MULTIPLE_INVITATION_ENTRYPOINT.SHARE_ALLOCATION_UPDATED, …)` for officers/shareholders without invitation; `shareAllocationService.setTotalPercentageOfSharesPerShareholder`; persists per-`CompanyUser` `shareholder.shares`; `startIncorporationWorkflow(companyId, AUTO_START_INCORP_WORKFLOW.SHARE_ALLOCATION_ADMIN_COMPLETED)`.
  - `PUT …/update-shares` — owner guard; extended validation (ordinary shareholder minimum, decimals, enhanced rules); conditional `inviteCompanyUsers(SHARE_ALLOCATION_COMPLETED, …)` when `post_payment_onboarding` / Beta onboarding; `setTotalPercentageOfSharesPerShareholder`; `buildAuditLog` + `auditorService.saveAuditLog` (`update-company-shares`); on `completedOnboardingShareAllocation` query: `companyMetricService.createCompanyMetric` (`ONBOARDING.events.ONBOARDING_SHARE_ALLOCATION_COMPLETED`) and `startIncorporationWorkflow(…, SHARE_ALLOCATION_CLIENT_COMPLETED)`.
  - `PUT …/update-shares-without-invite` — same validation and audit/save path as `update-shares` but **no** invitation branch (comment: UK Ltd, empty email); no metric/workflow block in this handler.
- **`services/share-allocation-service.js`** — `validateNegativeValues` (`nb_of_shares`, `paid_up_amount`, `value_per_share`); `setTotalPercentageOfSharesPerShareholder` (gated by `corpsec_squad` admin `total_issued_shares_percentage_enabled`); `getTotalIssuedSharesCapital`; exported `correctValuePerShare` (not wired in current controller snippets).
- **`services/company-service.js`** — `isShareItemDuplicate`, `addShareItemToCompany` (push to `company.share_items`, save).
- **`services/invitations/invitation-service.js`** — `MULTIPLE_INVITATION_ENTRYPOINT.SHARE_ALLOCATION_COMPLETED` / `SHARE_ALLOCATION_UPDATED` validated entrypoints; `inviteCompanyUsers` orchestrates email/registration flows with `enhance_share_allocation` and role-based logic.
- **`services/camunda-workflow/sg-incorporation/incorporation-initiator.js`** — `startIncorporationWorkflow(companyId, entrypoint)`: gated by `incorp_transfer_workflow` auto-start and tenant workflow type (SG/HK/UK); `startIncorporationValidator` (share items currency skipped for `gb`; shareholder allocation checks differ by tenant); delegates to `sg-incorporation` / `hk-incorporation` / `uk-incorporation` handlers.
- **`services/company-metric-service.js`** — `createCompanyMetric` persists to `CompanyMetric` schema after company exists.
- **`controllers-v2/handlers/auditor/all.js`** — `saveAuditLog` → `PUT` `${sleekAuditorBaseUrl}/api/log` (skipped when `NODE_ENV` is `test`).

# Keep migration company data aligned with Sleek Back and Dext

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Keep migration company data aligned with Sleek Back and Dext |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | System, Operations User |
| **Business Outcome** | Migration records and step status stay consistent with the source-of-truth company roster in Sleek Back and with Dext receipt-account setup so operators see accurate migration progress and downstream automation can proceed. |
| **Entry Point / Surface** | **User-triggered (Sleek Back):** `GET /migration/sync/:companyId` to pull Sleek Back companies into migration records; `PUT /migration/uen/:id` also calls `syncCompaniesFromSleekBack` after a UEN-based update. **System / M2M:** `POST /migration/update/company` for programmatic company upserts from Sleek Back; `POST /migration/dext-setup/:id` for Dext setup callbacks (`M2MAuthGuard`). |
| **Short Description** | Fetches company data from Sleek Back’s migration API (`/v2/sb-migration/companies`), enriches each row with Xero tenant id from BigQuery, skips companies already present in SleekBooks when doing bulk sync, and upserts the `Migration` Mongo document with ownership, accounting contacts, currency, and related fields. Separately, Dext posts SUCCESS or FAILED for a company id; the service finds an in-progress migration on the `dextsetup` step and updates step and overall status plus structured logs. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | **Upstream:** Sleek Back HTTP API (`SLEEK_BACK_API_BASE_URL`), service-to-service basic auth (`SLEEK_SERVICE_CLIENT_ID` / `SECRET`). **Enrichment:** `XeroService.getCompanyDataFromBQ(companyRegNo)` for `companyTenantId`. **Guard:** `SleekbooksService.checkCompanyInSB` to avoid duplicating companies already in SleekBooks during sync. **Downstream:** `AppLoggerService` for Dext setup success/failure logs; migration pipeline steps (`dextsetup`) elsewhere in `MigrationService`. |
| **Service / Repository** | xero-sleekbooks-service |
| **DB - Collections** | `Migration` (read/write via `migrationModel`): `findOne`, `updateOne` with upsert, `findOne` for Dext callback matching `companyId`, `status: 'inprogress'`, `currentStep: 'dextsetup'`. |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | `setDextSetupStatus` sets FAILED/SUCCESS fields on the loaded Mongoose document and logs, but does not await a `save()` after those mutations (only a non-awaited `save()` runs immediately after load). Confirm whether Dext status updates persist as intended. Route param `id` on `POST /migration/dext-setup/:id` is passed to the service but lookup uses `data.company` only — clarify whether the path id is redundant. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **`migration/migration.controller.ts`**
  - `GET /migration/sync/:companyId` — `SleekBackAuthGuard`, `syncCompaniesFromSleekBack('all', 'all', id)`.
  - `PUT /migration/uen/:id` — after `updateByUen`, `syncCompaniesFromSleekBack('all', 'all', updatedMigration.companyId)`.
  - `POST /migration/update/company` — `M2MAuthGuard`, `updateCompaniesFromSleekBack(migration)`.
  - `POST /migration/dext-setup/:id` — `M2MAuthGuard`, `@ApiOperation` “hook to update dext setup status”, `setDextSetupStatus(id, migration)`.
- **`migration/migration.service.ts`**
  - `syncCompaniesFromSleekBack`: HTTP GET `${SLEEK_BACK_API_BASE_URL}/v2/sb-migration/companies?startDate=&endDate=&companyId=` with basic auth; for each company: `getCompanyDataFromBQ`, `checkCompanyInSB` short-circuit, `migrationModel.updateOne({ companyRegNo }, { $set: { companyId, companyName, region: process.env.PLATFORM, companyTenantId, defaultCurrency, country, ownerId, accountant, accountManager, renewalDate, accountingTool } }, { upsert: true })`.
  - `updateCompaniesFromSleekBack`: single-company upsert keyed by `companyRegNo` with same field set plus `companyId` from payload.
  - `setDextSetupStatus`: `findOne({ companyId: data.company, status: 'inprogress', currentStep: 'dextsetup' })`; on `data.status == 'FAILED'` sets `currentStepStatus` / `status` to failed and error log; on `SUCCESS` sets completed and success log.
- **`migration/dtos/dext-setup.dto.ts`**
  - `DextSetupDto`: `user`, `company`, `resource`, optional `payload`, `status`, optional `failure_reason` — validates callback body shape for Dext.

**Usage confidence rationale:** Sleek Back sync and M2M update paths are explicit and write to `Migration`. Dext callback persistence is less clear because document updates may not be saved after mutation.

**Criticality rationale:** Wrong or stale migration company data blocks or misroutes the Xero-to-SleekBooks migration; Dext step status drives receipt automation readiness.

# Configure Xero Integration

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Configure Xero Integration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | SuperAdmin |
| **Business Outcome** | Allows SuperAdmins to manage the active/inactive state of the Xero accounting connection per client type, ensuring invoices and contacts sync correctly to the right Xero organisation. |
| **Entry Point / Surface** | Internal Admin API → `PUT /xero/settings` (with `client-type` header: `main` or `manage_service`) |
| **Short Description** | SuperAdmins toggle the `isActive` flag on the Xero credential record for a given client type. When active, the default token persist key is used; when inactive, the service falls back to the backup token key. Credentials (clientId, clientSecret) stored encrypted in the DB override environment-level defaults when present. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Upstream: Xero OAuth token flow (token persisted via `XeroService.persistToken`). Downstream: all Xero API operations (`getItems`, `getTaxRates`, `getAccounts`, `createInvoice`, `createContact`, etc.) depend on the active setting to resolve the correct credentials. Related: `xero-webhook`, `xero-config-monitoring`. |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `xerosettings` (SleekXeroDB — `MONGODB_XERO_URI`) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. The `UpdateXeroSettingRequestDto` only exposes `isActive`; the `clientId` and `clientSecret` fields in `XeroSetting` schema are encrypted and stored, but there is no visible endpoint to set them — what mechanism populates those fields? 2. What triggers the need to switch between the default and backup token persist keys in practice (e.g., credential rotation, incident recovery)? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Route
- `PUT /xero/settings` — `XeroController.updateXeroSetting` (`xero/xero.controller.ts:53–63`)
- Guard: `@GroupAuth(Group.SuperAdmin)` — restricted to SuperAdmins only
- Header: `client-type` (`ClientType.main` | `ClientType.manageService`) selects which Xero organisation's setting is updated

### DTO
- `UpdateXeroSettingRequestDto` (`xero/dtos/update-xero-setting.request.dto.ts`) — single field: `isActive: boolean`

### Service logic
- `XeroService.updateXeroSetting(data)` (`xero/services/xero.service.ts:281–284`)
  - Calls `xeroSettingRepository.updateById(this.defaultTokenPersistKey, data)`
  - `defaultTokenPersistKey` = `XERO-TOKEN-SET-{clientType}` (e.g. `XERO-TOKEN-SET-main`)

### Token key resolution (in `XeroService.init`)
- Reads `defaultXeroSetting` by `defaultTokenPersistKey`
- If `defaultXeroSetting.isActive` is `true` → uses `defaultTokenPersistKey`
- If `false` → falls back to `backupTokenPersistKey` (`XERO-TOKEN-SET-{clientType}-BACKUP`)
- Decrypts `clientId` / `clientSecret` from DB if present; otherwise uses env vars (`XERO_CLIENT_ID_MAIN`, `XERO_CLIENT_SECRET_MAIN`, etc.)

### Schema — `XeroSetting` (`xero/models/xero-setting.schema.ts`)
- `_id`: string (token persist key, e.g. `XERO-TOKEN-SET-main`)
- `value`: string (encrypted OAuth token set)
- `clientId?`: string (optional encrypted Xero app client ID)
- `clientSecret?`: string (optional encrypted Xero app client secret)
- `isActive`: boolean (defaults to `true`)
- Timestamps: `createdAt`, `updatedAt`
- Database connection: `SleekXeroDB` → `MONGODB_XERO_URI`

### Repository
- `XeroSettingRepository` extends `BaseRepository<XeroSetting>` (`xero/repositories/xero-setting.repository.ts`)
- Registered under `SleekXeroDB` named connection

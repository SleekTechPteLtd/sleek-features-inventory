# Toggle Automated Signature per Employee

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Toggle Automated Signature per Employee |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Enable or disable automated signing for individual employees to control which staff can sign on behalf of clients |
| **Entry Point / Surface** | Admin App > Auto-Sign Configuration > Automated Signature toggle (per employee row) |
| **Short Description** | Per-employee on/off toggle to enable or disable automated signature. When enabled, the employee's signature can be automatically applied to qualifying documents without manual intervention. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | UK and AU unverified — sessions expired before audit. Confirm what triggers automated signature application (document type, workflow step, request template, etc.). |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/auto-sign-configuration/index.js` — auto-sign employee table, add employees, toggles, column filters. Webpack: `admin/auto-sign-configuration`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.

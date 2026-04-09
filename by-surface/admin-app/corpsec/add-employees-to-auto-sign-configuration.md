# Add Employees to Auto-sign Configuration

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Add Employees to Auto-sign Configuration |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Onboard new Sleek employees into the auto-sign system so their signatures can be applied automatically to qualifying documents |
| **Entry Point / Surface** | Admin App > Auto-Sign Configuration > ADD EMPLOYEES button |
| **Short Description** | Adds new Sleek employees to the auto-sign configuration list, making them eligible for automated signature assignment on company documents. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | UK and AU unverified — sessions expired before audit. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/auto-sign-configuration/index.js` — auto-sign employee table, add employees, toggles, column filters. Webpack: `admin/auto-sign-configuration`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.

# Filter Auto-sign Employee List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Filter Auto-sign Employee List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Quickly find specific employees in the auto-sign configuration without scrolling through the full list |
| **Entry Point / Surface** | Admin App > Auto-Sign Configuration > column filter icons (Name, Role, Automated Signature) |
| **Short Description** | Filter the auto-sign employee list by Name of Employees, Role, or Automated Signature status using the per-column filter icons. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Low |
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

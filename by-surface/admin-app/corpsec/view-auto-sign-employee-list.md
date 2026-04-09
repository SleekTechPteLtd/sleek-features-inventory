# View Auto-sign Employee List

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | View Auto-sign Employee List |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Corpsec Officer / Admin User |
| **Business Outcome** | Review which employees are configured and enabled for automated document signing |
| **Entry Point / Surface** | Admin App > Auto-Sign Configuration |
| **Short Description** | Displays a table of all employees configured for auto-sign with columns: Name/Email, Role (Corp Sec / Corp Sec Admin / Nominee Director), and Automated Signature toggle status. SG shows ~35 employees; HK shows ~14 employees. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | — |
| **Service / Repository** | sleek-back, sleek-website |
| **DB - Collections** | sleek |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Must Keep |
| **Open Questions** | UK and AU unverified — sessions expired before audit; confirm whether Auto-sign Configuration exists in UK and AU. |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### sleek-website

- `src/views/admin/auto-sign-configuration/index.js` — auto-sign employee table, add employees, toggles, column filters. Webpack: `admin/auto-sign-configuration`.

### Live app walkthrough

- Confirms admin behaviour described in the master sheet for this capability.

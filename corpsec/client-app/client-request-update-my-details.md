# Client Request – Update My Details

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Request – Update My Details |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Shareholder / Director (self-serve) |
| **Business Outcome** | Allows individual users to keep their personal information current with ACRA requirements without going through a formal request flow. |
| **Entry Point / Surface** | Client App > Requests > Request > Update My Details > Update my profile |
| **Short Description** | User updates their own personal information including identity information and residential address. Supporting documents may be required. Each director/shareholder must update their own profile individually. Free and self-serve (no Sleek processing step). References ACRA documentation and penalty requirements. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | ACRA filing (if required); user profile management |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Does this trigger an ACRA filing automatically or is it a manual step? |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- **Requests hub:** `CustomerRequestContent.vue` — `UPDATE_MY_DETAILS` type (self-serve profile update messaging; links/actions to profile flow).
- **Profile:** `GET /customer/profile` — `src/routes/routes.js` (`user-profile`, `Profile` container) for personal particulars.

### customer-common

- `MasterLayout`.

### customer-root

- `src/root-config.js`.

### Live app walkthrough

- Confirms per-user profile update and ACRA reference copy.

# Recipients list

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Recipients list |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Browse and manage saved payout recipients for transfers. |
| **Entry Point / Surface** | **`/sba/business-account/recipients`** — **`name: "recipients"`**, component **`SBARecipients`**. |
| **Short Description** | Directory of recipients with navigation to create/update flows. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | NIUM payout / DBS recipient APIs via orchestrator |
| **Service / Repository** | customer-sba; sba-bank-api; sba-nium-payout |
| **DB - Collections** | N/A |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- `customer-sba/src/routes/routes.js` — `path: "business-account/recipients"`.

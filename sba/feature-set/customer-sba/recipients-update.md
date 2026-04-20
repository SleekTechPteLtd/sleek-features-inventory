# Update recipient

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | Update recipient |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Edits an existing recipient’s details while preserving transfer history linkage. |
| **Entry Point / Surface** | **`/sba/business-account/recipients/update`** — **`name: "Update Recipient"`**, component **`SBARecipientUpdate`** (`props: true`). |
| **Short Description** | Update flow receives route params via `props: true`. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Recipients list |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/recipients/update"`, `props: true`.

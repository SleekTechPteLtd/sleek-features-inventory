# New recipient

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | SBA |
| **Feature Name** | New recipient |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Customer |
| **Business Outcome** | Adds a new transfer recipient with validation and compliance fields. |
| **Entry Point / Surface** | **`/sba/business-account/recipients/new`** — **`name: "New Recipient"`**, component **`SBARecipientNew`**. |
| **Short Description** | Creation form for recipients; feeds into transfer and payout flows. |
| **Variants / Markets** | |
| **Dependencies / Related Flows** | Recipients list; orchestrator recipient APIs |
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

- `customer-sba/src/routes/routes.js` — `path: "business-account/recipients/new"`.

# Find similar supplier matches

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Find similar supplier matches |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Operators can see fuzzy-ranked candidate supplier records so they can pick the right canonical supplier or consolidate duplicates during accounting setup. |
| **Entry Point / Surface** | Authenticated client → Coding Engine `GET /supplier/similar-suppliers?name=…` (exact UI navigation not evidenced in repo) |
| **Short Description** | Given a supplier name string, the service loads candidates from the Supplier Rules service, re-ranks them with Fuse.js fuzzy matching on `name` and `custom_display_name`, and returns up to three options each with a similarity score. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Supplier Rules API (`GET /suppliers?search=…&exclude_children_of_any_parent=1`); downstream supplier rules / document flows that use `similar_supplier_info` on documents or feedback (separate code paths). |
| **Service / Repository** | acct-coding-engine |
| **DB - Collections** | None for this endpoint (no MongoDB access in `findSimilarSupplier`). Types `SimilarSupplierOption` / `SimilarSupplierInfo` are defined for API and for `similar_supplier_info` embedded data on documents and feedback elsewhere. |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which product screen calls this route; whether markets differ; relationship to automated `getSimilarSupplierInfo` in feedback vs this manual lookup. |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

- **Route:** `SupplierController.getSimilarSuppliers` — `GET supplier/similar-suppliers`, query param `name`, `AuthGuard`, returns `SimilarSupplierOption[]`. Default limit of 3 via `findSimilarSupplier(name, 3)`.
- **Service:** `SupplierService.findSimilarSupplier` — HTTP GET to `${VITE_APP_SUPPLIER_RULES_API}/suppliers?search=${encodeURIComponent(original_supplier_name)}&exclude_children_of_any_parent=1` with `SUPPLIER_SERVICE_AUTH_TOKEN`; builds `Fuse` over `response.data.data` with keys `name`, `custom_display_name`; `includeScore`, `shouldSort`, `threshold: 0.1`, `minMatchCharLength: 4`; maps results to `SimilarSupplierOption` with `score = (1 - fuseScore) * 100`. Returns empty array if name missing or on error.
- **Schema:** `similar-supplier-info.schema.ts` — `SimilarSupplierOption` (`name`, optional `custom_display_name`, `score`); `SimilarSupplierInfo` (e.g. `original_supplier_name`, `similar_suppliers`, auto-modify fields) for embedded document/feedback shapes — not written by this endpoint.

**Files:** `acct-coding-engine/src/supplier/supplier.controller.ts`, `acct-coding-engine/src/supplier/supplier.service.ts`, `acct-coding-engine/src/document/models/similar-supplier-info.schema.ts`.

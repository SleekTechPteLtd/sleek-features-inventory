# Review Outbound Transaction Compliance

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Review Outbound Transaction Compliance |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Compliance Admin (internal ops user) |
| **Business Outcome** | Enables compliance admins to assess client-submitted proof for debit transactions, accept or reject it, whitelist recurring payment patterns to reduce future review load, request additional details, or escalate to an account-level compliance review — keeping outbound payment flows compliant without blocking legitimate transactions. |
| **Entry Point / Surface** | Sleek Admin App > Transactions > [Transaction Detail] > Outbound Review tab |
| **Short Description** | Compliance admins review client-uploaded proof for flagged outbound (debit) transactions and choose one of six outcomes: accept proof, accept and whitelist similar future transactions, request more proof, invalidate proof, escalate to account compliance review, or close a prior account review. All decisions are logged in a timestamped review history and may include admin-uploaded supporting files. |
| **Variants / Markets** | SG, HK |
| **Dependencies / Related Flows** | Client-side proof submission flow (upstream); SBA account status (escalation updates SBA status to "under compliance review"); file storage service (supporting document upload/download); outbound whitelist engine (auto-approves future matching transactions); Transaction URL Manager (cross-link to whitelist source transaction) |
| **Service / Repository** | sleek-website (admin frontend); SBA backend (`/sba/v2/admin/transactions` API) |
| **DB - Collections** | Unknown — collections are owned by the SBA backend; fields observed on transaction object: `compliance_status`, `compliance_review_history`, `supporting_documents`, `outbound_whitelist`, `no_proof_available`, `purpose_of_payment`, `recurrence_type`, `amount_consistency`, `additional_details`, `submitted_at`, `submitted_by` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which backend service owns the compliance-status PATCH endpoint and its DB collections? Does the whitelist engine live in the SBA backend or a separate service? Are there email/notification triggers fired after each status change? Is the escalation path (account_under_compliance_review) tied to a formal SBA compliance workflow outside this UI? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry point
- `views/admin/transactions/components/outbound-review-tab.js` — `OutboundReviewTab` React component renders the full review UI: compliance status chip, action form (comments + status dropdown + file upload), supporting documents viewer, whitelist info card, and timestamped review history timeline.

### Actions available (via status dropdown)
| Status value | Label | Effect |
|---|---|---|
| `proof_accepted` | PROOF ACCEPTED | Marks client proof as sufficient |
| `proof_accepted_whitelisted` | PROOF ACCEPTED & WHITELISTED | Accepts proof + whitelists similar transactions (same recipient, amount ±5%, same purpose) for automatic future approval |
| `proof_required` | PROOF REQUIRED | Flags that more proof is needed from the client |
| `proof_invalid` | PROOF INVALID | Marks provided documents as unacceptable |
| `account_under_compliance_review` | ACCOUNT UNDER COMPLIANCE REVIEW | Escalates — updates SBA account status to "under compliance review" |
| `account_review_closed` | ACCOUNT REVIEW CLOSED | Closes a prior account-level compliance review |

Actions are only shown when `compliance_status` is one of: `pending_review`, `proof_required`, `proof_invalid`, `account_under_compliance_review`, `pending_compliance_account_review`.

### API call chain
```
OutboundReviewTab
  → useTransactionActions() → onUpdateOutboundReview(transactionId, payload)
    → contexts/transaction-actions-context.js :: updateOutboundReview()
      → business-account-utils.js :: updateOutboundReviewRequest(_id, data)
        → api-bank.js :: updateOutboundReviewRequest(_id, data)
          PATCH /sba/v2/admin/transactions/{_id}/compliance-status
          body: { compliance_status, comments, uploaded_files? }
```

### File upload flow
- Admin can attach supporting files alongside the review decision.
- Files are uploaded to the company's SBA folder structure (via `createAttachmentFolder` + `uploadFile`).
- Uploaded file IDs are included in the PATCH payload as `uploaded_files`.
- Both client-uploaded and admin-uploaded documents are distinguished by `upload_source` field (`"client"` / `"admin"`).

### Review history
- `compliance_review_history` array on the transaction object stores each decision: `status`, `reviewer_name`, `reviewer_email`, `reviewed_at`, `comments`, `uploaded_files`.
- Rendered as a chronological timeline in the UI.

### Whitelist display
- If a transaction was auto-approved via a whitelist, `outbound_whitelist.source_transaction.transaction_id` points to the originating transaction that created the whitelist entry; clicking it opens that transaction in a new tab via `TransactionUrlManager`.

### Compliance status constants (`src/utils/constants.js` lines 2123–2146)
```
not_required, pending_review, proof_required, proof_invalid,
proof_accepted, proof_accepted_whitelisted,
pending_compliance_account_review, account_under_compliance_review,
account_review_closed, auto_proof_acceptance_whitelisted
```

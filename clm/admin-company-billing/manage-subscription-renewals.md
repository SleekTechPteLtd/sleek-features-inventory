# Manage Subscription Renewals

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Subscription Renewals |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (Billing Super Admin) |
| **Business Outcome** | Gives Billing Super Admins full control over a subscription's renewal lifecycle — adjusting renewal dates and amounts, toggling auto-renewal, cancelling upcoming renewals, and offboarding or reactivating subscriptions — so that billing accurately reflects commercial agreements and client status. |
| **Entry Point / Surface** | Sleek Admin > Company Billing > Subscription Detail |
| **Short Description** | Admins can update the next renewal date and custom renewal amount, enable or disable auto-renewal, cancel an upcoming renewal, offboard a client from a service, reactivate or discontinue a subscription, and update the financial year end — all with mandatory reasons for audit. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Sleek Billings API (external billing service); Audit Logs (getAuditLogsByCompanyIdAndTags); Company Billing view; Subscription Detail view; Auto-renewal charge scheduling (AUTO_RENEWAL_CHARGE config) |
| **Service / Repository** | sleek-website (frontend); Sleek Billings API (backend, separate service) |
| **DB - Collections** | Unknown (managed by Sleek Billings API backend; not accessible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | Which markets/jurisdictions use this flow? Are there market-specific restrictions on renewal actions? What does the Sleek Billings API backend persist — which collections are touched? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Entry file
- `src/views/admin/company-billing/subscription-detail.js` — React component `SubscriptionDetail`

### Permission guard
- Edit actions gated on `BILLING_SUPER_ADMIN` group membership via `isMember` (`src/utils/api.js`)
- State: `hasEditPermission` (line 117) populated via `isMember({ group_name: SLEEK_GROUP_NAMES.BILLING_SUPER_ADMIN })`

### API calls (`src/utils/sleek-billings-api.js` → `SLEEK_BILLINGS_API`)
| Handler | Endpoint | Method |
|---|---|---|
| `updateCustomRenewalAmount` | `PUT /customer-subscriptions/:id/custom-renewal-amount` | Custom price override |
| `updateNextRenewalDate` | `PUT /customer-subscriptions/:id/next-renewal-date` | Reschedule renewal (also used for reactivation) |
| `cancelRenewal` | `PUT /customer-subscriptions/:id/cancel-renewal` | Cancel upcoming renewal |
| `toggleAutoRenewal` | `PUT /customer-subscriptions/:id/toggle-renewal` | Enable/disable auto-charge |
| `offboardSubscription` | `PUT /customer-subscriptions/:id/offboard` | Set delivery status to `toOffboard` |
| `reactivateSubscription` | `PUT /customer-subscriptions/:id/reactivate` | Set delivery status back to `active` |
| `discontinueSubscription` | `PUT /customer-subscriptions/:id/discontinue` | Set delivery status to `discontinued` |
| `updateFinancialYearEnd` | `PUT /customer-subscriptions/:id/financial-year-end` | Update FYE for accounting subscriptions |
| `updateCustomerSubscription` | `PUT /customer-subscriptions/:id/patch-data` | General patch for subscription fields |
| `getAuditLogsByCompanyIdAndTags` | `GET /audit-logs` (by companyId + `subscription-<id>` tag) | Audit log viewer |

### Subscription status values (`src/views/admin/company-billing/constants.js`)
- Delivery statuses: `active`, `delivered`, `discontinued`, `toOffboard`, `ddInProgress`, `deactivated`
- Renewal statuses: `none`, `notDue`, `due`, `renewed`, `cancelled`

### Audit trail
- Every mutation requires a mandatory reason field (enforced client-side)
- Reasons stored on subscription: `customRenewalAmountUpdateReason`, `nextRenewalDateUpdateReason`, `subscriptionCancellationReason`, `autoRenewalReason`, `serviceDeliveryOffboardingReason`, `serviceDeliveryReactivationReason`

### Related constants/utils
- `src/views/admin/company-billing/constants.js` — status mappings, `AUTO_RENEWAL_CHARGE` timing config (first attempt 27 days before, second 20 days before renewal date)
- `src/views/admin/company-billing/utils.js` — `getPurposeOfPurchaseOptions`
- `src/views/admin/company-billing/AuditLogDrawer` — audit log UI
- `src/views/admin/company-billing/components/deliverables.sds.component` — deliverables overview (co-located)

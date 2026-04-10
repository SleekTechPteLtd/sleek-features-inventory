# Assign Priority Labels to Subscriptions

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Assign Priority Labels to Subscriptions |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User (Delivery team operators / bookkeepers) |
| **Business Outcome** | Operators can flag subscriptions with urgency labels so that work queues can be sorted and triaged by priority, reducing risk of missing time-sensitive client obligations. |
| **Entry Point / Surface** | Sleek Admin > Delivery Overview — Labels column in the subscriptions list table (inline via dropdown) and Labels section in the right-hand subscription detail panel |
| **Short Description** | Operators tag one or more priority labels onto a subscription directly from the Delivery Overview list or the detail side-panel. Labels are persisted via a PATCH to the service-delivery-api and reflected immediately in both the list row and the detail view. The list can also be filtered by label. |
| **Variants / Markets** | SG, HK, AU |
| **Dependencies / Related Flows** | Delivery Overview subscription list (filter by label); Tasks Dashboard (also reads `SUBSCRIPTION_PRIORITY_LABEL_OPTIONS` for label filter); service-delivery-api `/subscriptions/:id` PATCH endpoint |
| **Service / Repository** | sleek-billings-frontend, service-delivery-api (backend, external) |
| **DB - Collections** | Unknown — persisted server-side via service-delivery-api; collection name not visible from frontend code |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | 1. UK market is absent from `SUBSCRIPTION_PRIORITY_LABEL_OPTIONS` — is priority labelling unsupported there or simply not yet configured? 2. Who in the backend controls the canonical list of allowed labels — is it hard-coded in service-delivery-api or configurable per platform? 3. Is there any audit trail / history for label changes? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Delivery/DeliveryOverview.jsx` — Main page; renders the subscriptions table and right-hand detail panel.
- `src/services/service-delivery-api.js` — `sleekServiceDeliveryApi.updateSubscription(id, { priorityLabels })` → `PATCH /subscriptions/:id`; `getAllSubscriptions({ priorityLabels })` → `GET /subscriptions?priorityLabels=<comma-separated>`.
- `src/components/SubscriptionPriorityLabel.jsx` — Pill badge component; renders a yellow badge (`#FFE8A8`) for most labels and a grey badge (`#EBEBEB`) specifically for the `Unresponsive Client` label.
- `src/lib/constants.jsx` — `SUBSCRIPTION_PRIORITY_LABELS` enum and `SUBSCRIPTION_PRIORITY_LABEL_OPTIONS` per-platform arrays.

### Key logic (`DeliveryOverview.jsx`)
- `priorityLabelOptions` (line 66): reads `billingConfig.platform` from `localStorage` and maps it to the market-specific label list.
- `handleUpdatePriorityLabels(label)` (line 340): toggles a label in/out of `subscription.priorityLabels[]`, re-sorts by the platform's canonical order, calls `sleekServiceDeliveryApi.updateSubscription`, then updates both the list row state and the `selectedSubscription` detail state from the API response.
- Table column `priorityLabels` (line 444): renders each label as a `<SubscriptionPriorityLabel>` pill with a "+" icon to open the label picker dropdown.
- Detail panel (line 1049): shows all current labels and opens the same dropdown for editing.
- Filter parameter (line 153): `queryParams.priorityLabels = currentFilters.filterByLabels.join(",")` passed to `getAllSubscriptions`.

### Label taxonomy per market
| Market | Labels |
|---|---|
| SG | AGM Due Soon, Client Escalation, High Transaction Volume, Sleek ND, Unresponsive Client |
| HK | PTR Received, Court Summons Received, Penalties Received, Client Escalation, High Transaction Volume, Unresponsive Client |
| AU | ATO Due Soon, BAS Due Soon, Compliance Action Required, Client Escalation, Critical Business Event, Backlog Work, Complex Transactions, High Transaction Volume, Unresponsive Client |
| UK | Not configured (absent from `SUBSCRIPTION_PRIORITY_LABEL_OPTIONS`) |

### API surface
- `PATCH /subscriptions/:id` — payload `{ priorityLabels: string[] }` — response `{ data: { id, priorityLabels, … } }`
- `GET /subscriptions?priorityLabels=<csv>` — filter subscriptions list by one or more labels

# Client Portal – On-going Requests View

## Master sheet (draft)

| Column | Value |
|--------|-------|
| **Domain** | Corpsec |
| **Feature Name** | Client Portal – On-going Requests View |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Client / Company Director |
| **Business Outcome** | Keeps clients informed of active request progress, reducing inbound support queries about request status. |
| **Entry Point / Surface** | Client App > Requests > On-going (left nav) |
| **Short Description** | Lists active/in-progress Corpsec requests submitted by the client. Each card shows request type, Request ID, Date of Request, and Price. Currently shows latest request only. |
| **Variants / Markets** | SG |
| **Dependencies / Related Flows** | Requests catalogue; admin-side request processing; Camunda workflows |
| **Service / Repository** | customer-main, customer-common, customer-root (client shell and shared UI) |
| **DB - Collections** | — |
| **Evidence Source** | Live app walkthrough |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** |  |
| **Reviewer** |  |
| **Review Status** | Draft |

## Evidence

### customer-main

- Route `GET /customer/on-going-request` — `src/routes/routes.js` (`name: on-going-request`).
- `src/modules/customer-requests/containers/OnGoingRequest.vue` → `components/OnGoingRequestContent.vue` — active request cards/list.
- `src/proxies/back-end/customer-requests/get.js` — `GetCustomerRequestsListsProxy` (`TARGET_URL` `/customer-requests`).

### customer-common

- `MasterLayout` from `@sleek/customer-common` wraps the page; drawer exposes **Requests** → On-going when configured.

### customer-root

- `src/root-config.js` — `@sleek/customer-main` on `/customer`.

### Live app walkthrough

- Confirms latest / in-progress corpsec request presentation per audit notes.

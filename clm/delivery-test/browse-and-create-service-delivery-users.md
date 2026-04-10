# Browse and Create Service Delivery Users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Browse and Create Service Delivery Users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User / Developer |
| **Business Outcome** | Allows operators to inspect and populate the service delivery user roster for testing and QA workflows, ensuring the system has the correct user data before running delivery scenarios. |
| **Entry Point / Surface** | Sleek Billings Admin > Developer Tools > Users tab |
| **Short Description** | Displays a paginated table of all users registered in the service delivery system (name, email, master-user flag, status, created date) and provides a dialog form to create new user records with first name, last name, email, and status. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Service Delivery API (`VITE_SERVICE_DELIVERY_API_URL`); Sync Users trigger (MongoDB → PostgreSQL sync in the same Developer Tools page); Seed/Truncate database flows (TriggersList on same page) |
| **Service / Repository** | sleek-billings-frontend, sleek-service-delivery-api (backend, inferred) |
| **DB - Collections** | Unknown (backend is PostgreSQL via service delivery API; collection name not visible from frontend) |
| **Evidence Source** | codebase |
| **Criticality** | Low |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | Is this page access-controlled (role guard)? The page is labelled "Developer Tools" — is it hidden in production? What PostgreSQL table backs the `/users` endpoint? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/pages/Delivery/TestDelivery.jsx` — `UsersList` component (lines 297–421); `TestDelivery` root component (lines 424–461)
- `src/services/service-delivery-api.js` — `sleekServiceDeliveryApi.getAllUsers` (line 373), `sleekServiceDeliveryApi.createUser` (line 392), `sleekServiceDeliveryApi.getUserById` (line 383), `sleekServiceDeliveryApi.getUserByExternalRefId` (line 587)

### API calls
| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/users?page=N&limit=2000` | Fetch paginated user list; response shape `{ data: [...], meta: { totalPages } }` |
| `POST` | `/users` | Create a new user; payload: `{ firstName, lastName, middleName?, email, status, createdBy }` |

### UI fields (create dialog)
`firstName` (required), `middleName` (optional), `lastName` (required), `email` (required), `status` (default `ACTIVE`), `createdBy` (hardcoded `admin`)

### User record columns displayed
`id`, `firstName`, `middleName`, `lastName`, `email`, `isMasterUser`, `status`, `createdAt`

### Auth
`Authorization` header sourced from `localStorage.getItem("auth")`; Bearer JWT if token has 3 segments, raw token otherwise. `App-Origin: admin` or `admin-sso` based on `alternate_login` flag.

### Context from sibling components
The same `TestDelivery` page also hosts a `TriggersList` tab that can seed/truncate the database and trigger a one-time sync of users from MongoDB to PostgreSQL — confirming the users list is the PostgreSQL mirror of a MongoDB source of truth.

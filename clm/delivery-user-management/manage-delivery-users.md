# Manage Delivery Users

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage Delivery Users |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Admin (sleek-back admin profile) |
| **Business Outcome** | Admins provision and control user accounts in the service delivery platform so that only authorised personnel have access at the correct lifecycle status, and identity records remain current for task and deliverable assignment. |
| **Entry Point / Surface** | Sleek Billings Frontend > Delivery > User Management |
| **Short Description** | Provides a paginated, searchable list of delivery-service users with inline create, edit (name + status), and delete actions. Status lifecycle covers ACTIVE, INACTIVE, and SUSPENDED states; email is immutable once set. Users carry an `external_ref_id` linking them to an external identity system. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Delivery deliverables (user is `assignedUser`); delivery tasks (user is `assignedUser`); team assignments; auto-assignments; offboarding requests (user as in-charge officer and activity actor); external identity system (via `external_ref_id` lookup) |
| **Service / Repository** | sleek-service-delivery-api; sleek-billings-frontend |
| **DB - Collections** | `users` table (PostgreSQL via TypeORM); relations to `deliverables`, `tasks`, `team_assignments`, `auto_assignments`, `offboarding_requests`, `offboarding_request_activities` |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | What external system does `external_ref_id` reference (HR system, main Sleek auth provider, or CRM)? Is `isMasterUser` flag set programmatically or manually — and what privileges does it grant? What system creates `createdBy` values in production (form defaults to hardcoded `"admin"`)? Are market-specific restrictions applied server-side? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Files
- `src/users/controllers/users.controller.ts` — NestJS controller; all endpoints gated by `@SleekBackAuth('admin')`
- `src/users/services/users.service.ts` — business logic; TypeORM repository; `findAll` excludes `+`-aliased emails (filters test accounts)
- `src/users/entities/user.entity.ts` — `users` table definition; relations to deliverables, tasks, team assignments, auto assignments, offboarding requests
- `src/users/dto/create-user.dto.ts` — create payload schema
- `src/users/dto/update-user.dto.ts` — update payload (partial of create)
- `src/pages/Delivery/UserManagement.jsx` — React UI; `UserManagement` component with `DataTable`, search, create/edit dialog, delete confirmation

### API surface (`UsersController`, base route `/users`)
| Method | Route | Purpose |
|---|---|---|
| `POST` | `/users` | Create new user |
| `GET` | `/users` | Paginated user list (default 10/page; UI uses 100/page) |
| `GET` | `/users/:id` | Fetch single user by ID (loads `deliverables` + `tasks` relations) |
| `GET` | `/users/by-external-ref/:external_ref_id` | Look up user by external reference ID |
| `PATCH` | `/users/:id` | Update user (name, status) |
| `DELETE` | `/users/:id` | Remove user (204 No Content) |

### Auth
`@SleekBackAuth('admin')` applied at controller class level — all endpoints require a valid sleek-back token with `profile = 'admin'`. Token passed via `Authorization` header.

### User entity fields (`users` table)
| Field | Type | Notes |
|---|---|---|
| `firstName` | varchar(100) | Required |
| `middleName` | varchar(100) | Optional |
| `lastName` | varchar(100) | Required |
| `email` | varchar(255) | Unique; immutable on edit (UI disables input) |
| `external_ref_id` | varchar(255) | Cross-system identity reference |
| `status` | varchar(50) | `ACTIVE` \| `INACTIVE` \| `SUSPENDED`; defaults to `ACTIVE` |
| `isMasterUser` | boolean | Flag for elevated user type; defaults to `false` |
| `createdAt`, `updatedAt` | timestamps | From `SleekBase` |

### Relations loaded on `findOne`
- `deliverables` — tasks/deliverables assigned to this user
- `tasks` — tasks assigned to this user

### Client-side search (UI)
Filters by `firstName`, `middleName`, `lastName`, `email`, and full name combination — performed in the browser against the current page data.

### Status badge colours
- `ACTIVE` → green (`bg-green-100 text-green-800`)
- `INACTIVE` → gray (`bg-gray-100 text-gray-800`)
- `SUSPENDED` → red (`bg-red-100 text-red-800`)

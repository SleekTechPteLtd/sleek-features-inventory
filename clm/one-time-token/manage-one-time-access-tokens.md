# Manage One-Time Access Tokens

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | CLM |
| **Feature Name** | Manage One-Time Access Tokens |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User |
| **Business Outcome** | Enables Operations users to issue, inspect, and revoke short-lived tokens tied to a user and a billing resource, so that time-limited secure access can be granted without exposing long-lived credentials. |
| **Entry Point / Surface** | Internal REST API — `POST /one-time-token`, `GET /one-time-token/:id`, `DELETE /one-time-token/:id` |
| **Short Description** | Operations users create tokens linked to a `userId` and `referenceId` (e.g. an invoice or subscription). Tokens carry an optional expiry window (in days). Tokens can be retrieved by ID or revoked by deletion. All routes are auth-guarded. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Auth guard (`@Auth()` — JWT/internal); consuming flows that validate the token before granting access to the referenced billing resource (not visible in this module). |
| **Service / Repository** | sleek-billings-backend |
| **DB - Collections** | `onetimetokens` (MongoDB, SleekPaymentDB) |
| **Evidence Source** | codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Unknown |
| **Open Questions** | 1. TTL auto-expiry index (`expireAfterSeconds: 0`) is commented out — MongoDB will NOT purge expired tokens automatically; only explicit `DELETE` removes them. Is this intentional or a bug? 2. Where are tokens validated/consumed? No token-check logic found in this module. 3. What `referenceType` values are in use (e.g. `invoice`, `subscription`)? 4. Is there an admin UI surface for this, or is it purely API-driven? |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### Controller — `src/one-time-token/one-time-token.controller.ts`

| Method | Route | Guard | Purpose |
|---|---|---|---|
| `POST` | `/one-time-token` | `@Auth()` | Create a new token |
| `GET` | `/one-time-token/:id` | `@Auth()` | Retrieve token detail by MongoDB ID |
| `DELETE` | `/one-time-token/:id` | `@Auth()` | Revoke (delete) a token |

- All three routes require authentication via the shared `@Auth()` decorator.
- The `GET` handler validates the param as a valid MongoDB ObjectId before querying.

### Service — `src/one-time-token/services/one-time-token.service.ts`

- `createToken(data)` — calculates `expireAt = now + period days` (via `moment`); stores token via repository. `period` is optional; if omitted `expireAt` is `null` (token never expires by field value).
- `getTokenDetail(id)` — finds token by ID via `OneTimeTokenRepository.findById`.
- `deleteToken(id)` — hard-deletes by ID via `OneTimeTokenRepository.deleteById`.

No calls to external systems (Xero, Kafka, Redis, SleekBooks, ERPNext).

### DTO — `src/one-time-token/dtos/create-one-time-token.request.dto.ts`

| Field | Type | Required | Notes |
|---|---|---|---|
| `userId` | MongoId | Yes | The user the token is issued for |
| `referenceId` | MongoId | Yes | The billing resource being accessed |
| `referenceType` | string | No | Qualifier for `referenceId` (e.g. `invoice`) |
| `period` | number | No | Token lifetime in days; omit for no expiry |

Response DTO (`create-one-time-token.response.dto.ts`) returns the full `OneTimeToken` document.

### Schema — `src/one-time-token/models/one-time-token.schema.ts`

- Collection: `onetimetokens` (Mongoose default pluralization of `OneTimeToken`)
- Database: `SleekPaymentDB`
- Indexes: `userId`, `companyId` (field not on schema — stale index), `expireAt`
- TTL index (`expireAt: 1, expireAfterSeconds: 0`) is **commented out** — records do not auto-expire from the database.

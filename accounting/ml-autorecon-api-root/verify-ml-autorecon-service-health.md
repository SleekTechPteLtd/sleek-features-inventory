# Verify ML autorecon service health

## Master sheet (draft)

| Column | Value |
|---|---|
| **Domain** | Bookkeeping & Accounting |
| **Feature Name** | Verify ML autorecon service health |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operations User; System (load balancers, monitoring, orchestration); developers probing the service |
| **Business Outcome** | Confirms the ML autorecon HTTP API process is up and reachable so traffic, deployments, and automated checks can proceed before relying on autorecon and Kafka-backed work. |
| **Entry Point / Surface** | HTTP `GET /`, `GET /info`, and `GET /ping` on the ML autorecon service (no Sleek app navigation; programmatic health and discovery probes). |
| **Short Description** | Three unauthenticated GET routes return small JSON payloads: root and info advertise the service and point to `/docs` and `/redoc`; ping returns a simple “ML Server is up!” message. Together they support liveness and basic reachability checks. |
| **Variants / Markets** | Unknown |
| **Dependencies / Related Flows** | Autorecon business routes are mounted under `/autorecon` (`autorecon.endpoints.router`); startup initializes a Kafka consumer on `reconcilitation_queries_topic` and Celery—separate from these static health responses. |
| **Service / Repository** | ml-autorecon-service |
| **DB - Collections** | None |
| **Evidence Source** | codebase |
| **Criticality** | High |
| **Usage Confidence** | High |
| **Disposition** | Unknown |
| **Open Questions** | none |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### `app/main.py`

- `FastAPI()` app; `app.include_router(autorecon.endpoints.router, prefix="/autorecon")` for main autorecon API (not used by health routes).
- `@app.get("/")` → `root()` returns JSON `message` directing users to `/docs` or `/redocs`.
- `@app.get("/info")` → `info()` returns the same shape as root (duplicate messaging for info-style probing).
- `@app.get("/ping")` → `ping()` returns `{"message": "ML Server is up!"}`.
- No auth middleware or route-level guards on these handlers in this file.
- `@app.on_event("startup")` / `shutdown`: Kafka consumer lifecycle (`KafkaWrapper` + `reconcilitation_queries_topic`)—does not affect the HTTP responses of `/`, `/info`, or `/ping`, but full “service ready” for processing may require Kafka to be healthy beyond HTTP-only checks.

### Tests

- Unknown (not verified in this pass).

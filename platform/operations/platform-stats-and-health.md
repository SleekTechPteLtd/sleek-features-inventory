# Platform stats and health

## Master sheet (draft)

| Column | Value |
|--------|--------|
| **Domain** | Platform |
| **Feature Name** | Operational health and aggregated auth metrics |
| **Canonical Owner** | TBD |
| **Primary User / Actor** | Operators, SRE, internal dashboards |
| **Business Outcome** | Visibility into auth usage and liveness without exposing PII |
| **Entry Point / Surface** | `GET /stats` (authenticated); standard Nest health module if configured |
| **Short Description** | Stats returns aggregated authentication metrics; health supports probes |
| **Variants / Markets** | Environment-scoped data |
| **Dependencies / Related Flows** | Monitoring stack |
| **Service / Repository** | `sleek-auth` `src/stats/stats.controller.ts`, `health/health.controller.ts` |
| **DB - Collections** | TBD |
| **Evidence Source** | Codebase |
| **Criticality** | Medium |
| **Usage Confidence** | Medium |
| **Disposition** | Must Keep |
| **Open Questions** | Who is authorized to call `/stats` in production |
| **Reviewer** | |
| **Review Status** | Draft |

## Evidence

### sleek-auth

- `src/stats/stats.controller.ts` — `@Authenticated()` metrics.
- `src/health/health.controller.ts`

### sleek-auth-ui

- N/A (operator-facing tools may call API directly).

### sdk-auth-nest

- `@Authenticated()` and guards used to protect stats if same decorator pattern applies.

# Sleeksign (category)

**Electronic signatures, document circulation, templates, and signing workflows** — distinct from core **Platform** identity ([../authentication/](../authentication/)) and policy ([../authorization/](../authorization/)). Spreadsheet **Domain** for these rows: **`Sleeksign`** (per [Sleek Feature Scope Audit Hub](../Sleek%20Feature%20Scope%20Audit%20Hub.md)).

## Repos (evidence)

| Repo / package | Role |
|----------------|------|
| `sleek-sign/sleek-sign-backend/v1` | Dedicated **Sleek Sign API** (Express, Postgres, S3, SQS, Redis) |
| `customer-mfe/sleek-sign` | Customer **Vue** shell: proxies to monolith + sign backend |

**sleek-back** also integrates (e.g. `/v2/sleek-sign` connection, signature flows); cite those paths inside each doc’s **Evidence** where relevant.

## Capability documents

| Document | Short description |
|----------|-------------------|
| [sleeksign-v2-rest-api.md](./sleeksign-v2-rest-api.md) | `/v2/*` tenant-scoped API: drafts, admin actions, contacts, templates, free user, OTP |
| [sleeksign-legacy-document-api.md](./sleeksign-legacy-document-api.md) | `/document/*` signing, drafts, circulation, downloads, reminders |
| [sleeksign-async-pipeline-and-integrations.md](./sleeksign-async-pipeline-and-integrations.md) | S3, SQS stamping/snapshots, email, webhooks, platform vendor, health |
| [sleeksign-customer-mfe-shell.md](./sleeksign-customer-mfe-shell.md) | `customer-mfe/sleek-sign` UI and proxies |

## Related

- [../cross-repo-sleek-surfaces-map.md](../cross-repo-sleek-surfaces-map.md)
- [../inventory-scope-and-domains.md](../inventory-scope-and-domains.md)
- [../scans-pending/sleek-sign-backend/README.md](../scans-pending/sleek-sign-backend/README.md)

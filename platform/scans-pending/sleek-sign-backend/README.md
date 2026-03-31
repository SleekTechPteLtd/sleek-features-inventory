# sleek-sign-backend — scan notes

Dedicated **Sleek Sign** HTTP API (`sleek-sign/sleek-sign-backend/v1`): Express app in `app.js`, `routes/`, `routes-v2/`, Postgres + S3 + SQS.

## Inventory

Capability rows (spreadsheet **Domain** `Sleeksign`) live under [../../sleeksign/](../../sleeksign/) — not under `scans-pending/`.

## Authentication

Sleek Sign–specific **free user**, **OTP**, and **social auth init** routes are **Sleeksign** product auth, not **Sleek Auth** platform login. Do not file them under [../../authentication/](../../authentication/) as duplicate identity rows unless the outcome matches the Sleek Auth product.

## Evidence hotspots

- `app.js` — router mounts and `tenantIdGateway`
- `routes-v2/index.js` — v2 route catalogue
- `routes/document.js` — legacy document API surface

## Related

- [../../cross-repo-sleek-surfaces-map.md](../../cross-repo-sleek-surfaces-map.md)
- [../../sleeksign/README.md](../../sleeksign/README.md)

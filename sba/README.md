# SBA domain (Sleek Business Account)

Top-level domain for **Sleek Business Account** banking capabilities implemented across orchestrator and vendor microservices.

## Layout

| Path | Purpose |
|------|---------|
| `sba/feature-set/<repository-name>/` | One module folder per codebase (mirror of repo name). |
| `sba/feature-set/**/*.md` | Master-sheet markdown per capability (same table shape as `clm/feature-set`). |
| `sba/generate-sba-domain-html.py` | Regenerates `domain-sba.html` (canonical feature matrix). |

## Repositories (modules)

| Repository | Role |
|------------|------|
| `sba-bank-api` | Central orchestrator — vendor factory/proxy, routes, Kafka, webhooks. |
| `sba-bank-dbs-api` | DBS integration — FAST, PayNow, TT, A2A, virtual accounts, CAMT, FX. |
| `sba-nium-api` | NIUM cards — delegated model RHA, virtual cards, KYB, webhooks. |
| `sba-nium-payout` | NIUM payouts — beneficiaries, international remittance. |
| `customer-sba` | Customer Vue microfrontend — /sba banking UI (Single-SPA); calls `sba-bank-api`. Inventory rows are split per route in `customer-sba/src/routes/routes.js`. |

## Regenerate the domain page

From the inventory repo root:

```bash
python3 sba/generate-sba-domain-html.py
```

This reads all `sba/feature-set/**/*.md` files and writes `domain-sba.html`.

## Conventions

- **Service / Repository** must name the owning repo and any cross-repo dependencies so the matrix checkmarks resolve correctly.
- **Criticality** uses `High` / `Medium` / `Low` like other domains.
- This domain is **API-first**; there is no screenshot gallery on `domain-sba.html` (unlike CLM). Extend the generator if UI evidence is added later.

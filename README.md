# Sleek features inventory

Version-controlled **draft rows and evidence** for the **Sleek Feature Scope Audit** — a first-pass inventory of user-meaningful capabilities across Sleek domains. This repo complements the shared **Google Sheet**; it is not a substitute for it.

## What this repo is for

- **Capture** capabilities from **any** master-sheet **Domain** (Corpsec, Bookkeeping, Platform, Sleeksign, and the rest) as markdown “row drafts”: master-sheet columns, short descriptions, code/repo evidence, open questions, and review status. **We started with Platform** (shared identity, authz, integrations, operations) plus **Sleeksign** under [`platform/sleeksign/`](./platform/sleeksign/README.md); other domains can add their own top-level folders beside `platform/` as squads contribute.
- **Align** squads on definitions, overlap, and gaps before architecture or delivery planning.
- **Stay living**: treat content as **Draft** until product owners validate (see the hub doc).

The canonical **process, column definitions, and spreadsheet link** live in:

**[Sleek Feature Scope Audit Hub.md](./Sleek%20Feature%20Scope%20Audit%20Hub.md)**

## How to use it

1. **Open the hub** — Read working principles, what counts as a feature, column meanings, and the link to the **[Feature Master Sheet](https://docs.google.com/spreadsheets/d/1-8-fY-WRoXcbBYsz5XQgLYVhuUKN2Q6GQmXitJNRvGs/edit?usp=sharing)**.
2. **Add or update the sheet** — New capabilities belong in the spreadsheet first (or in parallel if you prefer), using the **Domain** enum and other columns from the hub.
3. **Add deep-draft markdown when helpful** — **Platform** drafts (including **Sleeksign** at [`platform/sleeksign/`](./platform/sleeksign/README.md)) live under [`platform/`](./platform/README.md): pick a category ([authentication](./platform/authentication/README.md), [authorization](./platform/authorization/README.md), [external-integrations](./platform/external-integrations/README.md), [operations](./platform/operations/README.md), [sleeksign](./platform/sleeksign/README.md)). **Other domains** can add their own folder at the repo root as those inventories start. Each file should mirror a sheet row and include **Evidence** (repos, paths, endpoints).
4. **Avoid duplicate auth rows** — Legacy `sleek-back` / customer admin login paths are **migration context**, not second copies of Sleek Auth rows. See [platform/authentication/README.md § Scope](./platform/authentication/README.md#scope-no-duplicate-auth-rows).
5. **Unsure which domain?** — Use [platform/inventory-scope-and-domains.md](./platform/inventory-scope-and-domains.md) and the cross-repo map [platform/cross-repo-sleek-surfaces-map.md](./platform/cross-repo-sleek-surfaces-map.md).

**Scans in progress** (notes before full rows): [`platform/scans-pending/`](./platform/scans-pending/README.md).

## Repository layout

| Path | Purpose |
|------|---------|
| `README.md` | This file — orientation and workflow |
| `Sleek Feature Scope Audit Hub.md` | Audit goals, sheet columns, process, links |
| `platform/` | First markdown area: Platform + Sleeksign; [index](./platform/README.md) |

Additional top-level folders (e.g. Corpsec, Bookkeeping) appear **as other squads add them** — same hub and sheet conventions.

## Clone

```bash
git clone git@github.com:aldrev-sleek/sleek-features-inventory.git
cd sleek-features-inventory
```

No build step — markdown only. Open the folder in your editor and the hub doc for full context.

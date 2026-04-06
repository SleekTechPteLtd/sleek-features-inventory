# Client App (Corpsec)

Inventory markdown for Corpsec capabilities whose **Entry Point / Surface** is the **Client App** in the master sheet.

## Evidence repos

| Repo | Role |
|------|------|
| **customer-main** | Vue MFE: routes (`src/routes/routes.js`), feature modules under `src/modules/` (e.g. `corporate-secretary/`, `customer-requests/`, `change-of-*`), proxies under `src/proxies/`. |
| **customer-common** | Shared package (`@sleek/customer-common`): `MasterLayout`, drawer / nav (e.g. company secretary entry), `FileDataTable`, mixins and utilities. |
| **customer-root** | single-spa shell: `src/root-config.js` registers `@sleek/customer-main` for `/customer`. |

Regenerate all client-app `*.md` files from the master CSV:

```bash
python3 scripts/generate-corpsec-client-app-md.py
```

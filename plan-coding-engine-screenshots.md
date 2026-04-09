# Plan: Coding Engine Feature Inventory + Screenshot Support

> acct-sit.sleek.com is the **Accounting Coding Engine** — one surface within the Accounting domain.
> This plan covers: (1) inventorying its visible features and restructuring the index UI to show screenshots, (2) proposing how to capture and store those screenshots in the repo.

---

## Part 1 — Feature Inventory of acct-sit.sleek.com

The app has four main sections accessed via the top nav. Country scope (UK / SG / HK / AU) applies globally. The current user is identified as a **Bookkeeping Admin**.

### Section: Documents `/home/documents`

| # | Feature | Notes |
|---|---|---|
| D1 | View document queue — To Review tab | Default view; 8,643 total documents in SIT |
| D2 | View document queue — To Reconcile tab | Separate reconciliation stage |
| D3 | View document queue — Completed tab | Completed documents |
| D4 | View all documents (cross-status) | Unfiltered full list |
| D5 | Upload a document | Button in top bar |
| D6 | Search documents | Free-text search |
| D7 | Filter documents | By: Paid by (Company / Expense claim / Sales invoice), Submission date, Publish date, Elapsed time (≤1d / ≤3d / ≤5d / ≤1mth / ≥1mth), Document date, Assignees, Status, Company Name, Client's note, Is SleekMatch |
| D8 | Switch country scope | UK / SG / HK / AU selector |
| D9 | View document row detail | Doc ID, Assigned to, Date of submission, Elapsed time, Company name, Document date, Supplier/Customer |
| D10 | Track document status | Statuses: Extracting Data → Verifying → Publishing → Duplicated / Error |
| D11 | Assign document to accountant | Assignee column in document row |
| D12 | Control page size | 50 / 100 / 250 / 1000 rows |

### Section: Suppliers `/home/suppliers`

| # | Feature | Notes |
|---|---|---|
| S1 | Browse supplier list | 2,658 suppliers in SIT |
| S2 | Search suppliers by name | Free-text |
| S3 | View supplier type and rule count | MAIN vs GENERIC; No. of Specific Rules |
| S4 | Open supplier detail page | "View" link per row |

### Section: Clients `/home/clients`

| # | Feature | Notes |
|---|---|---|
| C1 | Browse client list | 17,712 clients in SIT |
| C2 | Search clients by name | Free-text |
| C3 | View client accounting plan | e.g. Accounting Only, Accounting & Payroll, Annual Filling & Bookkeeping |
| C4 | View client document and supplier counts | Columns: No. of Documents, No. of Suppliers, No. Specific Rules |
| C5 | View client currency | Currency column |
| C6 | Open client detail page | "View" link per row |

### Section: Bank Statements `/home/bank-statements`

| # | Feature | Notes |
|---|---|---|
| B1 | Browse bank statement list | 15,599 statements in SIT |
| B2 | Upload bank statement | "Upload statement" button |
| B3 | View statement metadata | Company, Bank/Account number, Start date, End date, Review needed flag, Source, Added date |
| B4 | Filter statements | By: Company Name, Bank Name, Statement Date, Source, Review needed, Exported status, Tool, Tags |
| B5 | Track statement source | Uploaded by Client / Uploaded by Accountant / SBA feed / Mailroom / Xero feed / Automated feed / Scheduled statements |
| B6 | Track export status | Exported / Partially exported / Pending export / In Progress / Exported manually / Failed / Duplicate |
| B7 | Tag statements | Already processed, Non-accounting client, Balance mismatch, Empty-Unsupported Format, Empty-Exceed Page Limit, Multi-currency account |
| B8 | Assign tool per statement | SleekBooks / Xero / No tool |
| B9 | Flag Review needed | Yes/No per statement |

### Cross-cutting

| # | Feature |
|---|---|
| X1 | Sign in / sign out |
| X2 | User identity and role display (Bookkeeping Admin) |
| X3 | Paginate all lists (numbered pages) |

### Mapping to existing inventory

All of the above features are sourced from the **`coding-engine`** surface in `by-surface/coding-engine/bookkeeping/`. Many are already inventoried as markdown files there (e.g. `document-events/`, `suppliers/`, `customers/`, `bank/`). Screenshots would attach to those existing files.

---

## Part 2a — Reorganised Index UI with Screenshot Support

### What needs to change

The current `domain-accounting.html` (and by extension the coding-engine portion) renders each feature as a plain `<li>` link. To support screenshots it needs:

1. **A thumbnail slot per feature** — shows the screenshot if present, a placeholder if not
2. **A coverage indicator** — how many of this surface's features have screenshots
3. **A lightweight inline preview** — clicking a thumbnail expands it without leaving the page

### Proposed layout change for the feature list

Replace the current two-column `<ul>` feature list with a **card grid** per surface. Each card contains:

```
┌─────────────────────────────────────────────┐
│  [thumbnail or grey placeholder]            │
│  Feature Name                               │
│  Short description (one line)               │
│  [Draft] [High]  📷 or 📷?                  │
└─────────────────────────────────────────────┘
```

- Screenshot thumbnail: 160×100px, clicking opens full-size in a lightbox
- Placeholder: dashed grey box with "No screenshot" label + a "📷 Add" link
- Pills: Review Status + Criticality (already in feature markdown)
- Camera icon: filled = has screenshot, outlined = missing

### Coverage stat strip

Add a new pill to the existing stats panel on domain pages:

```
[Surfaces: 4]  [Features: 25]  [Must-have: –]  [Screenshots: 12 / 25]
```

The screenshot count is computed by checking whether each linked markdown file has an image in the screenshots folder.

### Implementation approach

The domain index pages (`domain-accounting.html`) already load feature lists from the `by-surface/` folder structure. The change is:

1. Add a `screenshots/` folder under each surface (e.g. `by-surface/coding-engine/screenshots/`)
2. Name each screenshot after the feature markdown file slug (e.g. `document-list-to-review.png`)
3. In `domain-accounting.html`: for each feature link, check `by-surface/{surface}/screenshots/{slug}.png` — if the file exists, render it as a thumbnail; if not, render the placeholder
4. In `viewer.html`: add a screenshot banner at the top of each feature page when the image exists

This is a pure frontend change — no server-side logic, just `fetch(imgPath).then(ok => showThumbnail()).catch(() => showPlaceholder())`.

---

## Part 2b — Screenshot Capture & Storage Workflow

### Storage convention

```
by-surface/
  coding-engine/
    screenshots/
      documents/
        document-list-to-review.png
        document-list-to-reconcile.png
        document-detail-verifying.png
        document-filters.png
        document-upload.png
      suppliers/
        supplier-list.png
        supplier-detail.png
      clients/
        client-list.png
        client-detail.png
      bank-statements/
        bank-statement-list.png
        bank-statement-filters.png
        bank-statement-upload.png
```

**Rules:**
- PNG, max 1400px wide (retina screenshots should be saved at 1x or downscaled)
- Name matches the feature slug (same slug as the markdown file) — one screenshot per feature is enough for first pass
- If a feature has multiple states worth showing (e.g. "Verifying" vs "Publishing"), use a suffix: `document-detail-verifying.png`, `document-detail-publishing.png`

### Capture workflow (first pass, manual)

1. Open acct-sit.sleek.com in Chrome, signed in as Bookkeeping Admin
2. Navigate to the feature/screen being captured
3. Set a consistent window width (1440px recommended) — avoids inconsistent crops
4. Hide personal/test data if sensitive (blur or use test data already in SIT)
5. Take screenshot:
   - **Mac**: Cmd+Shift+4 → Space → click window, or use browser DevTools device mode for consistent sizing
   - **Chrome**: DevTools → Cmd+Shift+P → "Capture screenshot" for full-page or node screenshot
6. Save to `by-surface/coding-engine/screenshots/<section>/<slug>.png`
7. Commit with message: `screenshots: add <section> first pass`

### Capture workflow (automated, future)

Claude in Chrome can navigate to each page and call `gif_creator` or `computer` screenshot tools to capture all views in a single run. This would:
1. Visit each route in the feature inventory above
2. Screenshot each state (e.g. tab variants for Documents)
3. Save all images to the `screenshots/` folder under the correct slug names
4. Create a commit with the full first-pass set

This is feasible to run as a scheduled task once the naming convention is agreed.

### Frontmatter addition (optional)

To make the screenshot path explicit in the markdown (rather than inferred from filename), add a `screenshot` key to each feature file's master sheet table:

```markdown
| **Screenshot** | screenshots/documents/document-list-to-review.png |
```

`viewer.html` would then render this as an image above the master sheet. If the field is absent, no image is shown.

### Precedence order

1. Explicit `screenshot` frontmatter field (most precise — can point to any path)
2. Auto-inferred from slug (fallback — works without editing every markdown file)

---

## Summary

| Work item | Effort | Owner suggestion |
|---|---|---|
| Capture first-pass screenshots for all 25 coding-engine features | ~1h manual, or automated | Richard / QA |
| Add `screenshots/` folder structure to repo | 10 min | Richard |
| Update `domain-accounting.html` card layout with thumbnail slots | ~2h dev | Dev |
| Update `viewer.html` to show screenshot banner | ~30min dev | Dev |
| (Optional) Add `screenshot` field to feature markdown files | Low, batch-editable | Anyone |
| (Optional) Build automated screenshot capture scheduled task | ~1h | Claude |

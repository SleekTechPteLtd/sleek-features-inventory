# Accounting Feature Review — Instructions

We need your help reviewing the accounting feature inventory. It's a simple tool — takes maybe 20–30 minutes to go through your area.

---

## Setup

You'll need **Node.js** installed. If you don't have it: [nodejs.org](https://nodejs.org).

```bash
# 1. Clone the repo
git clone git@github.com:SleekTechPteLtd/sleek-features-inventory.git
cd sleek-features-inventory

# 2. Install dependencies
npm install

# 3. Pull the latest annotations before you start
git pull

# 4. Start the server
npm start
```

Open **http://localhost:3000/domain-accounting.html** in your browser.

---

## What you're looking at

The page has four sections:

### 1. Screenshot grids
Live screenshots of each of the four accounting surfaces:

- **Coding Engine** (`acct-sit.sleek.com`) — the internal tool accountants use to review and code documents
- **Customer Portal** (`sg-app-sit.sleek.com`) — what clients see: expenses, invoices, bank statements
- **Admin App** (`admin-sit.sleek.sg`) — internal ops: companies, users, KYC, billing, workflows
- **SleekBooks** (`au-books-staging.sleek.com`) — the ERPNext ledger: reconciliation, reports, chart of accounts

These give you a quick picture of what each surface actually looks like right now. Click any thumbnail to see the full screenshot.

### 2. Canonical Feature Matrix
This is the main thing we need your input on. It's a table of every capability we've identified, organised by category (Documents & Receipts, Bank Statements, Reconciliation, Invoicing, Reports, etc.).

Each row shows which surfaces have that feature (CE / CP / AA / SB) and has three annotation columns on the right:

| Column | What to do |
|--------|-----------|
| **Priority** | Set **High / Medium / Low** if this feature matters for your area. Leave blank if you don't know or don't care. |
| **Notes** | Add any context — is it broken? Confusing? Half-built? Missing from one surface where it should exist? |
| **FP** (False Positive) | Tick this if the row is wrong — the feature doesn't actually exist, or it's listed incorrectly. |

Changes save automatically as you make them — there's no save button.

**If a feature is missing from the list entirely**, click **+ Add feature** (top-right of the matrix). You'll need to provide a URL where the feature can be seen — this is required so we can verify it exists. Pick the category, tick which surfaces have it, and submit. It'll appear as a new row.

### 3. Backend Workflows
A summary of the key data flows between surfaces — document ingestion, bank reconciliation, client onboarding, ledger sync. Read-only, just for context.

### 4. Full inventory
The full raw scan of every API endpoint and feature, organised by surface. This is the detailed source material. You probably won't need to read this, but it's there if you want to dig in.

---

## When you're done

The app stores everything in `feature-annotations.json` — a plain text file in the repo. Once you've finished annotating your section, commit and push it:

```bash
git add feature-annotations.json
git commit -m "annotations: <your name> — <your area>"
git push
```

That's it. If there's a merge conflict (someone else pushed while you were reviewing), run `git pull --rebase` — since it's plain JSON, Git can usually sort it out automatically as long as you weren't both editing the exact same row.

---

## What we're focused on

**Accounting only for now.** The other domains (Platform, CLM, Compliance, CorpSec) aren't ready yet — ignore those pages.

You don't need to review every row — just the ones relevant to your area. Focus on what you know.

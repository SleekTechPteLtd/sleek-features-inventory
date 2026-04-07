# Accounting domain (inventory)

This folder is the **Accounting** TLD in the Sleek features inventory.

- **Module** = immediate child folder (for example `reconciliation/`, `xero/`).
- **Feature** = one markdown file per capability under that module (for example `accept-or-reject-ml-reconciliation-matches.md`).

Each feature file follows the shared inventory template (master sheet draft, evidence, and so on).

## Visual roadmap page

The domain overview with links to every feature row is generated into [`../domain-accounting.html`](../domain-accounting.html) from the filesystem.

Regenerate after adding, renaming, or removing feature files:

```bash
python3 scripts/generate-accounting-domain-html.py
```

Run the command from the repository root. Commit the updated `domain-accounting.html` together with inventory changes.

## Must-have for migration

On [`domain-accounting.html`](../domain-accounting.html), add a `[Must-have]` prefix before a linked feature title in the HTML list item when that capability is in scope for migration (same convention as the CorpSec domain page).

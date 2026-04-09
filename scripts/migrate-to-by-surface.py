#!/usr/bin/env python3
"""
Move corpsec/ and accounting/ inventory into by-surface/{customer-app,admin-app,sleekbooks,coding-engine}/.

Run from repo root:
  python3 scripts/migrate-to-by-surface.py --dry-run
  python3 scripts/migrate-to-by-surface.py
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BY = ROOT / "by-surface"

# Exact relative path (from accounting/) -> surface
ACCOUNTING_FILE_OVERRIDES: dict[str, str] = {}

# Prefix under accounting/ -> surface (longest match wins)
ACCOUNTING_PREFIX_OVERRIDES: list[tuple[str, str]] = [
    ("sleek-site-onboarding/", "customer-app"),
    ("tasks-command/", "sleekbooks"),
    ("sleekbooks/", "sleekbooks"),
    ("webhook/propagate-bank-reconciliation-from-sb", "sleekbooks"),
    ("webhook/forward-erpnext-invoices-to-sleek-receipts", "sleekbooks"),
    ("reconciliation-listener/apply-core-engine-bank-reconciliation-to-erpnext", "sleekbooks"),
    ("report-generation/", "sleekbooks"),
    ("platform/", "sleekbooks"),
    ("permission/", "sleekbooks"),
    ("xero/provision-", "sleekbooks"),
    ("xero/connect-", "sleekbooks"),
    ("xero/access-", "sleekbooks"),
]


def extract_field(text: str, field: str) -> str:
    """Extract markdown table cell after | **Field** |."""
    pat = rf"\|\s*\*\*{re.escape(field)}\*\*\s*\|\s*([^|]+)\|"
    m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def classify_accounting(rel: str, text: str) -> str:
    """rel is like 'xero/foo.md' (no 'accounting/' prefix)."""
    if rel in ACCOUNTING_FILE_OVERRIDES:
        return ACCOUNTING_FILE_OVERRIDES[rel]

    for prefix, surf in sorted(ACCOUNTING_PREFIX_OVERRIDES, key=lambda x: -len(x[0])):
        if rel.startswith(prefix) or rel == prefix.rstrip("/"):
            return surf

    svc = extract_field(text, "Service / Repository").lower()
    entry = extract_field(text, "Entry Point / Surface").lower()

    if any(x in svc for x in ("customer-main", "customer-common", "customer-root")):
        return "customer-app"
    if "sleek-website" in svc:
        return "admin-app"
    if "sleek-erpnext-service" in svc or "xero-sleekbooks-service" in svc:
        return "sleekbooks"
    if "acct-coding-engine" in svc or "sleek-receipts" in svc:
        return "coding-engine"
    if "supplier-rules-service" in svc:
        return "coding-engine"
    if "coding-engine" in svc and "url" in svc:  # external HTTP to CE
        return "coding-engine"
    if "sleek-ml-node-server" in svc:
        return "coding-engine"
    if "sleek-bot-pilot" in svc:
        return "coding-engine"

    if "sleek-back" in svc:
        customer_hints = (
            "client app",
            "customer app",
            "client portal",
            "customer ",
            "sleek app",
            "mobile",
            "marketing website",
            "prospect",
            "signup",
            "sleek-site-onboarding",
            "incorporation",
            "website onboarding",
        )
        if any(x in entry for x in customer_hints):
            return "customer-app"
        return "admin-app"

    # Multi-service lines without sleek-back
    if "xero-sleekbooks" in svc or "erpnext" in svc:
        return "sleekbooks"

    # Fallback from entry point
    if any(x in entry for x in ("admin", "sleek admin", "/admin/")) and "client" not in entry:
        return "admin-app"
    if any(x in entry for x in ("client app", "customer app", "customer ", "portal")):
        return "customer-app"

    return "coding-engine"


def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    moves: list[tuple[Path, Path, str]] = []

    # --- accounting/*.md under module dirs ---
    accounting = ROOT / "accounting"
    if accounting.is_dir():
        for mod in sorted(accounting.iterdir()):
            if not mod.is_dir() or mod.name.startswith("."):
                continue
            for md in sorted(mod.glob("*.md")):
                rel = f"{mod.name}/{md.name}"
                text = md.read_text(encoding="utf-8")
                surf = classify_accounting(rel, text)
                dest = BY / surf / "bookkeeping" / mod.name / md.name
                moves.append((md, dest, surf))

    # --- corpsec client-app ---
    for md in sorted((ROOT / "corpsec" / "client-app").glob("*.md")):
        dest = BY / "customer-app" / "corpsec" / md.name
        moves.append((md, dest, "customer-app"))

    # --- corpsec admin-app ---
    for md in sorted((ROOT / "corpsec" / "admin-app").glob("*.md")):
        dest = BY / "admin-app" / "corpsec" / md.name
        moves.append((md, dest, "admin-app"))

    legacy = ROOT / "corpsec" / "company-register-management.md"
    if legacy.is_file():
        moves.append((legacy, BY / "admin-app" / "corpsec" / legacy.name, "admin-app"))

    # Collision check
    dests: dict[Path, list[Path]] = {}
    for src, dst, _ in moves:
        dests.setdefault(dst, []).append(src)

    bad = {d: s for d, s in dests.items() if len(s) > 1}
    if bad:
        for d, s in bad.items():
            print("COLLISION", d, s)
        return 1

    for src, dst, surf in moves:
        if args.dry_run:
            print(f"{surf}: {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
        else:
            ensure_parent(dst)
            shutil.move(str(src), str(dst))

    if not args.dry_run:
        # Remove empty accounting module dirs and corpsec subdirs
        if accounting.is_dir():
            for mod in sorted(accounting.iterdir()):
                if mod.is_dir() and not any(mod.iterdir()):
                    mod.rmdir()
            # remove accounting/README if we keep a stub — leave README for now
        for sub in ("client-app", "admin-app"):
            p = ROOT / "corpsec" / sub
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()

    print(f"{'Would move' if args.dry_run else 'Moved'} {len(moves)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

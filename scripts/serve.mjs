#!/usr/bin/env node
/**
 * Feature Matrix annotation server
 * Persists annotations to feature-annotations.json (plain text, git-friendly)
 *
 * Usage: npm start
 *        open http://localhost:3000/domain-accounting.html
 */

import express from 'express';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT      = join(__dirname, '..');
const DB_PATH   = join(ROOT, 'feature-annotations.json');

// ── In-memory state ────────────────────────────────────────────────────────
function load() {
  if (existsSync(DB_PATH)) {
    return JSON.parse(readFileSync(DB_PATH, 'utf8'));
  }
  return { annotations: {}, additions: [] };
}

function save(state) {
  writeFileSync(DB_PATH, JSON.stringify(state, null, 2), 'utf8');
}

let state = load();

// ── Express ────────────────────────────────────────────────────────────────
const app = express();
app.use(express.json());
app.use(express.static(ROOT));

app.get('/api/state', (_req, res) => {
  res.json({
    annotations: Object.entries(state.annotations).map(([row_id, ann]) => ({ row_id: Number(row_id), ...ann })),
    additions:   state.additions,
  });
});

app.put('/api/annotations/:rowId', (req, res) => {
  const rowId = parseInt(req.params.rowId, 10);
  if (isNaN(rowId)) return res.status(400).json({ error: 'invalid rowId' });
  const { priority, comment, false_positive } = req.body;
  state.annotations[rowId] = {
    priority:       priority || null,
    comment:        comment  || '',
    false_positive: !!false_positive,
  };
  save(state);
  res.json({ ok: true });
});

app.delete('/api/annotations/:rowId', (req, res) => {
  delete state.annotations[parseInt(req.params.rowId, 10)];
  save(state);
  res.json({ ok: true });
});

app.post('/api/additions', (req, res) => {
  const { category, capability, url, ce, cp, aa, sb, priority, comment } = req.body;
  if (!category || !capability || !url) {
    return res.status(400).json({ error: 'category, capability, and url are required' });
  }
  const id = state.additions.length
    ? Math.max(...state.additions.map(a => a.id)) + 1
    : 1;
  const row = { id, category, capability, url, ce: !!ce, cp: !!cp, aa: !!aa, sb: !!sb, priority: priority || null, comment: comment || '', false_positive: false };
  state.additions.push(row);
  save(state);
  res.json({ id });
});

app.delete('/api/additions/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  state.additions = state.additions.filter(a => a.id !== id);
  save(state);
  res.json({ ok: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n  Feature inventory running at http://localhost:${PORT}/domain-accounting.html\n`);
});

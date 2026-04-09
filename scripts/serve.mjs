#!/usr/bin/env node
/**
 * Feature Matrix annotation server
 * Serves the HTML statically and persists annotations to feature-annotations.sqlite
 *
 * Usage: npm start
 *        open http://localhost:3000/domain-accounting.html
 */

import express from 'express';
import Database from 'better-sqlite3';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const DB_PATH = join(ROOT, 'feature-annotations.sqlite');

const db = new Database(DB_PATH);

db.exec(`
  CREATE TABLE IF NOT EXISTS annotations (
    row_id         INTEGER PRIMARY KEY,
    priority       TEXT CHECK(priority IN ('high', 'medium', 'low')),
    comment        TEXT DEFAULT '',
    false_positive INTEGER DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS additions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    category       TEXT NOT NULL,
    capability     TEXT NOT NULL,
    url            TEXT NOT NULL,
    ce             INTEGER DEFAULT 0,
    cp             INTEGER DEFAULT 0,
    aa             INTEGER DEFAULT 0,
    sb             INTEGER DEFAULT 0,
    priority       TEXT,
    comment        TEXT DEFAULT '',
    false_positive INTEGER DEFAULT 0
  );
`);

const upsertAnnotation = db.prepare(`
  INSERT INTO annotations (row_id, priority, comment, false_positive)
  VALUES (@row_id, @priority, @comment, @false_positive)
  ON CONFLICT(row_id) DO UPDATE SET
    priority       = excluded.priority,
    comment        = excluded.comment,
    false_positive = excluded.false_positive
`);

const app = express();
app.use(express.json());
app.use(express.static(ROOT));

app.get('/api/state', (_req, res) => {
  const annotations = db.prepare('SELECT * FROM annotations').all();
  const additions   = db.prepare('SELECT * FROM additions ORDER BY id').all();
  res.json({ annotations, additions });
});

app.put('/api/annotations/:rowId', (req, res) => {
  const row_id = parseInt(req.params.rowId, 10);
  if (isNaN(row_id)) return res.status(400).json({ error: 'invalid rowId' });
  const { priority, comment, false_positive } = req.body;
  upsertAnnotation.run({
    row_id,
    priority:       priority || null,
    comment:        comment  || '',
    false_positive: false_positive ? 1 : 0,
  });
  res.json({ ok: true });
});

app.delete('/api/annotations/:rowId', (req, res) => {
  db.prepare('DELETE FROM annotations WHERE row_id = ?').run(parseInt(req.params.rowId, 10));
  res.json({ ok: true });
});

app.post('/api/additions', (req, res) => {
  const { category, capability, url, ce, cp, aa, sb, priority, comment } = req.body;
  if (!category || !capability || !url) {
    return res.status(400).json({ error: 'category, capability, and url are required' });
  }
  const result = db.prepare(`
    INSERT INTO additions (category, capability, url, ce, cp, aa, sb, priority, comment)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    category, capability, url,
    ce ? 1 : 0, cp ? 1 : 0, aa ? 1 : 0, sb ? 1 : 0,
    priority || null, comment || '',
  );
  res.json({ id: result.lastInsertRowid });
});

app.delete('/api/additions/:id', (req, res) => {
  db.prepare('DELETE FROM additions WHERE id = ?').run(parseInt(req.params.id, 10));
  res.json({ ok: true });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`\n  Feature inventory running at http://localhost:${PORT}/domain-accounting.html\n`);
});

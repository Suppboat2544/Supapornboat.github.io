#!/usr/bin/env node
/**
 * Thin wrapper — canonical builder is scripts/build.py
 * (builds EN + TH + JA locale sites for GitHub Pages).
 */
const { spawnSync } = require('child_process');
const path = require('path');

const py = spawnSync('python3', [path.join(__dirname, 'build.py')], {
  stdio: 'inherit',
  cwd: path.join(__dirname, '..'),
});

process.exit(py.status == null ? 1 : py.status);

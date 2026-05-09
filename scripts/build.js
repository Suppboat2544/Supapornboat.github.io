const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, '..', 'src');
const OUT = path.join(__dirname, '..', 'docs');

async function rmrf(dir) {
  if (!fs.existsSync(dir)) return;
  await fs.promises.rm(dir, { recursive: true, force: true });
}

async function copyRecursive(src, dest) {
  const stat = await fs.promises.stat(src);
  if (stat.isDirectory()) {
    await fs.promises.mkdir(dest, { recursive: true });
    const entries = await fs.promises.readdir(src);
    for (const e of entries) {
      await copyRecursive(path.join(src, e), path.join(dest, e));
    }
  } else {
    // simple text replace for {{year}} token
    let content = await fs.promises.readFile(src);
    const ext = path.extname(src).toLowerCase();
    if (['.html', '.htm', '.css', '.js', '.txt'].includes(ext)) {
      content = content.toString().replace(/{{\s*year\s*}}/g, new Date().getFullYear());
    }
    await fs.promises.mkdir(path.dirname(dest), { recursive: true });
    await fs.promises.writeFile(dest, content);
  }
}

(async () => {
  try {
    await rmrf(OUT);
    await copyRecursive(SRC, OUT);
    console.log('Build complete. Output in docs/');
  } catch (err) {
    console.error('Build failed:', err);
    process.exit(1);
  }
})();

# githubio-site

Minimal GitHub Pages-ready static site scaffold.

How it works:

- Author content in `src/` (HTML, CSS, assets).
- Run `npm run build` to copy `src/` -> `docs/` (GitHub Pages serves `docs/` on the `main` branch).
- Run `npm run serve` to locally serve the generated `docs/` at http://localhost:8080

Files created:

- `src/` - source files (index, about, styles)
- `scripts/` - tiny Node scripts for build/clean/serve
- `docs/` - generated output after `npm run build`

Publish on GitHub Pages:

1. Create a repo named `yourusername.github.io` and push this project to `main`.
2. GitHub Pages will serve files from the `docs/` folder by default.

Notes:
- This scaffold intentionally has no external build dependencies so it works without npm installs.
- If you prefer Jekyll/Hugo/Eleventy, tell me and I can scaffold that instead.

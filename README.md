# Supaporn Klabklaydee — Personal Academic Website

Personal academic site for **Supaporn Klabklaydee (Boat)**, Ph.D. student in Civil and Environmental Engineering at the [Institute of Science Tokyo](https://www.isct.ac.jp/en).

🌐 **Live site:** https://suppboat2544.github.io/Supapornboat.github.io/

---

## About

This site showcases Boat's research, publications, and projects in computational environmental science and cheminformatics:

- Graph Neural Networks for toxicity prediction & biotransformation modeling
- PFAS analysis and transformation product identification
- Dissolved Organic Matter (DOM) chemical space refinement
- Structure-aware genetic algorithms (GSAT, CRAM-GTransformer)

---

## Pages

| Page | Description |
|---|---|
| [Home](src/index.html) | Cinematic hero, current work, publications, talks teaser |
| [About](src/about.html) | Bio, education, awards, internships, research hub |
| [Research](src/research.html) | Research themes and methodology |
| [Publications](src/publications.html) | Peer-reviewed papers and preprints |
| [Talks](src/talks.html) | Presentations, competitions, recognition |
| [Projects](src/projects.html) | CRAM/GSAT flagship work + open-source repos |
| [CV](src/cv.html) | Full curriculum vitae |
| [CRAM](src/cram.html) | PhD thesis — CRAM-GTransformer |
| [GSAT](src/gsat.html) | Published GSAT model documentation |

---

## Tech Stack

- Pure static HTML / CSS / JS — zero runtime dependencies
- Cinematic dark theme with liquid-glass navigation
- Google Fonts (Instrument Serif, Inter, JetBrains Mono)
- Deployed via **GitHub Actions** → `node scripts/build.js` → `docs/` → GitHub Pages

---

## Development

Edit source files in `src/`, then build and push:

```bash
node scripts/build.js
git add -A && git commit -m "your message" && git push
```

CI runs the same build step before deploy. Do not edit `docs/` directly.

---

## Contact

- ✉️ klabklaydee.s.aa@m.titech.ac.jp
- ✉️ suppaporn.2544@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/supaporn-klabklaydee-1a43401b6)
- 🔗 [ORCID](https://orcid.org/0009-0000-9747-711X)
- 🔗 [GitHub](https://github.com/Suppboat2544)

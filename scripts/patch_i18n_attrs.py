#!/usr/bin/env python3
"""Patch HTML sources with data-i18n / data-i18n-html attributes for full localization."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def once(text: str, old: str, new: str) -> str:
    if old not in text:
        print("MISS:", old[:80].replace("\n", " "))
        return text
    return text.replace(old, new, 1)


def patch_footer():
    p = SRC / "snippets" / "footer.html"
    t = p.read_text(encoding="utf-8")
    t = once(
        t,
        "<p>Structure-aware machine learning for molecular toxicology, biotransformation, PFAS fate, and aquatic chemical space.</p>",
        '<p data-i18n="footer.blurb">Structure-aware machine learning for molecular toxicology, biotransformation, PFAS fate, and aquatic chemical space.</p>',
    )
    replacements = [
        ("<h4>Pages</h4>", '<h4 data-i18n="footer.pages">Pages</h4>'),
        ("<h4>Current Work</h4>", '<h4 data-i18n="footer.currentWork">Current Work</h4>'),
        ("<h4>More</h4>", '<h4 data-i18n="footer.more">More</h4>'),
        ('<a href="index.html">Home</a>', '<a href="index.html" data-i18n="footer.home">Home</a>'),
        ('<a href="about.html">About</a>', '<a href="about.html" data-i18n="footer.about">About</a>'),
        ('<a href="research.html">Research</a>', '<a href="research.html" data-i18n="footer.research">Research</a>'),
        ('<a href="cram.html">CRAM-GTransformer</a>', '<a href="cram.html" data-i18n="footer.cram">CRAM-GTransformer</a>'),
        ('<a href="gsat.html">GSAT Model</a>', '<a href="gsat.html" data-i18n="footer.gsat">GSAT Model</a>'),
        ('<a href="publications.html">Publications</a>', '<a href="publications.html" data-i18n="footer.publications">Publications</a>'),
        ('<a href="talks.html">Talks</a>', '<a href="talks.html" data-i18n="footer.talks">Talks</a>'),
        ('<a href="projects.html">Projects</a>', '<a href="projects.html" data-i18n="footer.projects">Projects</a>'),
        ('<a href="cv.html">CV</a>', '<a href="cv.html" data-i18n="footer.cv">CV</a>'),
        ('<a href="win95.html">BoatOS Desktop</a>', '<a href="win95.html" data-i18n="footer.boatos">BoatOS Desktop</a>'),
    ]
    for a, b in replacements:
        t = once(t, a, b)
    p.write_text(t, encoding="utf-8")
    print("footer ok")


def patch_index():
    p = SRC / "index.html"
    t = p.read_text(encoding="utf-8")
    reps = [
        (
            """              <h1 class="hero-cinematic-title">
                From <em class="hero-em">molecular graphs</em><br class="hero-br">to <em class="hero-em">environmental fate.</em>
              </h1>
              <p class="hero-cinematic-sub" data-i18n="home.headline">
                Boat — Ph.D. researcher building structure-aware ML on molecular graphs:
                GNN-based LC<sub>50</sub> prediction, biotransformation pathway modeling, PFAS transformation products, and DOM chemical space.
              </p>""",
            """              <h1 class="hero-cinematic-title" data-i18n-html="home.heroTitleHtml">
                From <em class="hero-em">molecular graphs</em><br class="hero-br">to <em class="hero-em">environmental fate.</em>
              </h1>
              <p class="hero-cinematic-sub" data-i18n-html="home.headlineHtml">
                Boat — Ph.D. researcher building structure-aware ML on molecular graphs:
                GNN-based LC<sub>50</sub> prediction, biotransformation pathway modeling, PFAS transformation products, and DOM chemical space.
              </p>""",
        ),
        (
            '<a href="research.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-primary">Research Areas</a>',
            '<a href="research.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-primary" data-i18n="home.ctaResearch">Research Areas</a>',
        ),
        (
            '<a href="publications.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-secondary">Publications</a>',
            '<a href="publications.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-secondary" data-i18n="home.ctaPubs">Publications</a>',
        ),
        (
            '<a href="win95.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-secondary" title="Full desktop experience">Open BoatOS Desktop</a>',
            '<a href="win95.html" class="liquid-glass hero-cinematic-cta hero-cinematic-cta-secondary" title="Full desktop experience" data-i18n="home.ctaDesktop">Open BoatOS Desktop</a>',
        ),
        (
            '<p class="hero-portrait-caption">Boat · Ph.D. · Fujii Lab</p>',
            '<p class="hero-portrait-caption" data-i18n="home.portraitCap">Boat · Ph.D. · Fujii Lab</p>',
        ),
        (
            "<span>Welcome.txt — BoatOS 95</span>",
            '<span data-i18n="home.welcomeTitle">Welcome.txt — BoatOS 95</span>',
        ),
        (
            '<span class="hero-scroll-text">Research</span>',
            '<span class="hero-scroll-text" data-i18n="home.scrollResearch">Research</span>',
        ),
        (
            '<div class="stat-item"><span class="stat-num" data-count="5">5</span><span class="stat-label">Publications</span></div>',
            '<div class="stat-item"><span class="stat-num" data-count="5">5</span><span class="stat-label" data-i18n="home.statPubs">Publications</span></div>',
        ),
        (
            '<div class="stat-item"><span class="stat-num" data-count="7">7</span><span class="stat-label">Research Topics</span></div>',
            '<div class="stat-item"><span class="stat-num" data-count="7">7</span><span class="stat-label" data-i18n="home.statTopics">Research Topics</span></div>',
        ),
        (
            '<div class="stat-item"><span class="stat-num" data-count="3">3</span><span class="stat-label">Research Labs</span></div>',
            '<div class="stat-item"><span class="stat-num" data-count="3">7</span><span class="stat-label" data-i18n="home.statLabs">Research Labs</span></div>',
        ),
    ]
    # Fix accidental typo if I introduced one - check carefully
    # Wait I made a bug: data-count="3">7 - fix that
    reps_fixed = []
    for a, b in reps:
        if 'data-count="3">7' in b:
            b = b.replace('data-count="3">7', 'data-count="3">3')
        reps_fixed.append((a, b))
    for a, b in reps_fixed:
        t = once(t, a, b)

    more = [
        (
            '<div class="stat-item"><span class="stat-num" data-count="8">8</span><span class="stat-label">Awards</span></div>',
            '<div class="stat-item"><span class="stat-num" data-count="8">8</span><span class="stat-label" data-i18n="home.statAwards">Awards</span></div>',
        ),
        (
            '<div class="section-label" style="margin-top:44px">Current Work</div>',
            '<div class="section-label" style="margin-top:44px" data-i18n="home.currentWork">Current Work</div>',
        ),
        (
            '<span class="current-work-badge">PhD Thesis · In Progress</span>',
            '<span class="current-work-badge" data-i18n="home.cramBadge">PhD Thesis · In Progress</span>',
        ),
        (
            "<h3>CRAM-GTransformer</h3>\n          <p>Property-conditioned deep learning for carboxyl-rich aliphatic/alicyclic molecules (CRAM) and site-specific, pathway-level DOM biotransformation.</p>\n          <span class=\"current-work-link\">View CRAM project →</span>",
            '<h3 data-i18n="home.cramTitle">CRAM-GTransformer</h3>\n          <p data-i18n="home.cramDesc">Property-conditioned deep learning for carboxyl-rich aliphatic/alicyclic molecules (CRAM) and site-specific, pathway-level DOM biotransformation.</p>\n          <span class="current-work-link" data-i18n="home.cramLink">View CRAM project →</span>',
        ),
        (
            '<span class="current-work-badge">Published · ACS ES&amp;T Water 2026</span>',
            '<span class="current-work-badge" data-i18n="home.gsatBadge">Published · ACS ES&T Water 2026</span>',
        ),
        (
            "<h3>GSAT Model</h3>\n          <p>Graph–Sequence Attention Transformer for multigenerational ecotoxicity prediction — R² = 0.907 on LC<sub>50</sub> benchmarks.</p>\n          <span class=\"current-work-link\">View GSAT model →</span>",
            '<h3 data-i18n="home.gsatTitle">GSAT Model</h3>\n          <p data-i18n-html="home.gsatDescHtml">Graph–Sequence Attention Transformer for multigenerational ecotoxicity prediction — R² = 0.907 on LC<sub>50</sub> benchmarks.</p>\n          <span class="current-work-link" data-i18n="home.gsatLink">View GSAT model →</span>',
        ),
        (
            '<div class="home-kv"><span>Focus</span><strong data-i18n="home.aboutFocusVal">',
            '<div class="home-kv"><span data-i18n="home.kvFocus">Focus</span><strong data-i18n="home.aboutFocusVal">',
        ),
        (
            '<div class="home-kv"><span>Thesis</span><strong data-i18n="home.aboutThesisVal">',
            '<div class="home-kv"><span data-i18n="home.kvThesis">Thesis</span><strong data-i18n="home.aboutThesisVal">',
        ),
        (
            '<div class="home-kv"><span>Education</span><strong data-i18n="home.aboutEduVal">',
            '<div class="home-kv"><span data-i18n="home.kvEducation">Education</span><strong data-i18n="home.aboutEduVal">',
        ),
        (
            '<div class="home-kv"><span>Labs</span><strong data-i18n="home.aboutCollabVal">',
            '<div class="home-kv"><span data-i18n="home.kvLabs">Labs</span><strong data-i18n="home.aboutCollabVal">',
        ),
        (
            '<div class="home-kv"><span>Open to</span><strong data-i18n="home.aboutOpenVal">',
            '<div class="home-kv"><span data-i18n="home.kvOpen">Open to</span><strong data-i18n="home.aboutOpenVal">',
        ),
        (
            '<strong data-i18n="home.pipe3t">3 · Fate &amp; toxicity</strong>\n                <span data-i18n="home.pipe3d">LC<sub>50</sub>, biotransformation pathways, kinetic / PINN persistence</span>',
            '<strong data-i18n="home.pipe3t">3 · Fate &amp; toxicity</strong>\n                <span data-i18n-html="home.pipe3dHtml">LC<sub>50</sub>, biotransformation pathways, kinetic / PINN persistence</span>',
        ),
        (
            '<div class="highlight-cat">⬡ Bioinformatics</div>\n          <h3>Protein &amp; Enzyme Discovery</h3>\n          <p>Large-scale computational discovery of marine enzymes using protein language models, deep clustering, and structural analysis.</p>\n          <a href="research.html" class="highlight-link">Explore →</a>',
            '<div class="highlight-cat" data-i18n="home.area1Cat">⬡ Bioinformatics</div>\n          <h3 data-i18n="home.area1Title">Protein &amp; Enzyme Discovery</h3>\n          <p data-i18n="home.area1Desc">Large-scale computational discovery of marine enzymes using protein language models, deep clustering, and structural analysis.</p>\n          <a href="research.html" class="highlight-link" data-i18n="common.explore">Explore →</a>',
        ),
        (
            '<div class="highlight-cat">⬡ Chemoinformatics</div>\n          <h3>Chemical Space &amp; Molecular AI</h3>\n          <p>Generative models and graph neural networks for molecular formula assignment, toxicity prediction, and chemical space exploration.</p>\n          <a href="research.html" class="highlight-link">Explore →</a>',
            '<div class="highlight-cat" data-i18n="home.area2Cat">⬡ Chemoinformatics</div>\n          <h3 data-i18n="home.area2Title">Chemical Space &amp; Molecular AI</h3>\n          <p data-i18n="home.area2Desc">Generative models and graph neural networks for molecular formula assignment, toxicity prediction, and chemical space exploration.</p>\n          <a href="research.html" class="highlight-link" data-i18n="common.explore">Explore →</a>',
        ),
        (
            '<div class="highlight-cat">⬡ Environmental Science</div>\n          <h3>DOM &amp; Marine Carbon</h3>\n          <p>Decoding dissolved organic matter complexity in aquatic environments using HR-MS/MS and kinetic deep learning models.</p>\n          <a href="research.html" class="highlight-link">Explore →</a>',
            '<div class="highlight-cat" data-i18n="home.area3Cat">⬡ Environmental Science</div>\n          <h3 data-i18n="home.area3Title">DOM &amp; Marine Carbon</h3>\n          <p data-i18n="home.area3Desc">Decoding dissolved organic matter complexity in aquatic environments using HR-MS/MS and kinetic deep learning models.</p>\n          <a href="research.html" class="highlight-link" data-i18n="common.explore">Explore →</a>',
        ),
        (
            '<div class="highlight-cat">⬡ Machine Learning</div>\n          <h3>GNN &amp; Physics-Informed Models</h3>\n          <p>Graph Transformers, PINNs, and VAE architectures applied to environmental fate modeling, biotransformation, and drug discovery.</p>\n          <a href="research.html" class="highlight-link">Explore →</a>',
            '<div class="highlight-cat" data-i18n="home.area4Cat">⬡ Machine Learning</div>\n          <h3 data-i18n="home.area4Title">GNN &amp; Physics-Informed Models</h3>\n          <p data-i18n="home.area4Desc">Graph Transformers, PINNs, and VAE architectures applied to environmental fate modeling, biotransformation, and drug discovery.</p>\n          <a href="research.html" class="highlight-link" data-i18n="common.explore">Explore →</a>',
        ),
        (
            "<h2>Recent Publications</h2>\n        <a href=\"publications.html\" class=\"see-all\">See all →</a>",
            '<h2 data-i18n="home.pubsTitle">Recent Publications</h2>\n        <a href="publications.html" class="see-all" data-i18n="common.seeAll">See all →</a>',
        ),
    ]
    for a, b in more:
        t = once(t, a, b)

    # status panel keys
    status = [
        ('<span class="status-key">status</span>', '<span class="status-key" data-i18n="home.statusLabel">status</span>'),
        (
            '<span class="status-val status-active"><span class="status-dot"></span>Active PhD Researcher · Year 2</span>',
            '<span class="status-val status-active"><span class="status-dot"></span><span data-i18n="home.statusVal">Active PhD Researcher · Year 2</span></span>',
        ),
        ('<span class="status-key">supervisor</span>', '<span class="status-key" data-i18n="home.supervisorLabel">supervisor</span>'),
        (
            '<span class="status-val">Prof. Manabu Fujii · Institute of Science Tokyo</span>',
            '<span class="status-val" data-i18n="home.supervisorVal">Prof. Manabu Fujii · Institute of Science Tokyo</span>',
        ),
        ('<span class="status-key">institution</span>', '<span class="status-key" data-i18n="home.institutionLabel">institution</span>'),
        (
            '<span class="status-val">Institute of Science Tokyo (IST) — Ookayama Campus</span>',
            '<span class="status-val" data-i18n="home.institutionVal">Institute of Science Tokyo (IST) — Ookayama Campus</span>',
        ),
        ('<span class="status-key">currently</span>', '<span class="status-key" data-i18n="home.currentlyLabel">currently</span>'),
        (
            '<span class="status-val">CRAM-GTransformer: Bidirectional Graph Transformer for Site-Specific and Pathway-Level CRAM Biotransformation</span>',
            '<span class="status-val" data-i18n="home.currentlyVal">CRAM-GTransformer: Bidirectional Graph Transformer for Site-Specific and Pathway-Level CRAM Biotransformation</span>',
        ),
        ('<span class="status-key">funding</span>', '<span class="status-key" data-i18n="home.fundingLabel">funding</span>'),
        (
            '<span class="status-val status-open">AISpread1000 (PI: Prof. Fujii) · ¥5M · Million-scale diverse-DOM generation</span>',
            '<span class="status-val status-open" data-i18n="home.fundingVal">AISpread1000 (PI: Prof. Fujii) · ¥5M · Million-scale diverse-DOM generation</span>',
        ),
        ('<span class="status-key">open_to</span>', '<span class="status-key" data-i18n="home.openToLabel">open_to</span>'),
        (
            '<span class="status-val status-open">Collaborations · Internships · Conference Talks</span>',
            '<span class="status-val status-open" data-i18n="home.openToVal">Collaborations · Internships · Conference Talks</span>',
        ),
        (
            'Get in touch\n          </a>',
            '<span data-i18n="common.getInTouch">Get in touch</span>\n          </a>',
        ),
        (
            '<a href="cram.html" class="status-more-btn">CRAM project →</a>',
            '<a href="cram.html" class="status-more-btn" data-i18n="home.cramProjectBtn">CRAM project →</a>',
        ),
    ]
    for a, b in status:
        t = once(t, a, b)

    # skills tabs
    for old, new in [
        (
            '<button type="button" class="home-skills-tab is-active" role="tab" aria-selected="true" data-skill-tab="compute">Computing</button>',
            '<button type="button" class="home-skills-tab is-active" role="tab" aria-selected="true" data-skill-tab="compute" data-i18n="home.tabCompute">Computing</button>',
        ),
        (
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="ml">ML / AI</button>',
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="ml" data-i18n="home.tabMl">ML / AI</button>',
        ),
        (
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="chem">Chemistry</button>',
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="chem" data-i18n="home.tabChem">Chemistry</button>',
        ),
        (
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="tools">Tools</button>',
            '<button type="button" class="home-skills-tab" role="tab" aria-selected="false" data-skill-tab="tools" data-i18n="home.tabTools">Tools</button>',
        ),
    ]:
        t = once(t, old, new)

    # remove obsolete home.headline if still present as data-i18n without Html
    t = t.replace('data-i18n="home.headline"', 'data-i18n-html="home.headlineHtml"')
    t = t.replace('data-i18n="home.pipe3d"', 'data-i18n-html="home.pipe3dHtml"')

    p.write_text(t, encoding="utf-8")
    print("index ok")


def patch_simple_page(name: str, mapping: list[tuple[str, str]]):
    p = SRC / name
    t = p.read_text(encoding="utf-8")
    for a, b in mapping:
        t = once(t, a, b)
    p.write_text(t, encoding="utf-8")
    print(name, "ok")


def main():
    patch_footer()
    patch_index()

    patch_simple_page(
        "about.html",
        [
            (
                '<div class="page-hero-eyebrow">About · Cheminformatics</div>\n      <h1>Supaporn Klabklaydee</h1>\n      <p class="page-hero-sub">Ph.D. Student · Environmental Chemistry &amp; Cheminformatics · Institute of Science Tokyo · Fujii Lab<br>GNN · Molecular graphs · Ecotoxicity · PFAS · DOM</p>',
                '<div class="page-hero-eyebrow" data-i18n="about.eyebrow">About · Cheminformatics</div>\n      <h1>Supaporn Klabklaydee</h1>\n      <p class="page-hero-sub" data-i18n-html="about.heroSubHtml">Ph.D. Student · Environmental Chemistry &amp; Cheminformatics · Institute of Science Tokyo · Fujii Lab<br>GNN · Molecular graphs · Ecotoxicity · PFAS · DOM</p>',
            ),
            (
                '<span class="section-label">Research Hub</span>\n          <h2>Explore current work</h2>\n          <p>From published GSAT benchmarks to the in-progress CRAM thesis — dive into molecular graphs, toxicity, and biotransformation.</p>',
                '<span class="section-label" data-i18n="about.hubLabel">Research Hub</span>\n          <h2 data-i18n="about.hubTitle">Explore current work</h2>\n          <p data-i18n="about.hubDesc">From published GSAT benchmarks to the in-progress CRAM thesis — dive into molecular graphs, toxicity, and biotransformation.</p>',
            ),
            (
                '<span class="research-hub-badge">PhD · In Progress</span>\n            <strong>CRAM-GTransformer</strong>\n            <span>DOM chemical space &amp; pathway biotransformation</span>',
                '<span class="research-hub-badge" data-i18n="about.hubCramBadge">PhD · In Progress</span>\n            <strong>CRAM-GTransformer</strong>\n            <span data-i18n="about.hubCramDesc">DOM chemical space &amp; pathway biotransformation</span>',
            ),
            (
                '<span class="research-hub-badge">Published</span>\n            <strong>GSAT Model</strong>\n            <span>Multigenerational LC<sub>50</sub> · R² = 0.907</span>',
                '<span class="research-hub-badge" data-i18n="about.hubGsatBadge">Published</span>\n            <strong>GSAT Model</strong>\n            <span data-i18n-html="about.hubGsatDescHtml">Multigenerational LC<sub>50</sub> · R² = 0.907</span>',
            ),
            (
                '<span class="research-hub-badge">Overview</span>\n            <strong>Research Themes</strong>\n            <span>PFAS, DOM, GNN, environmental ML</span>',
                '<span class="research-hub-badge" data-i18n="about.hubThemesBadge">Overview</span>\n            <strong data-i18n="about.hubThemesTitle">Research Themes</strong>\n            <span data-i18n="about.hubThemesDesc">PFAS, DOM, GNN, environmental ML</span>',
            ),
            (
                '<p class="about-affil">Ph.D. Student · Civil &amp; Environmental Engineering<br>Institute of Science Tokyo · Fujii Lab</p>',
                '<p class="about-affil" data-i18n-html="about.affilHtml">Ph.D. Student · Civil &amp; Environmental Engineering<br>Institute of Science Tokyo · Fujii Lab</p>',
            ),
            (
                "            Yokohama, Japan\n          </div>",
                '            <span data-i18n="about.location">Yokohama, Japan</span>\n          </div>',
            ),
            (
                "<h2>Hi, I'm Boat</h2>",
                '<h2 data-i18n="about.hi">Hi, I\'m Boat</h2>',
            ),
            (
                '<h3 class="about-section-title">Current Research</h3>\n          <p class="section-note">Open to new collaborations — click any topic to learn more. Research interests also span other pages of this site.</p>',
                '<h3 class="about-section-title" data-i18n="about.currentTitle">Current Research</h3>\n          <p class="section-note" data-i18n="about.currentNote">Open to new collaborations — click any topic to learn more. Research interests also span other pages of this site.</p>',
            ),
            (
                '<h3 class="about-section-title" id="education">Education</h3>',
                '<h3 class="about-section-title" id="education" data-i18n="about.eduTitle">Education</h3>',
            ),
            (
                '<h3 class="about-section-title">Awards &amp; Honors</h3>',
                '<h3 class="about-section-title" data-i18n="about.awardsTitle">Awards &amp; Honors</h3>',
            ),
            (
                '<h3 class="about-section-title">Internship Experiences</h3>',
                '<h3 class="about-section-title" data-i18n="about.internTitle">Internship Experiences</h3>',
            ),
            (
                '<h3 class="about-section-title">Research Experiences</h3>',
                '<h3 class="about-section-title" data-i18n="about.expTitle">Research Experiences</h3>',
            ),
            (
                '<h3 class="about-section-title">Skills &amp; Expertise</h3>',
                '<h3 class="about-section-title" data-i18n="about.skillsTitle">Skills &amp; Expertise</h3>',
            ),
            (
                '<div class="skill-group-label">Programming Languages</div>',
                '<div class="skill-group-label" data-i18n="about.skillProg">Programming Languages</div>',
            ),
            (
                '<div class="skill-group-label">Libraries &amp; Tools</div>',
                '<div class="skill-group-label" data-i18n="about.skillLibs">Libraries &amp; Tools</div>',
            ),
            (
                '<div class="skill-group-label">Methods</div>',
                '<div class="skill-group-label" data-i18n="about.skillMethods">Methods</div>',
            ),
            (
                '<div class="skill-group-label">Research Domains</div>',
                '<div class="skill-group-label" data-i18n="about.skillDomains">Research Domains</div>',
            ),
        ],
    )

    # about bio paragraphs - more fragile; do separately with regex-ish unique starts
    about = (SRC / "about.html").read_text(encoding="utf-8")
    about = once(
        about,
        "<p>I am a Ph.D. student in <strong>Civil and Environmental Engineering</strong>",
        '<p data-i18n-html="about.bio1Html">I am a Ph.D. student in <strong>Civil and Environmental Engineering</strong>',
    )
    about = once(
        about,
        "<p>With extensive experience in data analysis using <strong>Python, R, and Julia</strong>",
        '<p data-i18n-html="about.bio2Html">With extensive experience in data analysis using <strong>Python, R, and Julia</strong>',
    )
    about = once(
        about,
        "<p>Beyond models, I care about <strong>reproducible scientific software</strong>",
        '<p data-i18n-html="about.bio3Html">Beyond models, I care about <strong>reproducible scientific software</strong>',
    )
    (SRC / "about.html").write_text(about, encoding="utf-8")

    patch_simple_page(
        "research.html",
        [
            (
                '<div class="page-hero-eyebrow">Research</div>\n      <h1>Research Interests</h1>\n      <p class="page-hero-sub">Computational Environmental Science · Machine Learning · Molecular Discovery</p>',
                '<div class="page-hero-eyebrow" data-i18n="research.eyebrow">Research</div>\n      <h1 data-i18n="research.h1">Research Interests</h1>\n      <p class="page-hero-sub" data-i18n="research.heroSub">Computational Environmental Science · Machine Learning · Molecular Discovery</p>',
            ),
            (
                "<p>My work sits at the intersection of <strong>environmental engineering</strong>",
                '<p data-i18n-html="research.introHtml">My work sits at the intersection of <strong>environmental engineering</strong>',
            ),
            (
                '<p class="ri-collab-note">I am actively open to new collaborations — click any topic to learn more and reach out.</p>',
                '<p class="ri-collab-note" data-i18n="research.collabNote">I am actively open to new collaborations — click any topic to learn more and reach out.</p>',
            ),
            (
                '<button class="ri-filter active" data-filter="all">All Topics</button>',
                '<button class="ri-filter active" data-filter="all" data-i18n="research.filterAll">All Topics</button>',
            ),
            (
                '<button class="ri-filter" data-filter="ml">Machine Learning</button>',
                '<button class="ri-filter" data-filter="ml" data-i18n="research.filterMl">Machine Learning</button>',
            ),
            (
                '<button class="ri-filter" data-filter="env">Environmental</button>',
                '<button class="ri-filter" data-filter="env" data-i18n="research.filterEnv">Environmental</button>',
            ),
            (
                '<button class="ri-filter" data-filter="chem">Chemoinformatics</button>',
                '<button class="ri-filter" data-filter="chem" data-i18n="research.filterChem">Chemoinformatics</button>',
            ),
            (
                '<button class="ri-filter" data-filter="bio">Bioinformatics</button>',
                '<button class="ri-filter" data-filter="bio" data-i18n="research.filterBio">Bioinformatics</button>',
            ),
            ("<h3>DOM Transformation</h3>", '<h3 data-i18n="research.c1Title">DOM Transformation</h3>'),
            (
                "<p>Decoding dissolved organic matter structural complexity in aquatic environments using HR-MS/MS and generative models.</p>",
                '<p data-i18n="research.c1Desc">Decoding dissolved organic matter structural complexity in aquatic environments using HR-MS/MS and generative models.</p>',
            ),
            ("<h3>Biotransformation Modeling</h3>", '<h3 data-i18n="research.c2Title">Biotransformation Modeling</h3>'),
            (
                "<p>Multigenerational toxicity prediction using Graph Neural Networks and Graph Transformers for environmental pollutant risk assessment.</p>",
                '<p data-i18n="research.c2Desc">Multigenerational toxicity prediction using Graph Neural Networks and Graph Transformers for environmental pollutant risk assessment.</p>',
            ),
        ],
    )

    # research CTAs - replace all Explore & collaborate
    res = (SRC / "research.html").read_text(encoding="utf-8")
    res = res.replace(
        '<span class="ri-cta">Explore &amp; collaborate →</span>',
        '<span class="ri-cta" data-i18n="research.cta">Explore &amp; collaborate →</span>',
    )
    (SRC / "research.html").write_text(res, encoding="utf-8")

    for page, eyebrow, h1, sub, ns in [
        ("publications.html", "Publications", "Publications", "Peer-reviewed papers, preprints, and first-author contributions in environmental AI and cheminformatics.", "publications"),
        ("talks.html", "Talks", "Talks & Presentations", "Conferences, posters, competitions, and invited research presentations.", "talks"),
        ("projects.html", "Projects", "Projects", "Research software, open-source tools, and funded program work.", "projects"),
        ("cv.html", "Curriculum Vitae", "Curriculum Vitae", "Education, research experience, publications, awards, and skills.", "cv"),
    ]:
        # read actual hero text from file to match
        pass

    # publications
    pub = (SRC / "publications.html").read_text(encoding="utf-8")
    pub = once(
        pub,
        '<div class="page-hero-eyebrow">',
        '<div class="page-hero-eyebrow" data-i18n="publications.eyebrow">',
    )
    # safer targeted
    if 'data-i18n="publications.eyebrow"' not in pub:
        pub = (SRC / "publications.html").read_text(encoding="utf-8")
    # rewrite publications hero block via regex
    pub = re.sub(
        r'(<div class="page-hero-eyebrow")(>)([^<]+)(</div>\s*<h1>)([^<]+)(</h1>\s*<p class="page-hero-sub")(>)',
        r'\1 data-i18n="publications.eyebrow"\2\3\4 data-i18n="publications.h1">\5\6 data-i18n="publications.heroSub"\7',
        pub,
        count=1,
    )
    (SRC / "publications.html").write_text(pub, encoding="utf-8")
    print("publications hero ok")

    for fname, ns in [
        ("talks.html", "talks"),
        ("projects.html", "projects"),
        ("cv.html", "cv"),
        ("cram.html", "cram"),
        ("gsat.html", "gsat"),
    ]:
        html = (SRC / fname).read_text(encoding="utf-8")
        html2 = re.sub(
            r'(<div class="page-hero-eyebrow")(>)([^<]*)(</div>\s*<h1)(>)([^<]*)(</h1>\s*<p class="page-hero-sub")(>)',
            rf'\1 data-i18n="{ns}.eyebrow"\2\3\4 data-i18n="{ns}.h1"\5\6\7 data-i18n="{ns}.heroSub"\8',
            html,
            count=1,
        )
        if html2 == html:
            # try heroSubHtml for gsat
            html2 = re.sub(
                r'(<div class="page-hero-eyebrow")(>)([^<]*)(</div>\s*<h1)(>)([^<]*)(</h1>\s*<p class="page-hero-sub")(>)',
                rf'\1 data-i18n="{ns}.eyebrow"\2\3\4 data-i18n="{ns}.h1"\5\6\7 data-i18n-html="{ns}.heroSubHtml"\8',
                html,
                count=1,
            )
        (SRC / fname).write_text(html2, encoding="utf-8")
        print(fname, "hero patched" if html2 != html else "hero UNCHANGED")

    # CRAM parts
    cram = (SRC / "cram.html").read_text(encoding="utf-8")
    cram = once(cram, '<div class="section-label">Part I</div>', '<div class="section-label" data-i18n="cram.part1">Part I</div>')
    cram = once(
        cram,
        '<h2 class="section-title" style="font-size:clamp(1.3rem,3vw,1.9rem);margin-bottom:6px;">CRAM Generative Model</h2>',
        '<h2 class="section-title" style="font-size:clamp(1.3rem,3vw,1.9rem);margin-bottom:6px;" data-i18n="cram.part1Title">CRAM Generative Model</h2>',
    )
    cram = once(cram, '<div class="section-label">Part II</div>', '<div class="section-label" data-i18n="cram.part2">Part II</div>')
    cram = once(
        cram,
        '<h2 class="section-title" style="font-size:clamp(1.3rem,3vw,1.9rem);margin-bottom:6px;">CRAM-GTransformer</h2>',
        '<h2 class="section-title" style="font-size:clamp(1.3rem,3vw,1.9rem);margin-bottom:6px;" data-i18n="cram.part2Title">CRAM-GTransformer</h2>',
    )
    (SRC / "cram.html").write_text(cram, encoding="utf-8")

    # gsat heroSub should be html
    gsat = (SRC / "gsat.html").read_text(encoding="utf-8")
    gsat = gsat.replace('data-i18n="gsat.heroSub"', 'data-i18n-html="gsat.heroSubHtml"')
    (SRC / "gsat.html").write_text(gsat, encoding="utf-8")

    # CV section titles
    cv = (SRC / "cv.html").read_text(encoding="utf-8")
    for en, key in [
        (">Education</h2>", ' data-i18n="cv.edu">Education</h2>'),
        (">Research Experience</h2>", ' data-i18n="cv.exp">Research Experience</h2>'),
        (">Publications</h2>", ' data-i18n="cv.pubs">Publications</h2>'),
        (">Selected Presentations &amp; Competitions</h2>", ' data-i18n="cv.pres">Selected Presentations &amp; Competitions</h2>'),
    ]:
        if en in cv and f'data-i18n="cv.' not in cv[cv.find(en) - 40 : cv.find(en)]:
            cv = cv.replace(f"class=\"cv-section-title\"{en}", f'class="cv-section-title"{key}', 1)
            # try alternate
            cv = cv.replace(f"cv-section-title\"{en}", f'cv-section-title"{key}', 1)
    (SRC / "cv.html").write_text(cv, encoding="utf-8")
    print("cv sections attempted")


if __name__ == "__main__":
    main()

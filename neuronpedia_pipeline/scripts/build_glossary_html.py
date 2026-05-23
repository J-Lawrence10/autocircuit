"""Convert docs/papers/GLOSSARY.md to docs/glossary.html (top-level docs/).

The generated HTML reuses the Bulma scaffolding (theme variables, theme toggle,
hero, footer) from docs/cross-domain-circuits.html and exposes stable anchor
IDs for the eleven glossary sections so the deep-link icons in the paper page
can jump straight to the right entry.

Anchor mapping (override the default markdown slugs):
  Jaccard Similarity                                  -> jaccard-similarity
  Activation Energy                                   -> activation-energy
  Bottleneck Tax                                      -> bottleneck-tax
  Architecture Dominance                              -> architecture-dominance
  Universal Bottleneck Features                       -> universal-bottleneck-features
  Traceback Graphing                                  -> traceback-graphing
  Three-Tier Dissociation                             -> three-tier-dissociation
  Cosine Similarity on Energy Profiles                -> cosine-similarity-on-energy-profiles
  Is Energy Finite? (Addressing the Metaphor)         -> is-energy-finite-addressing-the-metaphor
  Steering Experiments: How Features Were Selected    -> steering-experiments
  Direct Logit Attribution: How the Output Token...   -> direct-logit-attribution
"""

from __future__ import annotations

import io
import re
import sys
from pathlib import Path

import markdown

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "docs" / "papers" / "GLOSSARY.md"
HTML_OUT = ROOT.parent / "docs" / "glossary.html"

# Anchor overrides keyed by the EXACT H2 heading text in GLOSSARY.md.
ANCHOR_OVERRIDES: dict[str, str] = {
    "Jaccard Similarity": "jaccard-similarity",
    "Activation Energy": "activation-energy",
    "Bottleneck Tax": "bottleneck-tax",
    "Architecture Dominance": "architecture-dominance",
    "Universal Bottleneck Features": "universal-bottleneck-features",
    "Traceback Graphing": "traceback-graphing",
    "Three-Tier Dissociation": "three-tier-dissociation",
    "Cosine Similarity on Energy Profiles": "cosine-similarity-on-energy-profiles",
    "Is Energy Finite? (Addressing the Metaphor)": "is-energy-finite-addressing-the-metaphor",
    "Steering Experiments: How Features Were Selected": "steering-experiments",
    "Direct Logit Attribution: How the Output Token is Chosen": "direct-logit-attribution",
}


def convert_body(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "attr_list"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    html = md.convert(md_text)
    # Override H2 anchor IDs for the seven glossary sections so they match the
    # deep-link targets in cross-domain-circuits.html.
    for heading, anchor in ANCHOR_OVERRIDES.items():
        pattern = re.compile(
            r'(<h2)\b[^>]*?id="[^"]*"([^>]*)>(\s*)' + re.escape(heading) + r"(\s*</h2>)",
            re.IGNORECASE,
        )
        html, n = pattern.subn(
            rf'\1 id="{anchor}"\2>\3{heading}\4', html, count=1
        )
        if n == 0:
            print(f"WARNING: heading not found: {heading!r}")
    return html


HEAD_AND_HERO = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Glossary: Cross-Domain Circuit Analysis</title>
<meta name="description" content="Plain-language definitions of Jaccard similarity, activation energy, bottleneck tax, cosine similarity on energy profiles, steering experiments, and direct logit attribution.">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0d1117; --bg2: #161b22; --bg3: #21262d; --border: #30363d;
  --text: #c9d1d9; --text-muted: #8b949e; --link: #58a6ff;
  --hero-bg: #0d1117; --section-bg: #0d1117; --footer-bg: #161b22;
  --code-bg: #161b22; --table-head: #161b22; --table-even: rgba(22,27,34,0.6);
  --hr-color: #30363d;
}
[data-theme="light"] {
  --bg: #ffffff; --bg2: #f6f8fa; --bg3: #eaeef2; --border: #d0d7de;
  --text: #1f2328; --text-muted: #57606a; --link: #0969da;
  --hero-bg: #ffffff; --section-bg: #ffffff; --footer-bg: #f6f8fa;
  --code-bg: #eaeef2; --table-head: #f6f8fa; --table-even: #f6f8fa;
  --hr-color: #ededed;
}
html { font-size: 12pt; }
body {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--text);
  background: var(--bg);
  transition: background 0.2s ease, color 0.2s ease;
}
code, pre { font-family: 'DM Mono', monospace !important; background: var(--code-bg) !important; color: var(--link) !important; }
pre { padding: 0.75rem; border-radius: 6px; overflow-x: auto; }
a { color: var(--link); }
a:hover { opacity: 0.8; }
.hero { background: var(--hero-bg) !important; }
.section { background: var(--section-bg) !important; }
.footer { background: var(--footer-bg) !important; color: var(--text-muted); }
.footer a { color: var(--link); }
.title { color: var(--text) !important; }
.content { color: var(--text); }
.content h2, .content h3, .content h4 { color: var(--text) !important; }
.content h2 { border-bottom: 1px solid var(--hr-color); padding-bottom: 0.3em; margin-top: 2em; }
hr { background-color: var(--hr-color); border: none; height: 1px; }
table { color: var(--text) !important; background: transparent !important; }
table th { background: var(--table-head) !important; color: var(--text) !important; border-color: var(--border) !important; }
table td { border-color: var(--border) !important; }
table tr:nth-child(even) td { background: var(--table-even) !important; }
blockquote { border-left: 3px solid var(--link); padding-left: 1em; color: var(--text-muted); margin: 1em 0; }

#theme-toggle {
  position: fixed; top: 1rem; right: 1rem; z-index: 1000;
  background: var(--bg2); color: var(--text);
  border: 1px solid var(--border); padding: 0.4rem 0.8rem;
  border-radius: 20px; cursor: pointer; font-size: 0.85rem;
  transition: all 0.2s ease;
}
#theme-toggle:hover { border-color: var(--link); color: var(--link); }

.back-link {
  display: inline-block; margin-bottom: 1rem; font-size: 0.95rem;
  color: var(--text-muted); text-decoration: none;
}
.back-link:hover { color: var(--link); }
.back-link i { margin-right: 0.4rem; }
</style>
</head>
<body>

<!-- THEME TOGGLE -->
<button id="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">
  <span id="theme-icon">☀️</span>
  <span id="theme-label">Light mode</span>
</button>
<script>
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('theme-icon').textContent  = isDark ? '🌙' : '☀️';
  document.getElementById('theme-label').textContent = isDark ? 'Dark mode' : 'Light mode';
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
}
(function() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  document.addEventListener('DOMContentLoaded', function() {
    const isDark = saved === 'dark';
    document.getElementById('theme-icon').textContent  = isDark ? '☀️' : '🌙';
    document.getElementById('theme-label').textContent = isDark ? 'Light mode' : 'Dark mode';
  });
})();
</script>

<!-- HERO -->
<section class="hero">
  <div class="hero-body" style="padding: 3rem 1.5rem 0.5rem 1.5rem;">
    <div class="container is-max-desktop">
      <a href="cross-domain-circuits.html" class="back-link"><i class="fa-solid fa-arrow-left"></i>Back to paper</a>
      <h1 class="title is-2">Glossary</h1>
      <p class="subtitle is-5" style="color: var(--text-muted);">Plain-language definitions of key concepts used in the Cross-Domain Circuit Analysis paper.</p>
    </div>
  </div>
</section>

<hr>

<!-- BODY -->
<section class="section">
  <div class="container is-max-desktop">
    <div class="content">
"""

FOOTER = """    </div>
  </div>
</section>

<!-- FOOTER -->
<footer class="footer">
  <div class="container">
    <div class="columns is-centered">
      <div class="column is-8">
        <div class="content has-text-centered">
          <p><a href="cross-domain-circuits.html">Return to the Cross-Domain Circuit Analysis paper</a>.</p>
        </div>
      </div>
    </div>
  </div>
</footer>

</body>
</html>
"""


def main() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    body = convert_body(md_text)
    HTML_OUT.write_text(HEAD_AND_HERO + body + FOOTER, encoding="utf-8")
    print(f"Wrote {HTML_OUT} ({HTML_OUT.stat().st_size} bytes)")
    # Sanity: ensure each desired anchor ID exists in output.
    html = HTML_OUT.read_text(encoding="utf-8")
    for anchor in ANCHOR_OVERRIDES.values():
        if f'id="{anchor}"' in html:
            print(f"  anchor present: #{anchor}")
        else:
            print(f"  MISSING anchor: #{anchor}")


if __name__ == "__main__":
    main()

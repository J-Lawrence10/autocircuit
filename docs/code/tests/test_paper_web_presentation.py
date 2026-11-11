"""Web-only presentation checks. Numerical data and the authored text stay intact."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from paper_web_presentation import enhance_document, figure_markup

SHARE = ROOT/'paper_share' if (ROOT/'paper_share').exists() else ROOT.parent


def test_full_caption_is_retained_once_and_svg_replaces_png():
    legend = '<p><strong>Figure 2. Same-fact comparison.</strong> Mean 0.170; n=8. A &amp; B.</p>'
    source = ('<html><body><p>Before.</p><figure><img src="../figures/test.png" '
              'alt="Figure 2: Same-fact comparison" /><figcaption aria-hidden="true">'
              'Figure 2: Same-fact comparison</figcaption></figure>\n' + legend + '<p>After.</p></body></html>')
    actual, count = enhance_document(source, '../')
    assert count == 1
    assert actual.count(legend) == 1
    assert '<img src="../figures/test.svg"' in actual
    assert 'href="../figures/test.png" download' in actual
    assert '<p>Before.</p>' in actual and '<p>After.</p>' in actual
    assert 'aria-hidden="true"' not in actual
    assert 'src="../figure-viewer.js"' in actual


def test_figure_links_are_usable_without_javascript():
    markup = figure_markup('a.svg', 'a.png', 'A & B', '<p>Full legend.</p>', 'S1')
    assert markup.count('href="a.svg"') == 3
    assert 'alt="A &amp; B"' in markup
    assert 'id="figure-s1"' in markup
    assert 'aria-labelledby="figure-s1-label"' in markup


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []
        self.ids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            self.sources.append(attrs.get('src'))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


def test_all_web_figures_use_existing_vectors_and_unique_ids():
    for filename, count in [('manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.html', 16),
                            ('figures/index.html', 16), ('index.html', 1)]:
        path = SHARE/filename
        content = path.read_text(encoding='utf-8')
        parser = Images()
        parser.feed(content)
        assert len(parser.sources) == count
        assert len(parser.ids) == len(set(parser.ids))
        for src in parser.sources:
            assert src.endswith('.svg')
            assert (path.parent/src).exists()
        assert content.count('class="paper-figure"') == count
        assert content.count('class="figure-caption"') == count
        assert content.count('class="figure-enlarge"') == count


def test_all_sixteen_authored_legends_are_in_the_manuscript_html():
    md = (SHARE/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md').read_text(encoding='utf-8')
    document = (SHARE/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.html').read_text(encoding='utf-8')
    labels = re.findall(r'\*\*Figure (S?\d+)\.', md)
    assert len(labels) == 16
    for label in labels:
        assert document.count(f'<strong>Figure {label}.') == 1


def test_viewer_supports_keyboard_mobile_and_print():
    css = (SHARE/'review.css').read_text(encoding='utf-8')
    js = (SHARE/'figure-viewer.js').read_text(encoding='utf-8')
    assert '@media (max-width: 640px)' in css
    assert '@media print' in css
    assert 'focus-visible' in css
    assert "dialog.showModal()" in js
    assert "origin?.focus" in js
    assert "dialog.addEventListener('close'" in js
    assert all(f'data-scale="{scale}"' in js for scale in ['fit', '1', '1.5', '2'])

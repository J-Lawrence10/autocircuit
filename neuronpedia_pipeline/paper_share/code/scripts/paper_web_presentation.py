"""Present the unchanged paper artwork as crisp, accessible web figures."""
import html
import re


def figure_markup(svg, png, title, caption, key):
    """Keep captions verbatim; use the existing SVG, with a no-JS full-size link."""
    esc = html.escape
    label = f'Figure {key}' if key != 'overview' else 'Paper overview'
    anchor = f'figure-{key.lower()}'
    return (
        f'<figure class="paper-figure" id="{anchor}" aria-labelledby="{anchor}-label">\n'
        '<div class="figure-toolbar">'
        f'<span class="figure-label" id="{anchor}-label">{label}</span>'
        '<div class="figure-actions">'
        f'<a class="figure-enlarge" href="{esc(svg)}" data-figure-open '
        f'aria-label="Enlarge {esc(label)}">Enlarge figure</a>'
        f'<a href="{esc(svg)}" download>SVG</a>'
        f'<a href="{esc(png)}" download>PNG</a></div></div>\n'
        f'<a class="figure-artwork" href="{esc(svg)}" data-figure-open '
        f'aria-label="Enlarge {esc(label)}: {esc(title)}">'
        f'<img src="{esc(svg)}" alt="{esc(title)}" loading="lazy" decoding="async" />'
        '</a>\n'
        f'<figcaption class="figure-caption">{caption}</figcaption>\n</figure>'
    )


def enhance_document(document, asset_prefix):
    """Replace Pandoc's raster figures, retaining the full authored legend."""
    pattern = re.compile(
        r'<figure>\s*<img\s+src="(?P<src>[^"]+\.png)"\s+'
        r'alt="(?P<alt>[^"]*)"\s*/?>\s*'
        r'<figcaption[^>]*>.*?</figcaption>\s*</figure>'
        r'(?:\s*(?P<legend><p><strong>Figure\s+S?\d+\..*?</p>))?',
        re.S,
    )

    def replace(match):
        png = html.unescape(match['src'])
        title = html.unescape(match['alt'])
        number = re.match(r'Figure\s+(S?\d+)\s*:', title)
        key = number[1] if number else 'overview'
        caption = match['legend'] or f'<p>{html.escape(title)}</p>'
        return figure_markup(png[:-4]+'.svg', png, title, caption, key)

    document, count = pattern.subn(replace, document)
    expected = len(re.findall(r'<figure>', document))
    assert expected == 0, 'An unconverted figure needs review'
    return with_viewer(document, asset_prefix), count


def with_viewer(document, asset_prefix):
    return document.replace(
        '</body>',
        f'<script defer src="{asset_prefix}figure-viewer.js"></script>\n</body>',
    )

"""Three presentation mockups; no model calls or changes to the main figures."""
from pathlib import Path
import hashlib
import html
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/model_extension/figure1_mockups_20261006'
INK, MUTED, BLUE, GREEN, RUST = '#213747', '#667782', '#236C88', '#387765', '#A4532B'
RULE, PALE = '#D6E0E5', '#F2F6F8'
TITLE = 'Three tests ask what similar graphs can tell us'
MODELS = ['Gemma-2-2B · Qwen3-1.7B · Qwen3-4B', 'Qwen3-4B', 'Qwen3-4B']
SCOPE = ['Original questions and controls', '48 graphs · six country pairs', '16 graphs · one country pair · two answer formats']
HEADINGS = ['Reword a factual question', 'Change the correct A/B answer', 'Examine selected wrong answers']
QUESTIONS = [
    'Do reworded questions about the same fact\nshare more features than other-fact questions?',
    'Do same-fact questions still share more features\nwhen the correct A/B answer changes?',
    'Does an error graph resemble the intended\nquestion or a response giving the same answer?']
FILES = []


def txt(ax, x, y, s, size=11, bold=False, color=INK, ha='center', **kw):
    return ax.text(x, y, s, ha=ha, va='center', multialignment=ha, fontsize=size,
                   color=color, fontweight='bold' if bold else 'normal', linespacing=1.4, **kw)


def line(ax, x0, x1, y, color=RULE, lw=.8):
    ax.plot([x0, x1], [y, y], color=color, lw=lw, clip_on=False)


def box(ax, x, y, w, h, fill='white', edge=RULE):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.006,rounding_size=0.012',
                              facecolor=fill, edgecolor=edge, lw=.8))


def arrow(ax, start, end):
    ax.annotate('', xy=end, xytext=start, arrowprops=dict(arrowstyle='-|>', color='#8DA2AF', lw=1.0, mutation_scale=10))


def canvas(width=16.5, height=9):
    fig = plt.figure(figsize=(width, height), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    txt(ax, .035, .955, TITLE, 20, True, ha='left')
    return fig, ax


def footer(ax, full_prompt=False):
    line(ax, .035, .965, .098)
    txt(ax, .035, .070, 'Shared graph features do not, by themselves, establish a correct answer.', 11, True, ha='left')
    note = ('Panel C shows the recorded user prompt with line breaks only; chat-template tokens are omitted. Other examples and control questions are shortened.'
            if full_prompt else 'Shortened examples: gold is the chemical element (development); A/B choices use a pilot pair; errors are selected collected cases.')
    txt(ax, .035, .040, note, 8.7, color=MUTED, ha='left')
    txt(ax, .035, .020, 'Diagrams show comparisons, not causal pathways. Colors identify labeled categories, not measured amounts. Full details remain in the figure caption.', 8.5, color=MUTED, ha='left')


def save(fig, stem, label, description):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # Catch text that would be cut off at the image boundary.
    for ax in fig.axes:
        for t in ax.texts:
            b = t.get_window_extent(renderer)
            assert b.x0 >= 0 and b.x1 <= fig.bbox.width and b.y0 >= 0 and b.y1 <= fig.bbox.height, t.get_text()
    for ext in ['png', 'svg']:
        fig.savefig(OUT/f'{stem}.{ext}', dpi=220, facecolor='white')
    FILES.append(dict(stem=stem, label=label, description=description))
    plt.close(fig)


def journal():
    fig, ax = canvas(height=9.3)
    centers = [.182, .500, .818]
    for divider in [.341, .659]:
        ax.plot([divider, divider], [.142, .89], color=RULE, lw=.9)
    for i, x in enumerate(centers):
        txt(ax, x, .877, chr(97+i), 12, True, BLUE)
        txt(ax, x, .838, HEADINGS[i], 12.3, True)
        txt(ax, x-.137, .792, 'Models Tested:', 8.7, True, ha='left')
        txt(ax, x-.137, .767, MODELS[i], 8.7, color=MUTED, ha='left')
        txt(ax, x, .727, SCOPE[i], 8.7, color=MUTED)
        line(ax, x-.132, x+.132, .698)
        txt(ax, x, .671, 'STARTING EXAMPLE', 8.3, True, BLUE)
        line(ax, x-.132, x+.132, .503)
        txt(ax, x, .478, 'COMPARE WITH', 8.3, True, BLUE)
        line(ax, x-.132, x+.132, .235, GREEN, 1.6)
        txt(ax, x, .208, 'WHAT WE ASK', 8.3, True, GREEN)
        txt(ax, x, .165, QUESTIONS[i], 10.2, True)

    txt(ax, centers[0], .615, '“The chemical symbol\nfor gold is ...”', 15, family='DejaVu Serif', style='italic')
    txt(ax, centers[0], .549, 'Expected answer: Au', 11, color=BLUE)
    txt(ax, centers[0], .435, 'Same fact, reworded', 10.2, True)
    txt(ax, centers[0], .402, '“Gold has the chemical symbol ...” → Au', 10)
    txt(ax, centers[0], .359, 'Other fact', 10.2, True)
    txt(ax, centers[0], .328, '“Iron has the chemical symbol ...” → Fe', 10)
    txt(ax, centers[0], .286, 'Made-up name: “...zorium...”', 10.2)

    txt(ax, centers[1], .639, 'A: Paris. B: Berlin.', 11, True)
    txt(ax, centers[1], .594, '“For France rather than Germany,\nwhat is the capital?”', 12, family='DejaVu Serif', style='italic')
    txt(ax, centers[1], .542, 'Correct answer: A', 11, color=BLUE)
    txt(ax, centers[1], .435, 'Same fact, changed answer letter', 10.2, True)
    txt(ax, centers[1], .402, 'A: Berlin. B: Paris. Ask about France → B', 9.8)
    txt(ax, centers[1], .359, 'Different fact, same answer letter', 10.2, True)
    txt(ax, centers[1], .328, 'A: Berlin. B: Paris. Ask about Germany → A', 9.8)
    txt(ax, centers[1], .281, 'Reword too: “What is the capital for France\nrather than Germany?”', 9.4)

    txt(ax, centers[2], .644, 'Countries: France, Germany. A: Berlin. B: Paris.', 9.2)
    txt(ax, centers[2], .595, '“The first country, not the second”\n→ Berlin (wrong)', 12, family='DejaVu Serif', style='italic')
    txt(ax, centers[2], .542, 'Capital-name response', 10, color=MUTED)
    txt(ax, centers[2], .427, 'Correct response to the intended country', 10, True)
    txt(ax, centers[2], .392, '“Capital for France?” → Paris', 11)
    txt(ax, centers[2], .336, 'Correct response giving the same answer', 10, True)
    txt(ax, centers[2], .301, '“Capital for Germany?” → Berlin', 11)
    txt(ax, centers[2], .261, 'Country list and A/B choices stay fixed.', 8.8, color=MUTED)
    footer(ax)
    save(fig, 'option_a_editorial', 'A · Minimal editorial',
         'Light dividers, large example prompts, and no heavy boxes. A quieter, text-led journal layout.')


def lanes():
    fig, ax = canvas(width=17.5, height=10.2)
    for x, title in [(.347, 'STARTING EXAMPLE'), (.619, 'COMPARISONS'), (.876, 'WHAT WE ASK')]:
        txt(ax, x, .891, title, 9, True, BLUE)
    starts = [
        'About the element gold\n\n“The chemical symbol for gold is ...”\n\nExpected answer: Au',
        'A: Paris. B: Berlin.\n\n“For France rather than Germany,\nwhat is the capital?”\n\nCorrect answer: A',
        'Countries: France, Germany.\nA: Berlin. B: Paris.\n\n“Capital for the first country,\nnot the second?”\n→ Berlin (wrong)']
    comparisons = [
        'Same fact, reworded\n“Gold has the chemical symbol ...” → Au\n\nOther fact\n“Iron has the chemical symbol ...” → Fe\n\nMade-up name: “...zorium...”',
        'Same fact, changed letter\nA: Berlin. B: Paris. France → B\n\nDifferent fact, same letter\nA: Berlin. B: Paris. Germany → A\n\nAlso change the question wording.',
        'Correct response to intended country\n“Capital for France?” → Paris\n\nCorrect response with the same answer\n“Capital for Germany?” → Berlin\n\nCountry list and choices stay fixed.']
    prompts = [
        'More shared features\nfor the same fact?',
        'Do same-fact questions\nstill share more features\nwhen the A/B answer changes?',
        'Does similarity follow\nthe intended question\nor the produced answer?']
    for i, y in enumerate([.750, .502, .254]):
        box(ax, .035, y-.108, .930, .216, '#F7F9FA', edge='#E5EBEF')
        ax.plot([.206, .206], [y-.085, y+.085], color=RULE, lw=.8)
        txt(ax, .056, y+.080, f'{chr(97+i)}', 16, True, BLUE, ha='left')
        title = ['Reword a factual\nquestion', 'Change the correct\nA/B answer', 'Examine selected\nwrong answers'][i]
        txt(ax, .118, y+.044, title, 12, True)
        txt(ax, .050, y-.011, 'Models Tested:', 8.7, True, ha='left')
        models = 'Gemma-2-2B\nQwen3-1.7B · Qwen3-4B' if i == 0 else MODELS[i]
        txt(ax, .050, y-.040, models, 8.4, color=MUTED, ha='left')
        scope = ['Original questions\nand controls', '48 graphs · six country pairs', '16 graphs · one country pair\nTwo answer formats'][i]
        txt(ax, .050, y-.080, scope, 8.2, color=MUTED, ha='left')
        txt(ax, .347, y, starts[i], 10.4)
        arrow(ax, (.469, y), (.485, y))
        txt(ax, .619, y, comparisons[i], 9.7)
        arrow(ax, (.746, y), (.765, y))
        txt(ax, .871, y, prompts[i], 12, True, GREEN)
    footer(ax)
    save(fig, 'option_b_experiment_rows', 'B · Horizontal experiment rows',
         'One experiment per row, read left to right. Consistent columns separate the example, comparison, and question.')


def diagram():
    fig, ax = canvas(width=17, height=9.5)
    centers = [.182, .500, .818]
    for i, x in enumerate(centers):
        txt(ax, x-.139, .877, chr(97+i), 13, True, BLUE, ha='left')
        txt(ax, x, .838, HEADINGS[i], 12, True)
        txt(ax, x-.139, .797, 'Models Tested:', 8.5, True, ha='left')
        txt(ax, x-.139, .770, MODELS[i], 8.5, color=MUTED, ha='left')
        txt(ax, x, .732, SCOPE[i], 8.5, color=MUTED)
        line(ax, x-.139, x+.139, .706)
        line(ax, x-.139, x+.139, .240, GREEN, 1.4)
        txt(ax, x, .214, 'WHAT WE ASK', 8.5, True, GREEN)
        txt(ax, x, .170, QUESTIONS[i], 10, True)

    # A: the three comparison types branch from one starting question.
    box(ax, .065, .595, .234, .088, PALE)
    txt(ax, .182, .643, '“The chemical symbol for gold is ...”', 10.4)
    txt(ax, .182, .616, 'Expected answer: Au', 9.5, True, BLUE)
    labels = [('Same fact', '“Gold has the chemical symbol ...” → Au'),
              ('Other fact', '“Iron has the chemical symbol ...” → Fe'),
              ('Made-up name', '“The chemical symbol for zorium is ...”')]
    ax.plot([.058, .058], [.329, .570], color='#A6B7C1', lw=.9)
    ax.plot([.058, .182, .182], [.570, .570, .585], color='#A6B7C1', lw=.9)
    for y, (label, prompt) in zip([.509, .419, .329], labels):
        box(ax, .080, y-.037, .237, .074)
        arrow(ax, (.058, y), (.076, y))
        txt(ax, .1985, y+.015, label, 9, True, BLUE)
        txt(ax, .1985, y-.014, prompt, 9)

    # B: letters in the grid explicitly demonstrate answer remapping.
    txt(ax, .50, .670, '“For France rather than Germany,\nwhat is the capital?”', 11)
    txt(ax, .50, .612, 'Change the country asked about and the A/B choices', 8.8, color=MUTED)
    txt(ax, .461, .553, 'A: Paris\nB: Berlin', 9.5, True)
    txt(ax, .563, .553, 'A: Berlin\nB: Paris', 9.5, True)
    for r, (country, y) in enumerate([('France', .465), ('Germany', .371)]):
        txt(ax, .364, y, country, 9.6, ha='left')
        for c, x in enumerate([.461, .563]):
            letter = [['A', 'B'], ['B', 'A']][r][c]
            box(ax, x-.046, y-.039, .092, .078, '#EAF3F6' if letter == 'A' else '#F4EFE8', edge='white')
            txt(ax, x, y, letter, 22, True, BLUE if letter=='A' else RUST)
    txt(ax, .50, .288, 'Letters are correct answers, not measurements.\nAlso vary wording while keeping the available words.', 8.8, color=MUTED)

    # C: verbatim user text; only display line breaks differ from the saved prompt.
    jobs = json.loads((ROOT/'data/model_extension/failure_case_graphs_v1/jobs.json').read_text(encoding='utf-8'))
    job = next(j for j in jobs if j['job_id'] == 'f0m1p0w0_ordinal_capital')
    audit = json.loads((ROOT/'data/model_extension/failure_case_graphs_v1/analysis/results.json').read_text(encoding='utf-8'))
    observed = next(a for a in audit['audits'] if a['job_id'] == job['job_id'])
    prompt = ('Reply with only the capital name.\nA: Berlin. B: Paris.\nCountries: France, Germany.\n'
              'Question: what is the capital for the\nfirst country, not the second? Answer:')
    assert ' '.join(prompt.split()) == ' '.join(job['plain_prompt'].split())
    assert observed['observed'] == 'Berlin' and observed['expected'] == 'Paris' and not observed['correct']
    box(ax, .692, .460, .252, .222, '#FBF3EF', edge='#EBD5C9')
    txt(ax, .818, .660, 'RECORDED USER PROMPT', 8.7, True, RUST)
    txt(ax, .818, .586, prompt, 10.2)
    txt(ax, .818, .497, 'Model output: Berlin (wrong)', 12, True, RUST)
    txt(ax, .818, .473, 'Correct answer: Paris', 9.5, True)
    for x in [.750, .888]:
        arrow(ax, (.818, .447), (x, .402))
    for x, title, body in [(.750, 'Intended country', '“Capital for France?”\nParis'),
                           (.888, 'Same produced answer', '“Capital for Germany?”\nBerlin')]:
        box(ax, x-.061, .300, .122, .090, PALE)
        txt(ax, x, .373, title, 8.6, True, BLUE)
        txt(ax, x, .331, body, 9.5)
    txt(ax, .818, .268, 'Both comparison responses are correct.\nCountry list and A/B choices stay fixed.', 8.5, color=MUTED)
    footer(ax, full_prompt=True)
    save(fig, 'option_c_comparison_diagrams', 'C · Diagram-first comparisons',
         'A branching comparison, an A/B answer grid, and the actual recorded failure prompt with its two controls. Panel C preserves the user text verbatim, with line breaks added; chat-template tokens are omitted.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans', 'svg.fonttype':'none'})
    journal(); lanes(); diagram()
    intro = ('Three design mockups for Figure 1. These are presentation alternatives, not new results. '
             'Most examples are shortened; option C now shows the full recorded user prompt for the failure case. The existing main figure and full caption are unchanged.')
    sections = ''.join(f'<section id="{f["stem"]}"><h2>{html.escape(f["label"])}</h2><p>{html.escape(f["description"])}</p>'
                       f'<a href="{f["stem"]}.png"><img src="{f["stem"]}.png" alt="{html.escape(f["label"])}"></a>'
                       f'<p><a href="{f["stem"]}.svg">Editable SVG</a> · <a href="{f["stem"]}.png">Full-size PNG</a></p></section>' for f in FILES)
    (OUT/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Figure 1 layout options</title>'
        '<style>body{max-width:1600px;margin:32px auto;padding:0 28px;font:17px/1.55 system-ui;color:#213747;background:#f5f7f8}'
        'section{margin:36px 0 60px}img{width:100%;height:auto;background:white;border:1px solid #d6e0e5}h1,h2{line-height:1.2}'
        'p{max-width:1000px}a{color:#236c88}</style><h1>Figure 1: three layout directions</h1><p>'+html.escape(intro)+'</p>'
        '<p><a href="../paper_figures_plain_language_20261006/index.html">Current figure and full caption</a></p>'+sections+'</html>', encoding='utf-8')
    sources = [ROOT/'config/paper_control_manifest.csv', ROOT/'data/model_extension/matched_choice_chat_v2/jobs.json',
               ROOT/'data/model_extension/failure_case_graphs_v1/jobs.json',
               ROOT/'data/model_extension/failure_case_graphs_v1/analysis/results.json', ROOT/'scripts/build_outline_figures_v2.py']
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = dict(figures=FILES, source_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources},
                    script_sha256=sha(Path(__file__)), notes=[intro, 'Centered text inside boxes; model labels remain explicit.'],
                    output_hashes={p.name:sha(p) for p in OUT.iterdir() if p.suffix in ['.png','.svg','.html']})
    (OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(OUT/'index.html')


if __name__ == '__main__':
    main()

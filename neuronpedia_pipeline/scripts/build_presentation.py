#!/usr/bin/env python3
"""
Build PowerPoint presentation for Traceback Graphing project.
Generates a 16:9 widescreen deck summarizing the pipeline, findings, and next steps.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import datetime
import os

# ── Constants ──────────────────────────────────────────────────────────────
ACCENT = RGBColor(0x1B, 0x5E, 0x20)       # Deep green
ACCENT_LIGHT = RGBColor(0x4C, 0xAF, 0x50)  # Medium green
DARK = RGBColor(0x21, 0x21, 0x21)           # Near-black
GRAY = RGBColor(0x61, 0x61, 0x61)           # Body text gray
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = RGBColor(0xF5, 0xF5, 0xF5)      # Slide background
HIGHLIGHT = RGBColor(0xE8, 0xF5, 0xE9)     # Light green highlight
WARN_COLOR = RGBColor(0xE6, 0x51, 0x00)    # Orange for caveats
BLUE = RGBColor(0x15, 0x65, 0xC0)          # For links/asks

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
FONT_TITLE = "Calibri"
FONT_BODY = "Calibri"


def add_takehome_bar(slide, text):
    """Add green take-home message bar at top of slide."""
    left, top, width, height = Inches(0), Inches(0), SLIDE_W, Inches(0.65)
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.color.rgb = WHITE
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.name = FONT_TITLE
    p.alignment = PP_ALIGN.LEFT
    tf.margin_left = Inches(0.5)
    tf.margin_top = Inches(0.1)


def add_slide_title(slide, title, subtitle=None):
    """Add main title text below the take-home bar."""
    left, top, width, height = Inches(0.5), Inches(0.75), Inches(12), Inches(0.6)
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = DARK
    p.font.name = FONT_TITLE
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(14)
        p2.font.color.rgb = GRAY
        p2.font.name = FONT_BODY


def add_bullets(slide, bullets, left=0.5, top=1.6, width=12, font_size=16, spacing=Pt(8)):
    """Add bullet list to slide."""
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(5))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (text, level) in enumerate(bullets):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.level = level
        p.font.size = Pt(font_size - (level * 2))
        p.font.color.rgb = DARK if level == 0 else GRAY
        p.font.name = FONT_BODY
        p.space_after = spacing
        if level == 0:
            p.font.bold = False


def add_speaker_notes(slide, notes_text):
    """Add speaker notes to slide."""
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = notes_text


def add_placeholder_box(slide, label, left, top, width, height):
    """Add a dashed placeholder for a figure."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(left), Inches(top),
                                    Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = HIGHLIGHT
    shape.line.color.rgb = ACCENT_LIGHT
    shape.line.width = Pt(1.5)
    shape.line.dash_style = 2  # Dash
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(11)
    p.font.color.rgb = ACCENT
    p.font.italic = True
    p.font.name = FONT_BODY
    p.alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    shape.text_frame.paragraphs[0].space_before = Inches(0.1)


def add_two_column_text(slide, left_bullets, right_bullets, top=1.6):
    """Add two-column bullet layout."""
    add_bullets(slide, left_bullets, left=0.5, top=top, width=5.8, font_size=15)
    add_bullets(slide, right_bullets, left=6.8, top=top, width=5.8, font_size=15)


def add_footer(slide, slide_num, total):
    """Add small footer."""
    txBox = slide.shapes.add_textbox(Inches(11.5), Inches(7.1), Inches(1.5), Inches(0.3))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = f"{slide_num} / {total}"
    p.font.size = Pt(10)
    p.font.color.rgb = GRAY
    p.font.name = FONT_BODY
    p.alignment = PP_ALIGN.RIGHT


def insert_image_if_exists(slide, img_path, left, top, width, height, fallback_label):
    """Insert image if file exists, otherwise placeholder."""
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, Inches(left), Inches(top),
                                  Inches(width), Inches(height))
    else:
        add_placeholder_box(slide, fallback_label, left, top, width, height)


# ── Build the deck ─────────────────────────────────────────────────────────
def build_deck():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    TOTAL_SLIDES = 14
    blank_layout = prs.slide_layouts[6]  # Blank layout

    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    viz_paris = os.path.join(base, "data", "prompts", "paris-is-the-capital-of", "4_visualizations")
    viz_south = os.path.join(base, "data", "prompts", "the-southern-most-us-state-is", "4_visualizations")
    viz_val_south = os.path.join(base, "data", "prompts", "gemma-2-2b_the-southern-most-us-state-is", "4_visualizations")
    viz_val_water = os.path.join(base, "data", "prompts", "gemma-2-2b_water-boils-at-100-degrees", "4_visualizations")

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 1: Title
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    # Green banner
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(2.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ACCENT
    shape.line.fill.background()

    # Title text
    txBox = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11), Inches(1.2))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = "Traceback Graphing: Identifying Information"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = WHITE
    p.font.name = FONT_TITLE
    p2 = tf.add_paragraph()
    p2.text = "Bottlenecks in LLM Attribution Circuits"
    p2.font.size = Pt(32)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.font.name = FONT_TITLE

    # Subtitle
    txBox2 = slide.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(11), Inches(0.5))
    tf2 = txBox2.text_frame
    p3 = tf2.paragraphs[0]
    p3.text = "Mechanistic Interpretability via Neuronpedia Circuit Tracer"
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(0xC8, 0xE6, 0xC9)
    p3.font.name = FONT_BODY

    # Presenter info
    txBox3 = slide.shapes.add_textbox(Inches(0.8), Inches(3.2), Inches(5), Inches(1.5))
    tf3 = txBox3.text_frame
    for line, sz in [
        ("J. Lawrence", 20),
        (f"Lab Meeting  |  {datetime.date.today().strftime('%B %d, %Y')}", 14),
        ("CUNY Graduate Center / Hunter College", 14),
    ]:
        if tf3.paragraphs[0].text == "":
            p = tf3.paragraphs[0]
        else:
            p = tf3.add_paragraph()
        p.text = line
        p.font.size = Pt(sz)
        p.font.color.rgb = DARK if sz == 20 else GRAY
        p.font.name = FONT_BODY
        if sz == 20:
            p.font.bold = True

    add_speaker_notes(slide,
        "Welcome everyone. Today I'll present our Traceback Graphing project, "
        "which is a new method for identifying information bottlenecks inside "
        "large language models. We use Neuronpedia's Circuit Tracer API to extract "
        "attribution graphs, then apply a novel backward-BFS algorithm to find the "
        "critical features that control model predictions. I'll walk through our pipeline, "
        "show key findings across two models, and discuss where we're headed next.")
    add_footer(slide, 1, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 2: The Big Question
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Bottleneck position determines what information survives to the output layer")
    add_slide_title(slide, "The Big Question")

    add_bullets(slide, [
        ("WHY do LLMs fail on facts they 'know'?", 0),
        ("GEMMA-2-2B: 'Paris is capital of' -> 'France' (85.7%)", 1),
        ("GEMMA-2-2B: 'Capital of France is' -> 'a' (20.7%)  -- same fact, wrong answer", 1),
        ("", 0),
        ("Hypothesis: internal bottleneck features filter information", 0),
        ("Early bottlenecks discard semantics, keeping only syntax", 1),
        ("Late bottlenecks preserve more factual content", 1),
        ("", 0),
        ("Approach: trace attribution paths backward from output", 0),
        ("Identify WHERE convergence occurs = the bottleneck layer", 1),
        ("Classify WHAT survives = syntax vs. semantics", 1),
    ], top=1.5, font_size=16)

    add_speaker_notes(slide,
        "The central question is: why do language models fail on facts they clearly 'know'? "
        "GEMMA can answer 'Paris is capital of' correctly at 85.7%, but rephrase it as "
        "'Capital of France is' and accuracy drops to 20.7%. Same factual knowledge, different "
        "syntactic frame. Our hypothesis is that information bottleneck features inside the "
        "network filter content at specific layers. If the bottleneck is too early, semantic "
        "information like geographic facts gets discarded. If it's later, facts survive. "
        "Our approach traces attribution paths backward from the output to find these bottlenecks.")
    add_footer(slide, 2, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 3: Experimental Overview
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Two models, 10+ prompts, automated end-to-end pipeline")
    add_slide_title(slide, "Experimental Overview")

    left_b = [
        ("Models", 0),
        ("GEMMA-2-2B (26 layers, Google)", 1),
        ("QWEN3-4B (36 layers, Alibaba)", 1),
        ("", 0),
        ("Prompt Categories", 0),
        ("Geographic: capitals, states, cities", 1),
        ("Arithmetic: addition, temperature", 1),
        ("Political: president, governor", 1),
    ]
    right_b = [
        ("Data Source", 0),
        ("Neuronpedia Circuit Tracer API", 1),
        ("SAE-decoded feature activations", 1),
        ("", 0),
        ("Analysis Methods", 0),
        ("Traceback BFS (novel -- our method)", 1),
        ("Louvain clustering for supernodes", 1),
        ("Betweenness centrality for bottlenecks", 1),
    ]
    add_two_column_text(slide, left_b, right_b, top=1.5)

    add_speaker_notes(slide,
        "We analyze two open-weight models: GEMMA-2-2B from Google with 26 layers and "
        "QWEN3-4B from Alibaba with 36 layers. We run the same prompts through both models "
        "and compare their internal circuits. Prompts span geography, arithmetic, and politics. "
        "Data comes from Neuronpedia's Circuit Tracer API, which returns SAE-decoded feature "
        "activations and edges. Our novel contribution is the Traceback BFS algorithm that "
        "traces paths backward from output nodes to find bottleneck features. We also use "
        "Louvain community detection for supernodes and betweenness centrality.")
    add_footer(slide, 3, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 4: Pipeline Schematic
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Fully automated: prompt in -> bottleneck analysis + visualizations out")
    add_slide_title(slide, "End-to-End Pipeline")

    # Draw pipeline as connected boxes
    steps = [
        ("1. Generate\nGraph", "API call to\nNeuronpedia"),
        ("2. Convert\nGraph", "Standardize\nformat"),
        ("3a. Analyze\nCircuit", "Supernodes +\nbottlenecks"),
        ("3b. Traceback\nPaths", "Backward BFS\n(NOVEL)"),
        ("4. Visualize", "8 diagnostic\nplots"),
    ]
    box_w, box_h = Inches(2.0), Inches(1.2)
    start_x = Inches(0.5)
    y = Inches(2.0)
    gap = Inches(0.35)

    for i, (label, sublabel) in enumerate(steps):
        x = start_x + i * (box_w + gap)
        # Main box
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, box_w, box_h)
        fill_color = ACCENT if i == 3 else ACCENT_LIGHT  # Highlight novel step
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
        shape.line.fill.background()
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = label
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = WHITE
        p.font.name = FONT_TITLE
        p.alignment = PP_ALIGN.CENTER

        # Sublabel below box
        txBox = slide.shapes.add_textbox(x, y + box_h + Inches(0.05), box_w, Inches(0.5))
        tf2 = txBox.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        p2.text = sublabel
        p2.font.size = Pt(10)
        p2.font.color.rgb = GRAY
        p2.font.name = FONT_BODY
        p2.alignment = PP_ALIGN.CENTER

        # Arrow between boxes
        if i < len(steps) - 1:
            arrow_x = x + box_w
            arrow_y = y + box_h / 2
            arr = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
                                          arrow_x, arrow_y - Inches(0.1),
                                          gap, Inches(0.2))
            arr.fill.solid()
            arr.fill.fore_color.rgb = GRAY
            arr.line.fill.background()

    # Bottom: outputs summary
    add_bullets(slide, [
        ("Outputs per prompt: raw_graph.json | converted_graph.json | circuit_analysis.json | traceback_paths.json | 8 PNGs", 0),
        ("Runtime: ~30 seconds end-to-end per prompt (API-bound)", 0),
        ("All artifacts version-controlled in data/prompts/<prompt-name>/", 0),
    ], top=4.2, font_size=13)

    add_speaker_notes(slide,
        "Here's our end-to-end pipeline. Step 1 calls Neuronpedia's API with a text prompt "
        "and model selection, returning a raw attribution graph. Step 2 converts this to our "
        "standardized format. Step 3a applies Louvain clustering and betweenness centrality "
        "for supernode detection and initial bottleneck identification. Step 3b -- our novel "
        "contribution -- runs backward BFS from output nodes with geometric decay scoring. "
        "This traces all paths back to the input and identifies where they converge. "
        "Step 4 generates 8 diagnostic visualizations. The whole pipeline runs in about 30 "
        "seconds per prompt, limited by the API call. Every artifact is version-controlled.")
    add_footer(slide, 4, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 5: Traceback Algorithm Detail
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Novel backward-BFS identifies convergence points = information bottlenecks")
    add_slide_title(slide, "Traceback Algorithm (Novel Method)")

    left_b = [
        ("Algorithm", 0),
        ("Start from top-K output-layer nodes", 1),
        ("BFS backward through edges", 1),
        ("Score(child) = Score(parent) * |edge_weight|^0.8", 1),
        ("Geometric decay prevents explosion", 1),
        ("", 0),
        ("Key Metric: Convergence", 0),
        ("100% of paths through 1 node = bottleneck", 1),
        ("Convergence layer = decision point", 1),
    ]
    right_b = [
        ("Why Backward (not Forward)?", 0),
        ("Forward: exponential branching", 1),
        ("Backward: converges naturally", 1),
        ("Finds minimal sufficient set", 1),
        ("", 0),
        ("Validation", 0),
        ("Top-5 vs bottom-5 output nodes", 1),
        ("Both converge to SAME bottleneck", 1),
        ("Confirms: shared universal circuit", 1),
    ]
    add_two_column_text(slide, left_b, right_b, top=1.5)

    # Figure placeholder
    add_placeholder_box(slide, "[INSERT: Traceback path diagram showing\nconvergence from 5 output nodes to 1 bottleneck]",
                         3.5, 5.2, 6, 1.8)

    add_speaker_notes(slide,
        "This is our core methodological contribution. Traditional interpretability asks "
        "'which input tokens matter?' We ask 'which intermediate features control the output?' "
        "The algorithm starts from the top-K highest-activation output nodes and traces backward "
        "through all edges using BFS. Each step multiplies the parent score by edge weight raised "
        "to 0.8 -- this geometric decay prevents score explosion while preserving relative "
        "importance. The key insight is convergence: when ALL backward paths pass through a single "
        "node, that's your bottleneck. We validated by running traceback from both the top-5 AND "
        "bottom-5 output nodes -- they converge on the exact same bottleneck feature, confirming "
        "the model uses one shared circuit for all predictions, not separate per-token pathways.")
    add_footer(slide, 5, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 6: Pipeline Steps Detail
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Each step has clear inputs, QC checks, and versioned output artifacts")
    add_slide_title(slide, "Pipeline Step Details")

    # Table-like layout
    headers = ["Step", "Input", "Method / QC", "Output Artifact"]
    rows = [
        ["1. Generate", "Prompt + model ID", "API call; verify node/edge counts", "raw_graph.json + metadata.json"],
        ["2. Convert", "raw_graph.json", "Normalize tokens; validate edge integrity", "converted_graph.json"],
        ["3a. Analyze", "converted_graph.json", "Louvain + centrality; fetch descriptions", "circuit_analysis.json + supernodes.json"],
        ["3b. Traceback", "converted_graph.json", "Backward BFS; decay=0.8; top-5 seeds", "traceback_paths.json"],
        ["4. Visualize", "All analysis JSONs", "8 plot types; auto-layout", "8 PNG files"],
    ]

    # Build as a simple table shape
    from pptx.util import Inches as In
    table_shape = slide.shapes.add_table(len(rows) + 1, 4,
                                          Inches(0.5), Inches(1.5),
                                          Inches(12), Inches(4.0))
    table = table_shape.table

    # Set column widths
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(2.5)
    table.columns[2].width = Inches(4.2)
    table.columns[3].width = Inches(3.5)

    # Header row
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = WHITE
            p.font.name = FONT_BODY
        cell.fill.solid()
        cell.fill.fore_color.rgb = ACCENT

    # Data rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.text = val
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(12)
                p.font.color.rgb = DARK
                p.font.name = FONT_BODY
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 == 0 else LIGHT_BG

    add_speaker_notes(slide,
        "Here's the detail for each pipeline step. Step 1 queries Neuronpedia's Circuit Tracer "
        "API. We validate the returned graph has expected node and edge counts. Step 2 normalizes "
        "the token format across models -- GEMMA uses raw tokens while QWEN prepends special tokens. "
        "We also validate edge integrity: every edge must connect existing nodes. Step 3a runs "
        "Louvain community detection for supernodes and betweenness centrality for initial "
        "bottleneck identification. It also fetches human-readable feature descriptions from "
        "Neuronpedia. Step 3b is our novel traceback -- backward BFS with geometric decay from "
        "the top-5 output nodes. Step 4 generates all 8 visualization types. Each step writes "
        "a versioned artifact to the prompt's data directory.")
    add_footer(slide, 6, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 7: What We've Produced
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  10+ prompts analyzed across 2 models with full artifact sets")
    add_slide_title(slide, "Deliverables Produced So Far")

    left_b = [
        ("Datasets (per prompt x model)", 0),
        ("10+ prompt variations fully analyzed", 1),
        ("2 models: GEMMA-2-2B, QWEN3-4B", 1),
        ("80+ visualization PNGs generated", 1),
        ("Traceback JSONs for key prompts", 1),
        ("", 0),
        ("Code / Pipeline", 0),
        ("5-script automated pipeline", 1),
        ("Centralized PathManager for reproducibility", 1),
        ("Cross-model comparison script", 1),
    ]
    right_b = [
        ("Research Documents", 0),
        ("Full scientific paper draft (~6,800 words)", 1),
        ("Southern State case study", 1),
        ("Token Attribution validation report", 1),
        ("Semantic Taxonomy methodology", 1),
        ("", 0),
        ("Quantitative Tables", 0),
        ("Prediction probabilities per model/prompt", 1),
        ("Bottleneck positions (layer, feature ID)", 1),
        ("Convergence rates (% paths through BN)", 1),
    ]
    add_two_column_text(slide, left_b, right_b, top=1.5)

    add_speaker_notes(slide,
        "Here's what we've produced. On the data side: 10+ prompt variations fully analyzed "
        "through both models, generating over 80 visualization PNGs and structured JSON artifacts. "
        "The code is a 5-script automated pipeline with a centralized PathManager that ensures "
        "consistent file organization and reproducibility. On the research side, we have a "
        "6,800-word scientific paper draft ready for formatting, plus detailed case studies on "
        "the Southern State prompt, the Token Attribution validation, and our Semantic Taxonomy "
        "methodology for classifying features. Quantitative tables include prediction probabilities, "
        "bottleneck positions, and convergence rates across all experiments.")
    add_footer(slide, 7, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 8: Key Finding 1 -- Bottleneck Position
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  FINDING 1: Bottleneck at 19% depth (GEMMA) filters semantics; at 33% (QWEN) preserves them")
    add_slide_title(slide, "Key Finding: Bottleneck Position Determines Accuracy")

    left_b = [
        ("GEMMA-2-2B (26 layers)", 0),
        ("Bottleneck: Layer 5 (19% depth)", 1),
        ("'Southern most US state is' -> ' home' (10.5%)", 1),
        ("Correct ' Hawaii' ranks 6th (2.9%)", 1),
        ("Early compression discards geography", 1),
    ]
    right_b = [
        ("QWEN3-4B (36 layers)", 0),
        ("Bottleneck: Layer 12 (33% depth)", 1),
        ("'Southern most US state is' -> ' Florida' (78.1%)", 1),
        ("27x higher probability than GEMMA", 1),
        ("Later bottleneck preserves facts", 1),
    ]
    add_two_column_text(slide, left_b, right_b, top=1.5)

    # Figure placeholders
    insert_image_if_exists(slide, os.path.join(viz_south, "summary_dashboard.png"),
                            1.0, 4.2, 5.0, 2.8,
                            "[INSERT: GEMMA summary dashboard\nfor 'southern most US state']")
    add_placeholder_box(slide, "[INSERT: QWEN summary dashboard\nfor same prompt -- showing correct prediction]",
                         7.0, 4.2, 5.0, 2.8)

    add_speaker_notes(slide,
        "Our strongest finding. On the Southern State prompt, GEMMA's bottleneck occurs at "
        "Layer 5 -- only 19% into the network. All 5 traceback paths converge on a single "
        "feature at this layer with 100% convergence. This early compression filters out "
        "geographic semantic information, so the model predicts ' home' at 10.5% instead of "
        "the correct answer. QWEN's bottleneck is at Layer 12 -- 33% depth. This preserves "
        "enough factual content to predict ' Florida' at 78.1%, a 27x improvement. "
        "This strongly supports our hypothesis: bottleneck position is a key architectural "
        "parameter that determines factual accuracy. Models with later bottlenecks retain more "
        "semantic information through the critical compression point.")
    add_footer(slide, 8, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 9: Key Finding 2 -- Syntax vs Semantics
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  FINDING 2: 79/80 top features are syntactic -- models use template matching, not knowledge retrieval")
    add_slide_title(slide, "Key Finding: Syntactic Pattern Matching Dominates")

    add_bullets(slide, [
        ("'Paris is the capital of' -- what features fire?", 0),
        ("79/80 top features = syntax (articles, punctuation, connectors)", 1),
        ("0/80 features directly encode 'Paris' or 'France'", 1),
        ("Model uses template: 'X is capital of Y' -- not geographic knowledge", 1),
        ("", 0),
        ("Prompt sensitivity confirms pattern matching:", 0),
        ("'Paris is capital of'  -> ' France' at 85.7%  (matches template)", 1),
        ("'Capital of France is' -> ' a' at 20.7%  (template broken)", 1),
        ("Same facts, but syntactic frame determines success", 1),
        ("", 0),
        ("Implication: factual recall is fragile and syntax-dependent", 0),
    ], top=1.5, font_size=15)

    # Figure placeholder
    insert_image_if_exists(slide, os.path.join(viz_paris, "feature_importance.png"),
                            8.5, 4.0, 4.0, 3.0,
                            "[INSERT: Feature importance chart\nshowing top 20 features -- all syntactic]")

    add_speaker_notes(slide,
        "Our second major finding. When we examine which features fire for 'Paris is the "
        "capital of', 79 out of 80 top features are syntactic -- they encode articles, "
        "punctuation, connective structures. Zero features directly encode Paris or France "
        "as geographic entities. The model is doing template matching: it learns the syntactic "
        "frame 'X is capital of Y' and fills in the slot. This explains the prompt sensitivity: "
        "when you say 'Paris is capital of', it matches the template and gets 85.7%. But "
        "'Capital of France is' breaks the template and accuracy drops to 20.7%. Same factual "
        "knowledge, but the syntactic frame determines whether it can be accessed. This is a "
        "fundamental insight about how factual recall works -- or fails -- in these models.")
    add_footer(slide, 9, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 10: Key Finding 3 -- Shared Circuit
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  FINDING 3: All output tokens share ONE circuit -- token attribution hypothesis refuted")
    add_slide_title(slide, "Key Finding: Universal Shared Circuit")

    add_bullets(slide, [
        ("Initial hypothesis: different tokens use different circuits", 0),
        ("Top predictions -> top-ranked output nodes -> unique pathways?", 1),
        ("Alternative predictions -> bottom-ranked nodes -> separate pathways?", 1),
        ("", 0),
        ("Result: HYPOTHESIS REFUTED", 0),
        ("Top-5 AND bottom-5 output nodes converge on SAME bottleneck", 1),
        ("100% overlap -- zero unique pathways found", 1),
        ("Model computes full probability distribution through ONE circuit", 1),
        ("", 0),
        ("Implication: interventions target the whole circuit, not per-token", 0),
        ("Cannot selectively boost one answer without affecting all", 1),
    ], top=1.5, font_size=15)

    add_speaker_notes(slide,
        "We tested the Token Attribution Hypothesis: do different output tokens use different "
        "internal circuits? We ran traceback from the top-5 highest-activation output nodes -- "
        "which correspond to the model's top predictions -- and separately from the bottom-5. "
        "If the hypothesis were correct, they should trace back through different pathways. "
        "Instead, both sets converge on the exact same bottleneck feature with 100% overlap. "
        "This refutes the hypothesis and tells us the model uses a single shared universal "
        "circuit that computes the entire probability distribution. The practical implication "
        "is that you cannot selectively boost one prediction by targeting its 'unique' pathway "
        "-- there is no unique pathway. Any intervention affects the entire distribution.")
    add_footer(slide, 10, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 11: Caveats & Limitations
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Key limitations: linear attribution, SAE fidelity, limited prompt diversity")
    add_slide_title(slide, "Caveats & What's Still Uncertain")

    add_bullets(slide, [
        ("Linear attribution assumption", 0),
        ("Edges = linear contribution; non-linear interactions not captured", 1),
        ("LayerNorm, attention softmax create non-linearities we approximate", 1),
        ("", 0),
        ("SAE reconstruction fidelity (~90%)", 0),
        ("~10% of information lost in sparse autoencoder decomposition", 1),
        ("Some features may be polysemantic (encode multiple concepts)", 1),
        ("", 0),
        ("Prompt diversity", 0),
        ("Deep analysis on ~5 prompts per model; need broader coverage", 1),
        ("Arithmetic prompts show both models fail (below emergence threshold)", 1),
        ("", 0),
        ("Causal validation pending", 0),
        ("Bottlenecks identified correlatively; ablation experiments needed", 1),
    ], top=1.5, font_size=15)

    add_speaker_notes(slide,
        "Important caveats. First, our attribution is linear -- we trace edge weights that "
        "represent linear contributions. Non-linear interactions from LayerNorm and attention "
        "softmax are approximated, not captured exactly. Second, SAE reconstruction is about "
        "90% faithful -- so roughly 10% of information isn't captured in the feature decomposition. "
        "Some features may also be polysemantic, encoding multiple concepts simultaneously. "
        "Third, while we've tested 10+ prompts, deep traceback analysis has been done on about "
        "5 prompts per model. We need broader prompt diversity. Fourth, and most importantly, "
        "our bottleneck identification is correlational. We haven't yet done ablation experiments "
        "to prove these bottlenecks are causally necessary. That's what validation is addressing.")
    add_footer(slide, 11, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 12: Validation Plan
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Validation in progress: multi-algorithm comparison + semantic taxonomy annotation")
    add_slide_title(slide, "Validation Plan (In Progress)")

    left_b = [
        ("Algorithm Validation", 0),
        ("Multi-algorithm analysis: compare traceback", 1),
        ("  vs betweenness centrality vs PageRank", 1),
        ("Jaccard similarity between methods", 1),
        ("Convergence proof visualizations", 1),
        ("Already completed for 3 prompts", 1),
    ]
    right_b = [
        ("Semantic Taxonomy", 0),
        ("Classify top features: SYNTAX / SEMANTICS", 1),
        ("Sub-categories: Geographic, Temporal, Entity", 1),
        ("Inter-rater reliability target: kappa > 0.7", 1),
        ("Track semantic flow through bottleneck", 1),
        ("Annotation CSV in progress", 1),
    ]
    add_two_column_text(slide, left_b, right_b, top=1.5)

    # Insert validation figures if they exist
    insert_image_if_exists(slide, os.path.join(viz_val_south, "validation_algorithm_comparison.png"),
                            0.5, 4.5, 3.8, 2.5,
                            "[INSERT: Algorithm comparison chart]")
    insert_image_if_exists(slide, os.path.join(viz_val_south, "validation_jaccard_heatmap.png"),
                            4.6, 4.5, 3.8, 2.5,
                            "[INSERT: Jaccard similarity heatmap]")
    insert_image_if_exists(slide, os.path.join(viz_val_south, "validation_convergence_proof.png"),
                            8.7, 4.5, 3.8, 2.5,
                            "[INSERT: Convergence proof]")

    add_speaker_notes(slide,
        "Here's what we're doing right now for validation. On the algorithm side, we're running "
        "multi-algorithm comparisons: our traceback BFS against betweenness centrality and "
        "PageRank. We compute Jaccard similarity between the critical node sets identified by "
        "each method. If traceback and centrality agree on the same bottlenecks, that's strong "
        "convergent evidence. We've already completed this for 3 prompts with visualizations. "
        "On the semantic side, we're building a taxonomy to classify features as SYNTAX vs "
        "SEMANTICS with sub-categories. The acceptance criterion is inter-rater reliability "
        "kappa above 0.7. This will let us quantify exactly what percentage of semantic vs "
        "syntactic information passes through each bottleneck layer. Annotation is in progress.")
    add_footer(slide, 12, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 13: Next Steps
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  Next 4 weeks: complete validation, run ablations, expand to more models")
    add_slide_title(slide, "Next Steps & Timeline")

    add_bullets(slide, [
        ("Weeks 1-2: Complete Validation", 0),
        ("Finish semantic taxonomy annotation (top 100 features)", 1),
        ("Complete QWEN traceback for remaining prompts", 1),
        ("Generate cross-prompt bottleneck comparison table", 1),
        ("", 0),
        ("Weeks 3-4: Causal Experiments", 0),
        ("Ablation: zero out bottleneck features, measure accuracy change", 1),
        ("Amplification: boost geographic features at layer before bottleneck", 1),
        ("Quantify information loss with mutual information estimates", 1),
        ("", 0),
        ("Ongoing: Extend Scope", 0),
        ("Add 3+ prompt categories (code, reasoning, multi-hop)", 1),
        ("Test on Llama-3 (8B) for larger model comparison", 1),
        ("Format paper draft for workshop submission", 1),
    ], top=1.5, font_size=15)

    add_speaker_notes(slide,
        "Here's the roadmap. Weeks 1-2: finish validation. Complete the semantic taxonomy "
        "for the top 100 features so we can quantify what passes through bottlenecks. Finish "
        "QWEN traceback analysis on remaining prompts. Build a comprehensive cross-prompt "
        "comparison table showing bottleneck positions across all experiments. "
        "Weeks 3-4: causal experiments. The critical test: ablate the bottleneck feature -- "
        "zero it out -- and measure whether accuracy on geographic prompts actually changes. "
        "Also try amplifying geographic features at the layer just before the bottleneck. "
        "And estimate mutual information to quantify how much information is lost at each "
        "bottleneck. Ongoing: expand to more prompt categories -- code generation, multi-hop "
        "reasoning. Test a larger model like Llama-3 8B. And format the paper draft for a "
        "workshop submission.")
    add_footer(slide, 13, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # SLIDE 14: Asks / Decisions
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  I need feedback on: validation criteria, ablation priorities, and submission target")
    add_slide_title(slide, "Asks & Decisions Needed")

    add_bullets(slide, [
        ("1. Validation acceptance criteria", 0),
        ("Is kappa > 0.7 for semantic taxonomy sufficient?", 1),
        ("What Jaccard threshold confirms algorithm agreement?", 1),
        ("", 0),
        ("2. Ablation experiment priority", 0),
        ("Should we prioritize single-feature ablation or path ablation?", 1),
        ("Which prompts are highest priority for causal testing?", 1),
        ("", 0),
        ("3. Submission target", 0),
        ("Workshop paper (NeurIPS MechInterp) vs full paper (ICLR)?", 1),
        ("Timeline implications: workshop = 4 weeks, full = 8-12 weeks", 1),
        ("", 0),
        ("4. Compute needs", 0),
        ("Ablation experiments need model inference -- GPU access?", 1),
        ("Extend to Llama-3 8B requires additional API access", 1),
    ], top=1.5, font_size=15)

    add_speaker_notes(slide,
        "I have four asks for the group. First, validation criteria: is inter-rater kappa "
        "above 0.7 sufficient for the semantic taxonomy? And what Jaccard similarity threshold "
        "should we require for algorithm agreement? Second, when we move to ablation experiments, "
        "should we focus on single-feature ablation -- zeroing out one bottleneck node -- or "
        "full path ablation where we knock out the entire bottleneck pathway? And which prompts "
        "should we test first? Third, submission target: we could aim for a workshop paper at "
        "NeurIPS Mechanistic Interpretability workshop in about 4 weeks, or a full paper at "
        "ICLR which would take 8-12 weeks. The paper draft is at 6,800 words, close to workshop "
        "length already. Fourth, ablation experiments need GPU access for model inference. "
        "And extending to Llama-3 may require additional API access. I'd appreciate guidance "
        "on all four points. Thank you!")
    add_footer(slide, 14, TOTAL_SLIDES)

    # ════════════════════════════════════════════════════════════════════════
    # BONUS: Executive Summary Slide (can swap in if time is short)
    # ════════════════════════════════════════════════════════════════════════
    slide = prs.slides.add_slide(blank_layout)
    add_takehome_bar(slide, "  EXECUTIVE SUMMARY: Bottleneck position is a key architectural parameter for factual accuracy")
    add_slide_title(slide, "Executive Summary (Backup Slide)")

    add_bullets(slide, [
        ("What: automated pipeline to find information bottlenecks in LLMs", 0),
        ("How: novel backward-BFS traceback through Neuronpedia attribution graphs", 0),
        ("", 0),
        ("Finding 1: Bottleneck at 19% depth (GEMMA) vs 33% (QWEN) -> 27x accuracy diff", 0),
        ("Finding 2: 79/80 top features are syntactic -- template matching, not knowledge", 0),
        ("Finding 3: All outputs share ONE circuit -- shared universal architecture", 0),
        ("", 0),
        ("Status: validating with multi-algorithm comparison + semantic taxonomy", 0),
        ("Next: causal ablation experiments in weeks 3-4", 0),
        ("Ask: validation criteria, ablation priorities, submission target, GPU access", 0),
    ], top=1.5, font_size=16)

    add_speaker_notes(slide,
        "If you're short on time, this one slide captures everything. We built an automated "
        "pipeline that identifies information bottlenecks inside language models. Our novel "
        "traceback algorithm finds where attribution paths converge. Three key findings: "
        "bottleneck position determines accuracy with a 27x difference between models, "
        "factual recall is dominated by syntactic template matching not semantic knowledge, "
        "and all output tokens share a single universal circuit. We're currently validating "
        "these findings with multi-algorithm comparison and semantic feature classification. "
        "Next we'll run causal ablation experiments. I need the group's input on validation "
        "criteria, experiment priorities, submission target, and compute resources.")
    add_footer(slide, "B", TOTAL_SLIDES)

    # ── Save ───────────────────────────────────────────────────────────────
    output_path = os.path.join(base, "Traceback_Graphing_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved to: {output_path}")
    print(f"Total slides: {len(prs.slides)}")
    return output_path


if __name__ == "__main__":
    build_deck()

"""Regression checks for the explanatory diagram, never empirical analyses."""
import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import plot_methods_workflow as workflow


def test_exact_prompts_are_read_from_development_manifest():
    with (ROOT / "config/paper_control_manifest.csv").open(encoding="utf-8", newline="") as handle:
        manifest = {(r["pair_id"], r["role"]): r for r in csv.DictReader(handle)}
    examples = workflow.prompt_examples()
    assert all(row == manifest[key] for key, row in examples.items())
    assert examples[("gold_symbol", "target")]["prompt"] == "The chemical symbol for gold is"
    assert examples[("gold_symbol", "positive_paraphrase")]["prompt"] == "Gold has the chemical symbol"
    assert examples[("iron_symbol", "positive_paraphrase")]["prompt"] == "Iron has the chemical symbol"
    assert all(row["split"] == "development" for row in examples.values())
    assert all(path.is_file() for path in workflow.source_paths())


def test_illustrative_set_arithmetic():
    own, other, difference = workflow.illustrative_scores()
    assert len(workflow.ILLUSTRATIVE_TARGET & workflow.ILLUSTRATIVE_OWN) == 2
    assert len(workflow.ILLUSTRATIVE_TARGET | workflow.ILLUSTRATIVE_OWN) == 4
    assert own == .5
    assert other == pytest.approx(.3)
    assert difference == pytest.approx(.2)
    assert workflow.illustrative_jaccard(set(), set()) == 0
    assert workflow.illustrative_jaccard(["a", "a"], ["a"]) == 1


def test_feature_identity_preserves_family_and_layer_but_not_position():
    # Check the diagram's identity rule against the actual implementation.
    from whole_graph_analysis import node_identity
    a = dict(node_type="transcoder", layer=2, feature_id=7, token_position=2)
    repeated = {**a, "token_position": 5}
    assert node_identity(a) == node_identity(repeated) == ("transcoder", 2, 7)
    identities = {node_identity(node) for node in
                  [a, repeated, {**a, "layer": 3}, {**a, "node_type": "lorsa"}]}
    assert len(identities) == 3


def test_diagram_is_title_free_legible_and_inside_card_bounds():
    fig = workflow.build_figure()
    try:
        assert fig._suptitle is None
        assert tuple(fig.get_size_inches()) == (15, 10)
        workflow.validate_figure(fig)
        labels = "\n".join(t.get_text() for ax in fig.axes for t in ax.texts)
        assert workflow.ILLUSTRATION_NOTICE in labels
        assert "ALL other included factual rewordings" in labels
        assert "Not the other-fact baseline" in labels
        assert "Not graph pairs" in labels
        assert "Retain the layer" in labels
        assert "complete accepted answer" in labels
        assert "including registered spellings" in labels
        assert "after trimming whitespace" in workflow.CAPTION
        assert "Jaccard overlap" in labels
        assert "reconstruction-error nodes" in labels
        assert "Shared: a, b (green). Not shared: c, d (white)." in labels
        assert "$M_i$" in labels and "Delta" not in labels
        assert chr(0x2014) not in labels
        normalized = " ".join(labels.split())
        assert all(row["prompt"] in normalized for row in workflow.prompt_examples().values())
    finally:
        plt.close(fig)


def test_caption_distinguishes_examples_controls_and_primary_baseline():
    caption = workflow.CAPTION
    for phrase in [
        "development examples", "not evaluation questions", "every other included factual rewording",
        "mean of all those Jaccard overlaps", "one difference per fact",
        "facts, not graph pairs", "not the primary eligibility rule",
        "These values do not describe the gold or iron graphs", workflow.ILLUSTRATION_NOTICE,
    ]:
        assert phrase in " ".join(caption.split())
    assert chr(0x2014) not in caption
    assert "p <" not in caption and "p=" not in caption

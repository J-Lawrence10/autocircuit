"""Presentation-only wording for the paper figures; no estimates are changed."""
import hashlib
import numpy as np
from matplotlib.text import Text

AUDIT = []


def numeric_signature(fig):
    """Fingerprint plotted numbers, excluding text and presentation geometry."""
    digest = hashlib.sha256()
    for ax in fig.axes:
        arrays = [line.get_xydata() for line in ax.lines]
        arrays += [c.get_offsets() for c in ax.collections]
        arrays += [c.get_array() for c in ax.collections if c.get_array() is not None]
        arrays += [im.get_array() for im in ax.images]
        arrays += [[p.get_x(), p.get_y(), p.get_width(), p.get_height()]
                   for p in ax.patches if all(hasattr(p, name) for name in
                                            ['get_x', 'get_y', 'get_width', 'get_height'])]
        for values in arrays:
            array = np.asanyarray(values)
            digest.update(str(array.shape).encode())
            digest.update(np.asarray(array, dtype=np.float64).tobytes())
    return digest.hexdigest()
TITLES = {
    'figure1_design_and_coverage': 'Three tests ask what similar graphs can tell us',
    'figure2_fact_signal': 'Reworded questions about the same fact share more features in these samples',
    'figure3_fact_and_wording': 'Both the fact and the wording are linked to shared features',
    'figure4_control_comparisons': 'Invented name controls give different results across models',
    'figure5_matched_choice': 'Same-fact overlap is higher when the answer letter stays the same',
    'figure6_failure_cases': 'Selected error graphs share more features with correct predictions giving the same answer',
    'figureS1_export_and_error': 'Graph files have two separate limits: ID conflicts and approximation error',
    'figureS2_robustness': 'Average overlap differences stay positive under alternative graph comparisons',
    'figureS3_equal_feature_counts': 'Average overlap differences stay positive with equal numbers of features',
    'figureS4_lexical_support': 'Other-fact questions share fewer words, leaving a gap in the controls',
    'figureS5_answer_audit': 'A matching first token does not always verify the whole answer',
    'figureS6_graph_location_sensitivity': 'The answer-related differences remain after removing some graph features',
}

CAPTIONS = {
'figure1_design_and_coverage': (
    'A, Compare rewordings of the same fact with other-fact questions in the same subject and evaluation group. '
    'Gold is the chemical element. The examples use development questions, not the test questions plotted in Figure 2; '
    'subject coverage differs across the three models. B, In Qwen3-4B, vary the queried country, capital-to-A/B mapping, '
    'and wording while preserving the words and token counts within each country pair. All 48 predicted letters were correct. '
    'France/Germany illustrates the design using a pilot pair excluded from that evaluation. '
    'Displayed prompts are shortened; full prompts retain both countries and the other words, while word order and country roles vary. '
    'C, Compare a selected wrong-answer graph with correct predictions for the intended country and for the answer actually produced. '
    'This Qwen3-4B diagnostic has 16 graphs from one country pair and two response formats, with shared controls. '
    'Answers refer to the highest-probability next token. Arrows indicate comparisons, not causes; box colors identify steps. '
    'Sample accounting reports collection counts, exclusions, and failed preliminary checks.'),
'figure2_fact_signal': (
    'A, Points represent questions reserved for evaluation that passed the fixed inclusion rules. The difference in feature overlap '
    'is same-fact rewording overlap minus average other-fact rewording overlap within the same subject and test set. '
    'The displayed arithmetic, 0.50 − 0.30 = +0.20, illustrates this subtraction. These example numbers are not measured results. '
    'Positive, zero, and negative values indicate more, equal, and less overlap with the same fact; units are Jaccard differences, '
    'not percentage increases. B, Subject averages. Colors and shapes identify subjects; diamonds show model averages and bars '
    'show saved 95% intervals from 10,000 question-bootstrap resamples. n counts questions. Means are 0.170 for Gemma-2-2B '
    '(8 questions), 0.085 for Qwen3-1.7B (5), and 0.162 for Qwen3-4B (10). Repeated facts and different subject coverage '
    'preclude a model ranking; shared words and answers remain coupled to fact identity. Missing groups are unavailable, not zero. '
    '*The original Qwen3-4B collection contains 145/147 planned graphs.'),
'figure3_fact_and_wording': (
    'A, Feature-set overlap differences. B, Saved-influence-weighted cosine differences, comparing the direction of weighted feature vectors. '
    'The baseline changes both fact and wording. Each value is similarity in the labeled comparison minus similarity in that baseline, '
    'calculated within subject. The illustrated gold/iron prompts show the comparisons: retain gold and reword the question, '
    'replace gold with iron while retaining the pattern, or change both for the baseline. “Same wording” means the same sentence '
    'pattern, not an identical prompt. Each tested model has 27 graphs: three facts × three wordings × three subjects. '
    'Colored points are subject averages; black diamonds average subjects equally. Lines connect descriptive estimates, not intervals. '
    'Mean fact/wording differences in A are 0.074/0.118 for Gemma-2-2B and 0.101/0.064 for Qwen3-4B. Some predicted first tokens '
    'are incomplete answers or non-answers. Only Qwen3-4B geography passes all nine expected-token checks; its differences are '
    '0.101/0.106. These similarity measures do not measure correctness or establish factor dominance or model superiority. '
    'Qwen3-1.7B was not tested here.'),
'figure4_control_comparisons': (
    'Replace the real name with an invented name, retaining the starting wording (A) or rewording it (B). For each test question, '
    'subtract overlap with the invented name prompt from overlap with the factual rewording. Positive values favor the factual '
    'rewording; negative values favor the invented name control. Colors identify models, points show questions, diamonds show means, '
    'and bars show saved 95% question-bootstrap intervals; n counts included questions. Panel A means are -0.069 (n=2), '
    '-0.014 (n=4), and +0.096 (n=10) for Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B. Matching uses only broad first-token categories '
    '(letters/numbers, whitespace, or punctuation/symbols), leaving exact answer, meaning, confidence, and correctness unmatched. '
    'Small, differently composed samples support comparison-specific findings rather than a general explanation by wording. '
    '*The original Qwen3-4B collection is incomplete (145/147 graphs).'),
'figure5_matched_choice': (
    'Qwen3-4B: six country pairs, 48 correct next-token A/B predictions, and identical word/token inventories within pairs. '
    'Rules were fixed before collection in this outcome-informed follow-up. A, Mean feature overlap in the four cross-wording '
    'comparisons: 0.8005, 0.4853, 0.7377, and 0.4874, read row by row. The scale runs from no shared features (0) to identical sets (1). '
    'B, Same-country minus different-country overlap is 0.0628 with the same letter and -0.0022 with a changed letter. '
    'Their paired difference is 0.0650 (exploratory Student-t 95% interval 0.0553–0.0746; two-sided sign-flip p=0.03125). '
    'C, Their average is the prespecified primary outcome: 0.0303 (95% block-bootstrap interval 0.0265–0.0338). The descriptive '
    'same-letter minus different-letter difference, averaged across country relationships, is 0.2827. Lines represent country pairs; '
    'diamonds show means. Only the primary mean in C has an interval drawn. Colors identify labeled categories; B and C use different '
    'vertical scales. Tests assume six independent country-pair blocks; the sign-flip test additionally assumes symmetric null differences. '
    'The 48 graphs and 4,096 conditional-null reassignments are not independent replicates. Near zero is not equivalence. '
    'Overlap differences are neither accuracy nor variance explained; query order, country roles, and output-conditioned graphs '
    'remain alternatives to a causal interpretation. Supplement S6 reports graph-location checks.'),
'figure6_failure_cases': (
    'Qwen3-4B, one country pair and two response formats. A, All eight named-country prompts predict the correct first token; '
    'all eight selected position-based prompts reproduce the error (four of each per format). B–C, Compare error graphs with '
    'correct predictions for the intended country (blue) or giving the same answer (orange), holding list order and A/B mapping fixed. '
    'With France first and A: Berlin, B: Paris, the indirect France question predicts Berlin; naming France predicts Paris and '
    'naming Germany predicts Berlin. The error graph shares more features with Germany/Berlin. Circles use all retained features; '
    'open squares average 200 equal-feature-count samples. Lines connect comparisons for the same error. Same-answer minus '
    'intended-country overlap averages 0.1983 for letters and 0.2649 for capital names (0.1851 and 0.2361 with equal counts). '
    'All 16 exports and eight comparison triples pass integrity and output checks. The selected cases share controls, so they '
    'support descriptive comparisons, not error-frequency estimates or population tests. Words differ between prompt types; '
    'position matching, negation errors, and output-conditioned graph structure remain unresolved explanations. The intended '
    'correct-answer node is absent from each error graph, leaving its contribution unknown.'),
'figureS1_export_and_error': (
    'A, The percentage of saved raw graph files in which the same node ID refers to conflicting node identities. Labels show affected files '
    'over files checked. Zero means no conflict was detected, not no graphs or no model errors. The original question sets include factual '
    'questions and controls; the fact/wording sets vary both factors. B, Reconstruction-error nodes record part of the model computation '
    'not captured by the feature approximation. The axis gives their share of absolute nonterminal-node influence, using the saved audit '
    'definitions. This is not the percentage of wrong answers or of reasoning explained. Box centers mark medians; boxes span the middle '
    '50%, whiskers extend to values within 1.5 box lengths, and dots show values beyond the whiskers. Original distributions use raw-file '
    'audits; Qwen3-4B uses converted graphs with no ambiguous IDs removed. Differences combine model, exporter, and approximation choices; '
    'they do not isolate model size or architecture.'),
'figureS2_robustness': (
    'The difference in feature overlap is same-fact overlap minus other-fact overlap, using the comparison specified for each check. '
    'Compare the original analysis with three alternatives: include reconstruction-error nodes; use only files without detected node-ID '
    'conflicts; or compare with the most similar other-fact question rather than the average other-fact question. '
    'Reconstruction-error nodes represent approximation error, not wrong model answers. Points are saved averages; bars are 95% bootstrap '
    'intervals from resampling test questions. n counts questions. Restricting files requires rebuilding the comparison groups and leaves '
    'only two Gemma questions, so that positive result is weak evidence on its own. The size-regression intercept is not plotted: with centered '
    'predictors it equals the unadjusted mean and is not an independent check. *Qwen3-4B remains incomplete (145/147 graphs).'),
'figureS3_equal_feature_counts': (
    'The difference in feature overlap is same-fact overlap minus average other-fact overlap within the same subject and test set. '
    'Within each model, subject, and test set, randomly sample the same number of features from every graph. '
    'K is the number of features in the smallest graph in that group; the second check uses half that number, rounded down. '
    'Repeat 200 times, reusing each sampled graph across comparisons within a repetition. Lines show individual test questions; diamonds '
    'show averages. Bars are descriptive 95% bootstrap intervals from resampling questions, not from the 200 feature samples. '
    'Seven of eight Gemma questions and all included Qwen questions retain positive average differences. '
    'Equalizing counts does not remove differences in shared words, answers, or which features the exporter retains. '
    'A smaller overlap score after sampling is not a percentage of signal explained. *Qwen3-4B remains incomplete (145/147 graphs).'),
'figureS4_lexical_support': (
    'For each test question, compare word overlap with its same-fact rewording (horizontal axis) against the highest word overlap with '
    'any other-fact rewording (vertical axis). Word overlap uses unique letter/number words, ignores letter case, and keeps common words. '
    'Both axes use Jaccard overlap: shared words divided by all distinct words across the pair. The dashed line means equal overlap; '
    'the shaded band allows a difference of 0.05 in either direction. Every other-fact comparison falls below that band. '
    'Thus 0/8 Gemma, 0/5 Qwen3-1.7B, and 0/10 Qwen3-4B questions have a comparison meeting the specified word-matching rule. '
    'None qualifies under the alternative at-least-as-much-word-overlap rule or the joint word/feature-count rule either. '
    'This is a missing comparison, not a measured zero effect or proof that words explain all feature overlap. '
    'Same-fact questions also share their expected answer, so the data do not isolate meaning from words or answers. '
    '*Qwen3-4B remains incomplete (145/147 graphs).'),
'figureS5_answer_audit': (
    'A, Audit the first predicted text unit, or token, using the Qwen tokenizers. Green means the whole expected answer fits in that token; '
    'yellow means it is only a compatible beginning, so the completed answer is unverified; gray means a different token. '
    'Seven apparent mismatches across the two Qwen models are compatible beginnings of multi-token answers. '
    'Counts include development and test factual questions, including Qwen3-1.7B geography questions without complete controls; '
    'they are not the question counts in Figure 2. Qwen3-4B is missing one factual graph and one invented name control graph. '
    'Official Qwen tokenizer versions agree with all saved prompt pieces and decoded top tokens, but the exact versions used at the time '
    'of graph collection cannot be fully recovered. Gemma tokenizer access was denied, leaving that audit unresolved. '
    'B, In the fact/wording experiment, counts use the original exact first-token matching rule after trimming whitespace; that rule is unchanged. '
    'Only Qwen3-4B geography matches in all nine questions. Its fact/wording differences are 0.101/0.106, which do not establish that either '
    'factor dominates. A zero in history means zero matches under this rule, not zero history knowledge. *The original Qwen3-4B collection is incomplete.'),
'figureS6_graph_location_sensitivity': (
    'Qwen3-4B only. Repeat the saved comparisons after removing features at the last token position, in the last quarter of observed '
    'feature layers, or both. Removal happens before combining feature identities across positions. '
    'A, Plot the difference between the same-letter and changed-letter fact comparisons in Figure 5B. Each line represents one of six '
    'country pairs; black diamonds show averages. B, Plot overlap with the correct same-answer response minus overlap with the correct '
    'intended-country response in the selected errors from Figure 6. Lines show the individual comparisons; colored diamonds show format averages. '
    'All filtered feature sets are nonempty. Zero means equal overlap, not missing data. '
    'These checks were chosen after seeing earlier results. No confidence intervals or new population tests are attached. '
    'Removing features from saved graphs is not an intervention on the model and does not establish a cause. '
    'The remaining graphs are still constructed around the answer being produced.'),
}

# Exact text replacements avoid accidentally altering numerical annotations or identifiers.
REPLACE = {
    'a  Made-up name, original wording': 'a  Invented name control, original wording',
    'b  Made-up name, reworded question': 'b  Invented name control, reworded question',
    'a  Related questions': 'a  Reword the same question',
    'Original three-model samples': 'Original samples: three models',
    'Compare with a gold paraphrase\nand with questions about other facts': 'Compare with a reworded gold question\nand questions about other facts',
    'Does asking about the same fact\nincrease feature overlap?': 'Do questions about the same fact\nshare more graph features?',
    'b  Answer-label controls': 'b  Change the A/B answer',
    'Change the queried country,\nanswer mapping, and wording': 'Change the country asked about,\nthe A/B choices, and the wording',
    'Does the same-fact advantage remain\nwhen the A/B answer label changes?': 'Do same-fact questions still share more\nfeatures when the A/B answer changes?',
    'Compare correct responses preserving\nthe intended country or the produced answer': 'Compare with correct responses to the\nintended country or giving the same answer',
    'Feature overlap = shared feature identities divided by their union (Jaccard). It is not a correctness score.': 'Feature overlap: the share of distinct features found in both graphs (Jaccard). This does not measure correctness.',
    'Arrows show comparison steps, not a causal circuit. Failed pilots and sample exclusions are reported separately.': 'Arrows show comparison steps, not causes. Failed preliminary checks and excluded questions are reported separately.',
    'a  Same-fact advantage for each test fact': 'a  Overlap difference for each test question',
    'b  Average advantage by subject': 'b  Average overlap difference by subject',
    'Extra feature overlap for the same fact\n(Jaccard difference)': 'Difference in feature overlap\n(same fact minus other facts)',
    'Subject (color and shape)': 'Subject',
    'Points: test facts. Diamonds: means. Bars: 95% intervals. n = number of facts; absent groups are not zero effects.': 'Points: test questions. Diamonds: averages. Bars: 95% intervals. n = questions. Missing groups are not zero effects.',
    'b  Similarity weighted by feature influence': 'b  Similarity including feature weights',
    'Extra feature overlap\n(Jaccard difference)': 'Difference in feature overlap\n(Jaccard)',
    'Extra influence-weighted similarity\n(cosine difference)': 'Difference in weighted similarity\n(cosine)',
    'Subject (color and shape); black diamonds show the mean': 'Subject; black diamonds show the average',
    'Across-domain mean': 'Average across subjects',
    'Baseline: different fact AND different wording. Includes non-answer outputs; Qwen3-1.7B was not collected here.': 'Baseline: different fact AND different wording. Some outputs are not answers. Qwen3-1.7B was not tested here.',
    'Factual-paraphrase overlap minus\nmade-up-name overlap (Jaccard difference)': 'Overlap with reworded fact minus\noverlap with invented name control',
    'Above zero: the factual paraphrase shares more features. Controls match only the broad next-token class.': 'Above zero: more overlap with the reworded fact. Controls match only token type, not the exact answer (see caption).',
    'Model (color)': 'Model',
    'Same answer\nlabel': 'Same A/B\nanswer',
    'Changed answer\nlabel': 'Changed A/B\nanswer',
    'b  Same-fact advantage': 'b  Same-fact minus other-fact overlap',
    'c  Average contrasts': 'c  Fact and answer comparisons',
    'Same fact\n(averaged over labels)': 'Same fact\n(average of B)',
    'Feature overlap (Jaccard): none to identical': 'Shared features (Jaccard): 0 = none; 1 = identical sets',
    'B-C: each line = one country pair; diamonds = means.\nOnly the balanced fact mean in C has a 95% interval.': 'B–C: each line = one country pair; diamonds = averages.\nOnly the fact average in C has a 95% interval.',
    'Qwen3-4B only. Six country pairs; 48/48 correct top-label decisions. B and C use different vertical scales.': 'Qwen3-4B only. Six country pairs; 48/48 correct A/B answers. B and C use different vertical scales.',
    'Near-zero is not proof of no effect. Similarity is not accuracy, variance explained, or a causal mechanism.': 'Near zero does not prove no effect. Graph similarity does not measure accuracy or establish a cause.',
    'a  Selected-case behavior': 'a  Correct answers in selected cases',
    'Correct next-token answers (count)': 'Correct first-token answers (count)',
    'Feature overlap (Jaccard)\n0 = none; 1 = identical feature sets': 'Shared features (Jaccard)\n0 = none; 1 = identical sets',
    'Correct response to the intended country': 'Correct answer to the intended country',
    'Correct response giving the same answer': 'Correct response giving the same answer as the error',
    'Matched feature counts': 'Equal numbers of features',
    'a  Export identity audit': 'a  Files with conflicting node IDs',
    'Raw exports with ambiguous node IDs (%)': 'Graph files with conflicting node IDs (%)',
    'b  Residual influence differs by pipeline': 'b  Contribution from approximation error',
    'Reconstruction-error node influence (%)': 'Reconstruction-error share of influence (%)',
    'Gemma\ncontrolled': 'Gemma-2-2B\nQuestions\nand controls',
    'Qwen1.7\ncontrolled': 'Qwen3-1.7B\nQuestions\nand controls',
    'Gemma\ncrossed': 'Gemma-2-2B\nFact/wording\ntest',
    'Qwen4\ncontrolled': 'Qwen3-4B\nQuestions\nand controls',
    'Qwen4\ncrossed': 'Qwen3-4B\nFact/wording\ntest',
    'Primary': 'Original\nanalysis',
    'Errors included': 'Include graph-\napproximation errors',
    'Clean exports': 'No detected\nID conflicts',
    'Hardest other fact': 'Most similar\nother-fact question',
    'Same-fact advantage (Jaccard difference)': 'Difference in feature overlap\n(same fact minus other facts)',
    'Own-paraphrase advantage (Jaccard difference)': 'Difference in feature overlap\n(same fact minus other facts)',
    'Equal count K': 'Same count\n(K features)',
    'Equal count K/2': 'Half that count\n(K/2 features)',
    'Exploratory. Lines = facts; diamonds = means. *Qwen3-4B extension incomplete (145/147 graphs).': 'Follow-up check. Lines = questions; diamonds = averages; bars = 95% intervals. *Qwen3-4B: 145/147 graphs.',
    'Word overlap with own paraphrase': 'Word overlap with the\nsame question reworded',
    'Highest word overlap with another fact': 'Highest word overlap with\na question about another fact',
    'Each point = a held-out fact (points may overlap). Shaded band = declared 0.05 word-overlap caliper.': 'Each point = one test question (points may overlap). Shading = within 0.05 of equal word overlap.',
    'a  Qwen tokenizer-aware audit': 'a  What does the first token confirm?',
    'b  Crossed strict answer agreement': 'b  Expected first-token matches',
    'Available factual prompt graphs': 'Factual-question graphs checked',
    'Whole expected answer in next token': 'Whole expected answer in the first token',
    'Compatible prefix; answer unverified': 'Only the beginning matches; whole answer unverified',
    'Different next token': 'Different first token',
    'Matching next tokens (out of 9)': 'Expected first-token matches (out of 9)',
    'Same-label minus changed-label\nsame-fact advantage (Jaccard)': 'Difference between the two\nfact comparisons in Figure 5B',
    'Same-output minus intended-country\noverlap in wrong answers (Jaccard)': 'Same-answer overlap minus\nintended-country overlap (Figure 6)',
    'a  Answer-label dependence persists': 'a  A/B answer difference remains',
    'b  Selected errors still favor the same output': 'b  Errors still resemble the same answer',
    'Full feature\nset': 'All retained\nfeatures',
    'Remove final\nposition': 'Remove last\ntoken position',
    'Remove last\nquarter of layers': 'Remove last\nquarter of layers',
    'Mean': 'Average',
    'One country pair; selected known failures, not a prevalence estimate. Prompts contain requested and excluded positions.': 'One country pair and selected errors: this does not show how often errors occur. Questions specify which position to use and avoid.',
    'Same-output resemblance does not distinguish position matching from negation errors or output-conditioned structure.': 'Similarity alone cannot tell us why the model chose the wrong answer; see the caption for possible explanations.',
    'France\nfirst': 'France\nlisted first',
    'France\nsecond': 'France\nlisted second',
    'Germany\nfirst': 'Germany\nlisted first',
    'Germany\nsecond': 'Germany\nlisted second',
    'Gemma-2-2B: 0/8 matched': 'Gemma-2-2B\n0/8 have a control with\nsimilar word overlap',
    'Qwen3-1.7B: 0/5 matched': 'Qwen3-1.7B\n0/5 have a control with\nsimilar word overlap',
    'Qwen3-4B*: 0/10 matched': 'Qwen3-4B*\n0/10 have a control with\nsimilar word overlap',
}


def clarify(fig, stem):
    # Tick text must also be updated in its formatter or draw() restores old labels.
    ticks = [(ax, axis, [t.get_text() for t in getattr(ax, 'get_'+axis+'ticklabels')()])
             for ax in fig.axes for axis in ['x', 'y']]
    # Remove earlier overall titles; the caller adds the single reviewed headline.
    old_titles = {
        'Pooled advantage remains after equalizing feature counts',
        'The present controls cannot separate shared words from fact identity',
        'Next-token agreement is not equivalent to verified factual retrieval',
        'The measured differences are not confined to final-position or late-layer nodes',
    }
    for item in fig.findobj(match=Text):
        before = item.get_text()
        after = REPLACE.get(before, before)
        if before in old_titles:
            after = ''
        if after != before:
            item.set_text(after)
        if before.strip():
            AUDIT.append(dict(figure=stem, before=before, after=after,
                              decision='reworded' if before != after else 'retained'))
    for ax, axis, labels in ticks:
        changed = [REPLACE.get(label, label) for label in labels]
        if changed != labels:
            getattr(ax, 'set_'+axis+'ticks')(getattr(ax, 'get_'+axis+'ticks')(), changed)
    if stem == 'figure2_fact_signal':
        fig.set_size_inches(12.8, 7.2)
        fig.subplots_adjust(top=.73, bottom=.23)
        fig.text(.07, .915, 'Difference in feature overlap = overlap with the same fact, reworded', fontsize=11, fontweight='bold')
        fig.text(.07, .878, '                         minus average overlap with other facts in the same subject and test set.', fontsize=10)
        fig.text(.07, .830, 'Illustration only: 0.50 − 0.30 = +0.20. Above zero means more overlap with the same fact; it is not a percentage increase.', fontsize=9)
    elif stem == 'figure3_fact_and_wording':
        fig.set_size_inches(13.2, 8.5)
        fig.subplots_adjust(top=.68, bottom=.25)
        for ax in fig.axes:
            ax.set_xticks([0, 1, 3, 4], ['Same fact\nnew wording', 'New fact\nsame wording\npattern'] * 2)
            ax.set_xlim(-.65, 4.65)
            ax.tick_params(axis='x', labelsize=9)
        fig.text(.07, .915, 'Difference in similarity = similarity in the labeled comparison minus similarity when BOTH fact and wording change.', fontsize=10, fontweight='bold')
        fig.text(.07, .875, 'Illustrative starting prompt: “The chemical symbol for gold is ...”', fontsize=10)
        for x, heading, example in [
            (.07, 'Same fact, new wording', '“Gold has the chemical symbol ...”\nStill asks about gold; sentence pattern changes.'),
            (.39, 'New fact, same wording pattern', '“The chemical symbol for iron is ...”\nAsks about iron; sentence pattern stays the same.'),
            (.72, 'Baseline: both change', '“Iron has the chemical symbol ...”\nBoth element and sentence pattern change.')]:
            fig.text(x, .827, heading, fontsize=9.5, fontweight='bold')
            fig.text(x, .776, example, fontsize=8.8, linespacing=1.5)
        for t in fig.texts:
            if t.get_text() == 'Baseline: different fact AND different wording. Some outputs are not answers. Qwen3-1.7B was not tested here.':
                t.set_text('Above zero: more similarity than the baseline. Some outputs are not answers. Qwen3-1.7B was not tested here.')
    elif stem == 'figureS1_export_and_error':
        fig.set_size_inches(14, 5.8)
        fig.subplots_adjust(top=.80, bottom=.23, wspace=.32)
        for ax in fig.axes:
            ax.tick_params(axis='x', labelsize=8)
    elif stem == 'figureS2_robustness':
        fig.set_size_inches(14, 6.1)
        fig.subplots_adjust(top=.80, bottom=.29, wspace=.36)
        for ax in fig.axes:
            ax.tick_params(axis='x', labelsize=8)
            for t in ax.get_xticklabels():
                t.set_rotation(22)
    elif stem == 'figureS4_lexical_support':
        fig.subplots_adjust(bottom=.23, top=.74)
        for ax in fig.axes:
            ax.set_title(ax.get_title(loc='left'), loc='left', fontsize=10)
    elif stem == 'figureS5_answer_audit':
        fig.set_size_inches(13, 5.8)
        for ax in fig.axes:
            ax.title.set_fontsize(11)
    elif stem == 'figureS6_graph_location_sensitivity':
        for ax in fig.axes:
            ax.title.set_fontsize(11)
        fig.text(.07, .025, 'Vertical axes: differences in Jaccard overlap. These are checks on saved graphs, not interventions on the model.', fontsize=8.5)

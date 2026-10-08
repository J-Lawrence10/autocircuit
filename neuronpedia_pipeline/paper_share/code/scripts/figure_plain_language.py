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
    'figure4_control_comparisons': 'Made-up-name controls give different results across models',
    'figure5_matched_choice': 'Same-fact versus other-fact overlap depends on the A/B answer',
    'figure6_failure_cases': 'In selected errors, graph similarity follows the answer more than the question',
    'figureS1_export_and_error': 'Graph files have two separate limits: ID conflicts and approximation error',
    'figureS2_robustness': 'Average overlap differences stay positive under alternative graph comparisons',
    'figureS3_equal_feature_counts': 'Average overlap differences stay positive with equal numbers of features',
    'figureS4_lexical_support': 'Other-fact questions share fewer words, leaving a gap in the controls',
    'figureS5_answer_audit': 'A matching first token does not always verify the whole answer',
    'figureS6_graph_location_sensitivity': 'The answer-related differences remain after removing some graph features',
}

CAPTIONS = {
'figure1_design_and_coverage': (
    'A, Compare a question with a reworded question about the same fact and with questions about other facts. '
    'Comparisons stay within the same subject and evaluation group. Gold means the chemical element, not an ideal or gold-standard question. '
    'The gold, iron, and made-up-name examples come from the development questions, not the test questions plotted in Figure 2. '
    'The original samples cover three models, with different subjects available in each. '
    'B, In Qwen3-4B, keep the same words and token counts within each country pair, but change which country is asked about, '
    'which capital is assigned to A or B, and the wording. This tests whether questions about the same fact still share more features when the correct A/B answer changes. '
    'All 48 predicted answer letters were correct. The France/Germany example illustrates the design using a pilot pair, not an additional test pair. '
    'Displayed examples are shortened; full prompts preserve both country names and all other words within a pair. '
    'Word order and the role of each country still differ, so this does not isolate meaning alone. '
    'C, Compare a selected wrong-answer graph with two correct-answer graphs: one answering the intended country and one producing the same answer as the error. '
    'This Qwen3-4B study contains 16 graphs from one country pair and two answer formats, not 16 independent tests. '
    'Arrows show comparison steps, not causes. Box colors identify labeled steps, not quantities. '
    'Collection counts, exclusions, and failed preliminary checks are reported separately.'),
'figure2_fact_signal': (
    'A, Each point represents one test question that passed the fixed inclusion rules. A test question was reserved for evaluation, '
    'rather than for developing the analysis. The difference in feature overlap is the overlap with a reworded version of the same fact minus the average '
    'overlap with reworded questions about other facts in the same subject and test set. '
    'For illustration only, 0.50 overlap with the same fact minus 0.30 average overlap with other facts gives a difference of +0.20. '
    'These example numbers are not measured results. A positive difference means more overlap with the same fact, zero means equal overlap, '
    'and a negative difference means more overlap with the other-fact questions. The difference is not a percentage increase. '
    'B, The same measure is averaged separately by subject. Colors and shapes identify subjects; diamonds show model averages. '
    'Bars are saved 95% bootstrap intervals, obtained by resampling questions 10,000 times. n counts questions, not graph pairs. '
    'Averages are 0.170 for Gemma-2-2B (8 questions), 0.085 for Qwen3-1.7B (5), and 0.162 for Qwen3-4B (10). '
    'The same facts recur across models, and subject coverage differs, so these results do not rank the models. '
    'Shared words and shared answers remain possible explanations. Missing subject groups are unavailable comparisons, not zero effects. '
    '*The original Qwen3-4B collection is incomplete: 145 of 147 planned graphs are available.'),
'figure3_fact_and_wording': (
    'A, Difference in feature overlap. B, Difference in similarity when each feature is weighted by its saved graph-influence score '
    '(cosine similarity, which compares the direction of the weighted feature vectors). '
    'For both panels, the baseline is a pair of questions differing in both fact and wording. '
    'The same-fact comparison changes the wording; the same-wording comparison changes the fact. '
    'For example, compare “The chemical symbol for gold is ...” with “Gold has the chemical symbol ...” to keep the fact but change the wording. '
    'Compare the starting prompt with “The chemical symbol for iron is ...” to keep the wording pattern but change the fact. '
    'Compare it with “Iron has the chemical symbol ...” to change both: this is the baseline. These examples illustrate the comparisons. '
    '“Same wording” means the same sentence pattern, not an identical prompt; the element name must change. '
    'Each difference is similarity in the labeled comparison minus similarity in that baseline, calculated within each subject. Panel A counts which features are shared; '
    'panel B also considers their saved influence weights. Neither panel directly measures correctness. '
    'Each model has 27 graphs: three facts, three wordings, and three subjects. Colored points are subject averages; black diamonds '
    'average the subjects equally. Lines connect descriptive estimates, not confidence intervals. '
    'Average fact/wording differences in A are 0.074/0.118 for Gemma-2-2B and 0.101/0.064 for Qwen3-4B. '
    'Some first predicted tokens are incomplete answers or not answers at all. Only Qwen3-4B geography matches the expected first token '
    'in all nine questions; its fact/wording differences are 0.101/0.106. These results do not establish that one factor dominates '
    'or that one model is better. Qwen3-1.7B was not tested in this design.'),
'figure4_control_comparisons': (
    'Replace the real name in a question with a made-up name, either keeping the original wording (A) or rewording the question (B). '
    'For each target question, subtract its overlap with the made-up-name version from its overlap with a reworded factual version. '
    'Above zero favors the factual version; below zero favors the made-up-name version. Colors identify models, points represent test questions, '
    'diamonds show averages, and bars are saved 95% bootstrap intervals from resampling questions. n counts included questions. '
    'The controls match only the kind of first token: letters/numbers, whitespace, or punctuation/symbols. They do not match the exact answer, '
    'its meaning, confidence, or correctness. Averages in A are -0.069 (2 questions), -0.014 (4), and +0.096 (10) for Gemma-2-2B, '
    'Qwen3-1.7B, and Qwen3-4B. Small samples and different subject coverage prevent a general claim that wording explains the original result. '
    '*The original Qwen3-4B collection is incomplete (145/147 graphs).'),
'figure5_matched_choice': (
    'Qwen3-4B only: six country pairs and 48 correct predicted A/B answers. This follow-up was designed after earlier results were seen; '
    'its rules were fixed before collection. The words and token counts are identical within each country pair. '
    'A, Average overlap for questions asking about the same or different countries and producing the same or different A/B letters. '
    'All comparisons change the wording. The four averages are 0.8005, 0.4853, 0.7377, and 0.4874, read row by row. '
    'The color scale runs from no shared features (0) to identical feature sets (1); it is not an accuracy scale. '
    'B, Subtract different-country overlap from same-country overlap, separately when the answer letter stays the same or changes. '
    'The averages are 0.0628 and -0.0022. Their paired difference is 0.0650 (exploratory Student-t 95% interval 0.0553–0.0746; '
    'two-sided sign-flip p=0.03125, assuming independent country pairs and symmetric differences under the null). '
    'C, Average the two fact differences in B: 0.0303, with a saved 95% bootstrap interval of 0.0265–0.0338. '
    'For comparison, overlap with the same answer letter minus overlap with a different letter is 0.2827, averaged across same- and different-country comparisons. '
    'Each line in B–C represents one country pair; diamonds mark averages. Only the fact average in C has an interval drawn. '
    'Colors identify the labeled categories; B and C have different vertical scales. Six country pairs—not 48 graphs or 4,096 possible '
    'reassignments in the earlier null test—supply the independent units assumed by the statistical tests. '
    'A near-zero estimate does not prove no effect. These differences are not fractions of reasoning explained and do not establish a cause. '
    'Word order and country roles remain possible explanations. Supplement S6 checks whether the differences remain after excluding some features.'),
'figure6_failure_cases': (
    'A, In 16 new Qwen3-4B graphs, all eight questions naming the country are answered correctly and all eight selected questions referring '
    'to its position reproduce the error. Each answer format has four correct and four wrong responses. These selected cases do not estimate '
    'how often the model makes errors in general. B–C, Compare each wrong-answer graph with a correct response to the intended country (blue) '
    'and a correct response giving the same answer as the error (orange). The country-list order and A/B assignments stay fixed. '
    'For example, with France first and A: Berlin, B: Paris, an indirect question about France produces Berlin. Naming France produces Paris; '
    'naming Germany produces Berlin. The error graph is more similar to the Germany/Berlin graph. '
    'Circles use all retained features; open squares use equal numbers of randomly sampled features, averaged over 200 repetitions. '
    'Lines connect comparisons for the same error. The same-answer minus intended-country overlap averages 0.1983 for A/B answers and '
    '0.2649 for capital names (0.1851 and 0.2361 after equalizing feature counts). All 16 exports and eight three-graph comparisons pass the '
    'file-integrity and output checks. The cases share one country pair and overlapping controls, so no population confidence intervals or '
    'confirmatory p-values are shown. These comparisons do not keep the exact words constant. Confusing list positions, mishandling negation, '
    'or graph structure tied to the produced answer remain possible explanations—not established causes. '
    'The correct-answer output node is missing from each error graph; its contribution is unknown, not zero.'),
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
    'they are not the question counts in Figure 2. Qwen3-4B is missing one factual graph and one made-up-name graph. '
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
    'Factual-paraphrase overlap minus\nmade-up-name overlap (Jaccard difference)': 'Overlap with reworded fact minus\noverlap with made-up-name question',
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

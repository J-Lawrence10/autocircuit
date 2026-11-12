"""Guard the revised narrative's scope and reported values; not scientific validation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'
if not SOURCE.exists():
    SOURCE = ROOT.parent/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'


def manuscript():
    return SOURCE.read_text(encoding='utf-8')


def test_a2_distinguishes_graph_checks_residuals_and_rule_derived_subset():
    section = manuscript().split('### A2 Graph-file checks and reconstruction error\n\n', 1)[1].split('### A3 ', 1)[0]
    for value in ['84/120', '13/27', '91 Qwen3-1.7B', '147 Qwen3-4B',
                  '7.15%', '6.06%', '14.57%', '0.1704 to 0.1692',
                  '0.0894 to 0.0887', '0.2183 to 0.2153']:
        assert value in section
    assert 'Reconstruction-error nodes represent activity that this approximation does not capture.' in section
    assert 'not an incorrect model answer' in section
    assert 'uniquely identified internal nodes, excluding input embeddings and output logits' in section
    assert 'No reconstruction-error threshold was used to exclude graphs.' in section
    assert 'main analysis included eight Gemma evaluation facts' in section
    assert 'Only two Gemma facts qualified, corresponding to four factual-question graphs' in section
    assert 'a supporting check, not a replacement for the main analysis' in section
    assert 'the outcome of that rule, not a selected sample-size cutoff' in section
    assert 'grouped by error type and layer rather than treated as learned features' in section
    assert 'restriction to starting-question and factual-rewording exports without detected node-ID conflicts' in section


def test_a3_explains_selected_source_locations_and_distinct_error_denominator():
    section = manuscript().split('### A3 Connections to the predicted answer in selected errors\n\n', 1)[1].split('### A4 ', 1)[0]
    assert '16 selected Qwen3-4B graphs' in section
    assert 'eight incorrect predictions and eight correct named-country controls' in section
    assert '4.9–14.6 times' in section
    assert 'four incorrect A/B predictions did not show a consistent preference' in section
    assert 'A: Berlin. B: Paris. Countries: France, Germany.' in section
    assert 'first country, not the second? Answer:' in section
    assert 'Berlin was both the first answer option and the capital of the second country.' in section
    assert 'selected prompt layouts do not distinguish between them' in section
    assert 'median 23.1%' in section and '17.2–31.4%' in section
    assert 'only connections entering the predicted answer’s output node' in section
    assert 'A2 summarized influence across internal graph nodes' in section
    assert 'absent from all eight error graphs' in section
    assert 'does not mean that their contribution in the model was zero' in section
    assert 'not what a learned feature represents' in section


def test_a4_explains_comparison_support_and_limits_of_sensitivity_checks():
    section = manuscript().split('### A4 Checks on wording, feature counts, and graph locations\n\n', 1)[1].split('### A5 ', 1)[0]
    assert 'pairs differing in both fact and version as their baseline' in section
    assert 'a shared version label did not guarantee identical wording' in section
    for value in ['0.074 and 0.118', '0.101 and 0.064', '0.090 and 0.114',
                  '0.105 and 0.075', '0.1014 and 0.1063']:
        assert value in section
    assert 'a gap in the available comparisons, not a measured zero effect' in section
    assert 'tungsten, changed from a positive to a negative difference' in section
    assert 'cannot be interpreted as the percentage of the original difference explained by graph size' in section
    assert 'ordinary least-squares intercept with centered predictors equals the original sample mean by construction' in section
    assert 'Across all six country pairs' in section
    assert 'All eight selected error comparisons' in section
    assert 'filters changed the saved graph representations, not the model’s activity or predictions' in section
    for figure in ['S10', 'S4', 'S3', 'S6']:
        assert f'**Figure {figure}.' in section


def test_a5_separates_model_specific_history_coverage_and_control_definitions():
    section = manuscript().split('### A5 Qwen3-1.7B results in chemistry and geography\n\n', 1)[1].split('### A6 ', 1)[0]
    assert '91 available graphs provided 19 facts' in section
    assert 'evaluation sample contained five chemistry and five geography facts' in section
    assert 'Four of the ten history facts had no returned graphs' in section
    assert 'No history fact had a complete question/control set for Qwen3-1.7B' in section
    assert 'completed Qwen3-4B history analyses are reported separately in Section 3.6 and Supporting analyses A1 and A7' in section
    assert 'Positive values favor the factual rewording; negative values favor the comparator' in section
    assert 'same-pattern comparison’s interval then included zero' in section
    assert 'general categories of predicted tokens, not identical answers' in section
    assert 'not additional independent facts' in section
    assert 'retained the original comparison pools rather than rebuilding them' in section
    assert 'These analyses are exploratory' in section
    assert 'reconstruction-error diagnostic in A2, which imposed no percentage cutoff' in section


def test_a6_distinguishes_primary_workflow_from_illustrative_examples():
    section = manuscript().split('### A6 Feature-overlap analysis workflow\n\n', 1)[1].split('### A7 ', 1)[0]
    assert 'applying the inclusion rules in Section 2.2' in section
    assert 'set of unique learned features' in section
    assert 'its own factual rewording, then subtract its average overlap with rewordings of other facts' in section
    assert 'same model, subject area, and development or evaluation set' in section
    assert 'one difference per included fact' in section
    assert 'Invented name controls provide a separate comparison.' in section
    assert 'Gold refers to the chemical element, while zorium is an invented name' in section
    assert 'feature letters and numerical scores are illustrative, not measured values' in section
    assert 'historical-date analyses retain their own comparisons and inclusion rules' in section


def test_a7_defines_answer_letters_comparison_units_and_uncollected_evaluation():
    section = manuscript().split('### A7 Historical-date comparisons\n\n', 1)[1].split('### A8 ', 1)[0]
    assert 'required letter was the A or B assigned to the correct year' in section
    assert 'predicted letter was the response the model actually produced' in section
    assert 'All 11 correct and five incorrect predictions were retained' in section
    assert 'produced 16 comparisons per event pair' in section
    assert 'Each mean summarized eight graph pairs' in section
    assert 'Each cell below averages four comparisons' in section
    assert 'all 56 unordered graph comparisons: 28 within each event pair' in section
    for value in ['0.7396', '0.5075', '0.7758', '0.5614', '0.1268', '0.0015', '0.0686', '0.0210']:
        assert value in section
    assert 'not additional filtered tests of the predicted-letter grouping' in section
    assert 'average across repetitions, not to every repetition being positive' in section
    assert '160 graphs from 20 event pairs' in section
    assert 'at least 16 complete, correct-answer event pairs, including at least six from each theme' in section
    assert 'That estimate was therefore not measured.' in section
    assert 'before graph collection but after the preview answers were known' in section
    assert 'does not complete the uncollected 160-graph evaluation or add facts to the original three-model comparison' in section


def test_a8_separates_public_package_historical_reproduction_and_permissions():
    section = manuscript().split('### A8 Data, code, and reproducibility records\n\n', 1)[1].split('## Reproducibility and availability', 1)[0]
    assert '23 original fact-level overlap differences from 342' in section
    assert 'passed 82 software tests' in section
    assert 'not the final 8/10/12-fact sample' in section
    assert 'checked hashes for all 91 raw inputs' in section
    assert 'recomputed the 56 pairwise Jaccard comparisons' in section
    assert '147 Qwen3-4B raw-file hashes and recomputed 54 Jaccard comparisons' in section
    assert 'not a single independent end-to-end reproduction' in section
    assert 'run with `--reviewed`, checks' in section
    assert 'Adding `--write` updates manuscript captions' in section
    assert 'Credentials and private API configuration are excluded for security' in section
    assert 'Protocols were locally frozen, not publicly preregistered' in section
    assert 'The latest locally approved manuscript revisions await' not in section


def test_results_follow_question_controls_answer_errors_checks_scope():
    text = manuscript()
    headings = re.findall(r'^### 3\.\d+ (.+)$', text, re.M)
    assert headings == [
        'Reworded questions about the same fact share more features',
        'Same-fact questions share words and expected answers',
        'Same-fact overlap is higher when the answer letter stays the same',
        'Error graphs show greater overlap with answer-matched controls',
        'Greater same-fact feature sharing persists after matching feature counts',
        'History graphs can remain similar when the selected year changes',
    ]
    assert text.index('## Supporting analyses') > text.index('## 5. Conclusion')


def test_primary_and_exploratory_outcomes_remain_distinct():
    text = manuscript()
    assert 'Their average, the prespecified primary outcome, was 0.0303' in text
    assert 'The exploratory direct paired difference' in text
    for value in ['0.0628', '-0.0022', '0.0265–0.0338', '0.000244141',
                  '0.000732422', '0.0650', '0.0553–0.0746', 'p=0.03125', '0.2827']:
        assert value in text


def test_answer_letter_contrast_is_explicit_and_separate_from_primary_outcome():
    text = manuscript()
    results = text.split('### 3.3 Same-fact overlap is higher when the answer letter stays the same\n\n', 1)[1].split('### 3.4 ', 1)[0]
    paragraphs = results.split('\n\n')
    paragraph = next(p for p in paragraphs if p.startswith('Attribution graphs shared substantially more features'))
    assert '0.8005 with the same answer letter and 0.4853 with different letters, a difference of 0.3152 (Figure 4a)' in paragraph
    assert 'Questions about different countries showed the same pattern, with overlaps of 0.7377 and 0.4874, respectively' in paragraph
    assert 'letter-associated difference of 0.2827, positive in all six country pairs' in paragraph
    assert 'All 48 predictions were correct' in paragraph
    assert 'even when the country and correct capital remained unchanged' in paragraph
    assert 'separate descriptive overlap contrast, not a fraction of variance or reasoning explained' in paragraph
    assert 'prespecified primary outcome, was 0.0303' in results
    assert 'exploratory direct paired difference' in results
    assert 'word order, answer mapping, country roles, and output-conditioned graph construction remain possible contributors' in results


def test_selected_error_results_explain_controls_and_preserve_scope():
    text = manuscript()
    results = text.split('### 3.4 Error graphs show greater overlap with answer-matched controls\n\n', 1)[1].split('### 3.5 ', 1)[0]
    first, second, third = results.strip().split('\n\n')[:3]
    assert 'whether graph similarity also followed the predicted answer when that answer was wrong' in first
    assert 'Naming France directly produced the correct B or Paris response; naming Germany produced the correct A or Berlin response' in first
    assert 'correct France prediction for the intended country (Figure 5b,c)' in first
    assert '8/16 correct A/B predictions and stopped at its fixed accuracy requirement' in second
    assert '20-question diagnostic passed all four checks using direct instructions or previously successful questions' in second
    assert 'All eight questions naming the country directly produced the intended next token' in second
    assert 'all eight selected questions identifying the country by its list position reproduced errors' in second
    assert '(Figure 5a)' in second
    assert 'The planned evaluation following the failed preliminary check was not conducted' in second
    assert 'All 16 diagnostic graphs passed integrity checks and reproduced their archived preview answers' in third
    assert 'two correct-answer graphs: one for the intended country and one producing the same answer as the error' in third
    assert 'Every comparison favored the graph sharing the error’s answer (Figure 5b,c)' in third
    for value in ['0.1983', '0.2649', '0.1851', '0.2361']:
        assert value in third
    assert 'influence-weighted cosine similarity preserved the direction in all eight comparisons' in third
    assert 'shared control graphs and concerned only France and Germany' in third
    assert 'selected cases rather than eight independent replications' in third


def test_filtered_error_results_and_graph_size_bridge_preserve_scope():
    text = manuscript()
    errors = text.split('### 3.4 Error graphs show greater overlap with answer-matched controls\n\n', 1)[1].split('### 3.5 ', 1)[0]
    filtered, limits = errors.strip().split('\n\n')[3:5]
    assert 'all eight selected comparisons' in filtered
    assert 'final input-token position, in the last quarter of observed feature layers, or both' in filtered
    assert '0.2053 for labels and 0.2608 for capital names (Supplementary Figure S6b)' in filtered
    assert 'changed the graphs used for comparison, not the model itself' in filtered
    assert 'still constructed to explain the predicted answer' in filtered
    assert 'do not estimate how frequently the model makes this mistake' in limits
    assert 'selecting answer options by position and misinterpreting phrases' in limits
    assert 'Both explanations predict the same errors' in limits
    assert 'Supporting analysis A3' in limits
    assert 'missing output nodes for the intended correct answers' in limits
    size = text.split('### 3.5 Greater same-fact feature sharing persists after matching feature counts\n\n', 1)[1].split('\n\n', 1)[0]
    assert 'original three-model pattern' in size
    assert 'Within each model and subject area' in size
    assert 'sampling equal numbers of features from the starting and reworded factual graphs' in size
    assert 'repeated it with half as many' in size
    assert 'Mean same-fact-minus-other-fact overlap remained positive for all three models at both sample sizes (Supplementary Figure S3)' in size


def test_equal_count_results_define_table_units_and_sampling_limits():
    text = manuscript()
    results = text.split('### 3.5 Greater same-fact feature sharing persists after matching feature counts\n\n', 1)[1].split('### 3.6 ', 1)[0]
    assert 'K is the smallest number of distinct features among the included starting and reworded factual graphs within each model and subject area' in results
    assert 'K/2 is half that number, rounded down' in results
    assert 'mean same-fact-minus-other-fact Jaccard differences, not raw overlap scores' in results
    assert '| Gemma-2-2B | 0.170 | 0.149 [0.066, 0.257] | 0.058 | 7/8 |' in results
    assert '| Qwen3-1.7B | 0.089 | 0.084 [0.076, 0.092] | 0.033 | 10/10 |' in results
    assert '| Qwen3-4B | 0.218 | 0.181 [0.110, 0.267] | 0.072 | 12/12 |' in results
    assert '200 sampling repetitions at both feature counts' in results
    assert 'After averaging across repetitions' in results
    assert 'seven of eight Gemma questions, all ten Qwen3-1.7B questions, and all twelve Qwen3-4B questions had positive differences at K' in results
    assert '−0.0187 at K and −0.0080 at K/2' in results
    assert 'the 200 repetitions are not additional independent observations' in results
    assert 'Subsampling can retain a shared feature in one graph while removing it from another' in results
    assert 'cannot be interpreted as the percentage of the original association explained by graph size' in results
    assert 'Supplementary Figure S3' in results
    assert 'Supplementary Figures S5 and S1–S2' in results
    assert 'earlier size-regression calculation was not an independent robustness check' in results


def test_original_results_and_limitations_are_retained():
    text = manuscript()
    for value in ['0.170', '0.085', '0.218', '0.1983', '0.2649', '0.1851',
                  '0.2361', '−0.0187', '−0.0080', '385', '15/20', '20/20',
                  '23.1%', '17.2–31.4%', '4.9–14.6', '8/16']:
        assert value in text
    for phrase in ['rather than eight independent replications', 'not an equivalence',
                   'not causal ablations', 'Only 15 were correct, so the larger evaluation did not proceed.',
                   'Both explanations predict the observed error, and the selected prompt layouts do not distinguish between them.',
                   'Partial answer tokens did not qualify.',
                   'Later generated tokens were not recorded, so partial beginnings were kept separate from verified complete answers.']:
        assert phrase in text


def test_current_figures_and_public_availability_are_consistent():
    text = manuscript()
    assert '**Working manuscript. Not peer reviewed.**' in text
    images = re.findall(r'!\[Figure (S?\d+):', text)
    assert set(images) == {str(i) for i in range(1, 7)} | {f'S{i}' for i in range(1, 11)}
    assert len(images) == 16
    assert 'No data were published or submitted externally' not in text
    assert 'GitHub main branch' in text
    assert 'https://github.com/J-Lawrence10/autocircuit/tree/main/neuronpedia_pipeline/paper_share' in text
    assert 'Raw Neuronpedia exports, full feature caches, tokenizer/model files, and downloaded reference PDFs are excluded' in text
    assert 'Credentials and private API configuration are excluded for security' in text
    assert 'Sharing copy updated 8 October' not in text


def test_reader_gets_measurement_and_bridges_before_details():
    text = manuscript()
    assert '### 2.2 Measuring feature overlap' in text
    assert 'We measured feature sharing between questions using Jaccard similarity, our measure of feature overlap.' in text
    assert 'the number of shared features divided by the total number of distinct features across both graphs' in text
    assert 'Attribution graphs show patterns of activity inside a model and estimate how those patterns contribute to its prediction' in text
    assert 'questions containing two countries and two capitals labeled A and B' in text
    assert 'Both named-country predictions were correct for their respective questions' in text
    assert 'When the model had to answer with different letters, questions asking for the same capital had nearly the same average feature overlap as questions about different countries.' in text
    assert 'The factual answer remained the same, but the greater feature overlap observed with a shared answer letter did not persist.' in text
    assert 'using the tuple `(feature family, layer, feature ID)`' in text
    assert 'Matching numerical IDs in different layers or feature families remained distinct.' in text
    assert 'A feature that appeared at multiple positions in the input was counted once.' in text
    assert 'nodes with missing or duplicated graph-node identifiers' in text
    assert 'Features were compared only between graphs from the same model.' in text
    assert 'Higher overlap could reflect more than the fact being asked about' in text
    assert 'The matched-choice study used correct predictions. We next asked' in text
    assert 'Prespecified conditional correspondence test' in text
    assert 'Exploratory block sign-flip test' in text
    assert 'exchangeable conditional on the label and word inventory' in text


def test_opening_results_link_claims_to_their_figure_panels():
    text = manuscript()
    opening = text.split('### 3.1 Reworded questions about the same fact share more features\n\n', 1)[1].split('![Figure 2:', 1)[0]
    paragraphs = opening.strip().split('\n\n')
    assert len(paragraphs) == 4
    assert 'Across all three models, every included evaluation question had greater Jaccard overlap' in paragraphs[0]
    assert 'rewordings of other facts (Figure 2a)' in paragraphs[0]
    for value in ['0.170', '[0.085, 0.276]', 'n=8', '0.0894', '[0.0820, 0.0976]',
                  'n=10', 'n=12', '0.218', '[0.150, 0.307]', '0.00390625', '0.0009765625',
                  '0.000244140625', '0.00139', '0.0000694', '0.0000347']:
        assert value in paragraphs[0]
    assert 'prevent interpreting these effect sizes as a model ranking' in paragraphs[0]
    assert 'all five geography evaluation facts had positive overlap differences' in paragraphs[1]
    assert 'subject means of 0.0854 and 0.0935 (Figure 2b)' in paragraphs[1]
    assert 'no history fact had a complete set of factual and control graphs (Supplementary Figure S7a)' in paragraphs[1]
    assert 'Supporting analysis A5' in paragraphs[1]
    assert 'Qwen3-4B included five chemistry, five geography, and two history facts' in paragraphs[2]
    assert '0.601 and 0.395' in paragraphs[2] and '0.498' in paragraphs[2]
    assert 'Supplementary Figure S9a' in paragraphs[2]
    assert 'reworded questions may also share words and the expected answer' in paragraphs[3]
    assert 'examined whether these similarities could explain the pattern' in paragraphs[3]


def test_supporting_figures_do_not_interrupt_main_results():
    text = manuscript()
    main = text.split('## Supporting analyses')[0]
    assert not re.search(r'!\[Figure S\d+:', main)
    assert '### A4 Checks on wording, feature counts, and graph locations' in text
    assert '### 4.2 Graph similarity and factual correctness can diverge' in text
    assert 'ordinary least-squares intercept with centered predictors equals' in text


def test_primary_comparison_is_explained_before_equation_and_links_workflow():
    text = manuscript()
    methods = text.split('### 2.2 ', 1)[1].split('### 2.3 ', 1)[0]
    assert methods.index('For each starting question, we calculated Jaccard overlap') < methods.index('`M_i =')
    assert 'every other included fact from the same model, subject, and development or evaluation set' in methods
    assert 'Figure S8 summarizes the workflow.' in methods
    assert '### A6 Feature-overlap analysis workflow' in text
    assert 'the fact/wording, answer-letter, selected-error, and historical-date analyses retain their own comparisons and inclusion rules' in text


def test_primary_methods_define_sets_inclusion_and_statistical_units():
    text = manuscript()
    methods = text.split('### 2.2 ', 1)[1].split('### 2.3 ', 1)[0]
    assert 'Let T_i and P_i denote the feature sets from the graphs' in methods
    assert 'mean_{j ≠ i}' in methods
    assert 'all four question and control graphs were available' in methods
    assert 'removing leading and trailing whitespace, such as spaces or line breaks' in methods
    assert 'At least one other fact also had to meet these conditions' in methods
    assert 'descriptive 95% percentile bootstrap interval' in methods
    assert '10,000 resamples of the calculated fact-level differences with replacement' in methods
    assert 'Exact one-sided sign-flip tests assessed whether the mean difference was greater than zero.' in methods
    assert '30 model-specific fact observations, not 30 unique independent facts' in methods
    assert 'scoring error identified during the audit' in methods
    assert 'used the corrected inclusion decisions throughout the reported analyses' in methods
    assert 'within-subject' not in text


def test_crossed_design_distinguishes_version_labels_from_exact_templates():
    text = manuscript()
    methods = text.split('### 2.3 ', 1)[1].split('### 2.4 ', 1)[0]
    assert '27 graphs per model' in methods
    assert 'The version labels did not imply identical sentence patterns across facts.' in methods
    assert 'questions differing in fact and version as their baseline' in methods
    assert 'varied factual content and sentence pattern separately' not in text
    assert 'The average same-fact and same-version Jaccard differences were' in text
    assert '0.074 and 0.118 for Gemma' in text and '0.101 and 0.064 for Qwen3-4B' in text


def test_invented_name_control_paragraph_leads_with_purpose_and_defines_matching():
    text = manuscript()
    methods = text.split('### 2.3 ', 1)[1].split('### 2.4 ', 1)[0]
    assert 'We compared factual rewordings against invented name prompts, then checked whether the pattern persisted when their predicted outputs had the same general form.' in methods
    assert 'One control was based on the starting sentence pattern; the other used a reworded version.' in methods
    assert 'Positive differences therefore favored the factual rewording.' in methods
    assert 'same broad category as the starting question’s' in methods
    assert 'containing letters or numbers, whitespace only, or punctuation/symbols only' in methods
    assert 'This matched output category, not the exact token, its meaning, or its probability.' in methods


def test_exploratory_checks_define_matching_and_keep_sampling_units():
    text = manuscript()
    methods = text.split('### 2.4 ', 1)[1].split('### 2.5 ', 1)[0]
    assert 'File checksums covered all 385 graphs' in methods
    assert 'an absolute tolerance of 10⁻¹²' in methods
    assert 'starting and reworded evaluation graphs' in methods
    assert '200 repetitions with recorded fixed seeds' in methods
    assert 'model-specific seeds are retained in the reproducibility tables' in methods
    assert '10,000 fact-level resamples' in methods
    assert 'each sampled graph was reused in all its comparisons' in methods
    assert 'three alternative matching rules' in methods
    assert 'scores to differ by no more than 0.05' in methods
    assert "other-fact rewording's graph to contain between 80% and 125% as many features as the factual rewording's graph" in methods
    assert 'not estimable, rather than zero' in methods
    assert 'Matching thresholds were not relaxed after inspection.' in methods
    assert 'answer matching was not an inclusion requirement' in methods


def test_token_audit_and_complete_group_scope_are_preserved():
    text = manuscript()
    methods = text.split('### 2.4 ', 1)[1].split('### 2.5 ', 1)[0]
    assert 'versions and file checksums of the official Qwen tokenizers' in methods
    assert 'requiring the prompt’s token sequence to remain unchanged' in methods
    assert 'complete expected answers, compatible beginnings, whitespace-only matches, mismatches, and unresolved checks' in methods
    assert 'A compatible beginning did not verify that the model would complete the answer correctly.' in methods
    assert 'could not establish the exact tokenizer version used during graph collection' in methods
    assert 'authorization error (HTTP 401)' in methods
    assert 'three facts from one subject area, each asked in three versions' in methods
    assert 'only when all nine questions had highest-probability next tokens matching the expected text' in methods
    assert 'reported them separately from the original analysis' in methods
    assert 'did not select individual passing questions from groups that failed the rule' in methods


def test_matched_choice_keeps_design_statistics_and_plain_paragraph_structure():
    text = manuscript()
    choice = text.split('### 2.5 Matched-choice follow-up separating queried country and answer label\n\n', 1)[1].split('### 2.6 ', 1)[0]
    assert len(choice.strip().split('\n\n')) == 3
    assert 'compared graphs across the two wordings' in choice
    assert 'subtracted different-country overlap from same-country overlap in each answer-letter condition' in choice
    assert 'prespecified primary outcome' in choice
    assert 'six country pairs, not 48 independent graphs' in choice
    assert '95% bootstrap interval from 10,000 resamples' in choice
    assert '4,096 allowed assignments' in choice and 'Bonferroni correction' in choice
    assert 'original Qwen and Gemma setups and the revised Qwen chat setup' in choice
    assert 'rules were fixed before collecting the evaluation graphs' in choice
    assert 'giving four correct labels' in choice and 'none of the eight requested letters' in choice
    assert '###' not in choice


def test_current_qwen_sample_and_negative_controls_are_used_consistently():
    text = manuscript()
    assert '| Qwen3-1.7B | 91/120 | Not collected | 10: chemistry 5, geography 5 |' in text
    assert '91 collected graphs comprised 40 chemistry, 40 geography, and 11 history graphs' in text
    assert 'These are collection failures, not incorrect predictions.' in text
    assert 'All five chemistry and all five geography evaluation facts' in text
    for number in ['0.0935', '0.0894', '[0.0820, 0.0976]', '-0.0114', '-0.0109', '0.1059',
                   '0.0835', '0.0331', '0.00016', '0.1934', '14,400']:
        assert number in text
    assert 'exploratory rather than an independent confirmatory replication' in text
    assert 'eight of its ten evaluation questions shared more features with the same-pattern invented name control' in text
    assert 'no history fact had a complete set of factual and control graphs' in text
    assert 'Shorter history prompts were not generated or substituted' in text
    results = text.split('### 3.1 ', 1)[1].split('### 3.3 ', 1)[0]
    assert '0.0894 for Qwen3-1.7B ([0.0820, 0.0976], n=10)' in results
    assert '108 directed other-fact comparisons' in results
    assert '0.085 for Qwen3-1.7B' not in results
    assert '0/5 Qwen3-1.7B' not in results


def test_figure_captions_match_authoritative_wording():
    import sys
    import json
    sys.path.insert(0, str(ROOT/'scripts'))
    if (ROOT/'data/model_extension/paper_review_20261111').exists():
        from review_figure_catalog import catalog
        entries = catalog()
    else:
        manifest = json.loads((ROOT.parent/'provenance/final_figure_manifest.json').read_text(encoding='utf-8'))
        entries = manifest['figures'] + manifest['supplements']
    text = manuscript()
    for row in entries:
        number, title, caption = row['label'], row['title'], row['legend']
        assert f'![Figure {number}: {title}]' in text
        assert f'**Figure {number}. {title}.** {caption}' in text


def test_history_results_retain_errors_and_follow_figure_panel_order():
    text = manuscript()
    results = text.split('### 3.6 ', 1)[1].split('## 4. Discussion', 1)[0]
    assert 'including 11 correct and five incorrect predictions' in results
    assert 'changed the selected year from 1776 to 1783' in results
    assert 'retained the correct year, 1776; overlap was 0.512 (Figure 6a)' in results
    assert '0.795–0.911' in results and '0.512–0.532 (Figure 6b)' in results
    assert '0.766–0.808' in results and '0.527–0.602 (Figure 6c)' in results
    assert results.index('(Figure 6a)') < results.index('(Figure 6b)') < results.index('(Figure 6c)')
    assert 'Supporting analysis A7' in results
    methods = text.split('### 2.7 ', 1)[1].split('### 2.8 ', 1)[0]
    assert "after the prompts' behavioral outcomes were known" in methods
    assert 'descriptive comparisons rather than population confidence intervals or significance tests' in methods
    supplement = text.split('### A7 ', 1)[1].split('## Reproducibility', 1)[0]
    assert 'Only 15 were correct, so the larger evaluation did not proceed.' in supplement
    assert 'All 11 correct and five incorrect predictions were retained.' in supplement
    assert '15/20' in supplement and '20/20' in supplement
    assert 'Grouping by the required letter did not produce the same consistent pattern as grouping by the predicted letter.' in supplement
    assert '0.1268' in supplement and '0.0015' in supplement


def test_discussion_connects_fact_response_and_correctness_without_changing_scope():
    text = manuscript()
    section = text.split('### 4.1 What the comparisons establish\n\n', 1)[1].split('### 4.2 ', 1)[0]
    paragraphs = section.strip().split('\n\n')
    assert len(paragraphs) == 2
    assert paragraphs[0].startswith('Rewordings of the same fact shared more attribution-graph features')
    assert 'all three analyzed model samples (Figure 2)' in paragraphs[0]
    assert 'persisted after equalizing feature counts' in paragraphs[0]
    assert '(Supplementary Figure S3)' in paragraphs[0]
    assert 'combined association, rather than a measure specific to the requested fact' in paragraphs[0]
    assert 'concentrated in comparisons sharing an answer letter' in paragraphs[1]
    assert 'selected error graphs favored correct predictions giving the same response (Figures 4 and 5)' in paragraphs[1]
    assert 'response letter from agreement on the selected year (Figure 6)' in paragraphs[1]
    assert 'predicted response must be considered when interpreting feature overlap' in paragraphs[1]


def test_discussion_interprets_overlap_without_repeating_scoring_accounting():
    text = manuscript()
    section = text.split('### 4.2 Graph similarity and factual correctness can diverge\n\n', 1)[1].split('### 4.3 ', 1)[0]
    paragraphs = section.strip().split('\n\n')
    assert len(paragraphs) == 4
    assert 'Graph similarity therefore changed without a loss of factual accuracy' in paragraphs[0]
    assert all(f'(Figure {number})' in paragraphs[0] for number in (4, 5, 6))
    assert 'Jaccard overlap quantifies feature sharing' in paragraphs[1]
    assert 'requested fact, predicted response, and answer correctness together' in paragraphs[1]
    assert 'all three analyzed model samples' in paragraphs[2]
    assert 'experiments separating fact identity from the answer letter were conducted in Qwen3-4B' in paragraphs[2]
    assert 'small samples and shared comparison graphs do not establish how frequently' in paragraphs[2]
    assert 'Both could contribute.' in paragraphs[3]
    assert 'model’s computation, the way that computation is measured, or their interaction' in paragraphs[3]
    methods = text.split('### 2.2 ', 1)[1].split('### 2.3 ', 1)[0]
    assert 'highest-probability next token had to give the complete accepted answer' in methods
    assert 'Partial answer tokens did not qualify.' in methods
    supplement = text.split('### A1 ', 1)[1].split('### A2 ', 1)[0]
    assert 'Later generated tokens were not recorded, so partial beginnings were kept separate from verified complete answers.' in supplement
    assert 'Independent statistical review should' not in section


def test_a1_opening_explains_scoring_counts_and_history_without_changing_results():
    text = manuscript()
    first, second, third = text.split('### A1 Next-token matching and complete answers\n\n', 1)[1].split('\n\n')[:3]
    assert first.startswith('We counted a factual prediction as complete only when')
    assert 'highest-probability next token matched an accepted answer in full' in first
    assert 'Among 50 available Qwen3-1.7B factual prompt graphs, 42 predict' in first
    assert 'Among 60 Qwen3-4B factual graphs, the corresponding counts are 50, five, and five' in first
    assert 'These totals count individual prompts, not included evaluation facts.' in first
    assert 'Equivalent spellings counted as the same accepted answer.' in second
    assert '`Maria` and its rewording predicts `María`' in second
    assert 'all four required prompt graphs' in second
    assert 'high feature overlap does not require identical output-token text' in third
    for number in ['0.624', '0.023', '0.427', '0.032', '0.543', '0.370', '0.210', '0.151']:
        assert number in third
    assert '200 random subsamples of the existing graphs, not additional independent observations' in third


def test_a1_control_and_token_paragraphs_preserve_inclusion_and_error_distinctions():
    supplement = manuscript().split('### A1 ', 1)[1].split('### A2 ', 1)[0]
    assert 'starting prompt shared more features with its factual rewording than with either invented name control' in supplement
    for value in ['0.537', '0.556', '0.384', '0.385']:
        assert value in supplement
    assert 'All four controls predicted a comma, whereas the factual prompts predicted names.' in supplement
    assert 'Figure 3, which uses ten Qwen3-4B facts' in supplement
    assert 'Both remained in the main comparison in Figure 2.' in supplement
    assert 'All 50 Qwen3-1.7B factual prompts matched in checks of both input-token text and predicted-token text.' in supplement
    assert 'four predicted complete accepted answers, two predicted partial beginnings, and four predicted other next tokens' in supplement
    assert 'These partial predictions remained excluded from the complete-answer comparison.' in supplement
    assert 'not because a full response had been verified as wrong' in supplement


def test_a1_final_body_defines_exact_matching_and_restricted_groups():
    supplement = manuscript().split('### A1 ', 1)[1].split('### A2 ', 1)[0]
    assert 'predicted next-token text to equal the expected text after removing leading and trailing whitespace' in supplement
    assert '7/9, 4/9, and 0/9 for Gemma chemistry, geography, and history' in supplement
    assert 'Qwen3-4B counts were 8/9, 9/9, and 0/9 (Supplementary Figure S5b)' in supplement
    assert 'Eight Qwen3-4B predictions in this experiment contained only whitespace' in supplement
    assert 'only for groups in which all nine questions passed this matching rule' in supplement
    assert 'Each group contained three facts asked in three versions; only Qwen3-4B geography qualified.' in supplement
    assert 'same-fact overlap difference was 0.1014' in supplement
    assert 'difference for questions sharing a version label was 0.1063' in supplement
    assert 'they did not guarantee identical wording across facts' in supplement
    assert 'we did not formally test that comparison' in supplement


def test_invented_name_controls_are_defined_and_legacy_terms_are_absent():
    text = manuscript()
    assert 'The controls used invented names, such as “zorium” instead of gold.' in text
    assert not re.search(r'made.up|\bnonce\b|\ba invented\b', text, re.I)
    assert 'Mean same-fact-minus-other-fact overlap remained positive for all three models at both sample sizes' in text


def test_manuscript_uses_american_spelling_and_no_em_dashes():
    text = manuscript()
    assert chr(0x2014) not in text
    assert not re.search(r'\b(?:labelled|labelling|behaviour\w*|colour\w*|analysed|analysing|modelling|modelled|centred|artefact\w*|generalisation|normalisation)\b', text, re.I)


def test_introduction_moves_from_background_to_hypothesis_and_contribution():
    text = manuscript()
    intro = text.split('## 1. Introduction\n\n', 1)[1].split('\n## 2. Methods', 1)[0]
    paragraphs = [p for p in intro.strip().split('\n\n') if p]
    assert len(paragraphs) == 6
    starts = [
        'Knowing whether a language model gives a correct answer',
        'Attribution graphs show patterns of activity',
        'Comparing these graphs requires distinguishing',
        'We initially hypothesized that, within each model',
        'We then used Qwen3-4B',
        'Feature overlap was associated with both the relationship between questions',
    ]
    assert all(p.startswith(start) for p, start in zip(paragraphs, starts))
    assert paragraphs[5] == ('Feature overlap was associated with both the relationship between questions and the answer the model predicted. '
                             'We next describe the model samples, question designs, and graph comparisons used to evaluate these relationships.')
    assert 'using Jaccard similarity, our measure of feature overlap' in paragraphs[3]
    assert '[1]' in paragraphs[0] and '[2]' in paragraphs[1] and '[5]' in paragraphs[1]
    assert 'The score ranges from zero' not in intro
    measurement = text.split('### 2.2 ', 1)[1].split('### 2.3 ', 1)[0]
    choice = text.split('### 2.5 ', 1)[1].split('### 2.6 ', 1)[0]
    errors = text.split('### 2.6 ', 1)[1].split('### 2.7 ', 1)[0]
    results = text.split('### 3.3 ', 1)[1].split('### 3.4 ', 1)[0]
    assert 'The score ranges from zero' in measurement
    assert 'Paris was labeled A, but B when Paris was labeled B' in choice
    assert 'France/Germany illustrated the design in the preliminary check; six other country pairs formed the evaluation.' in choice
    assert 'Both named-country predictions were correct for their respective questions' in errors
    assert 'After the pilot failed' in errors and 'exploratory diagnostic' in errors
    assert 'The factual answer remained the same, but the greater feature overlap observed with a shared answer letter did not persist.' in results


def test_methods_defines_error_graph_before_using_the_term():
    text = manuscript()
    methods = text.split('## 2. Methods\n\n', 1)[1]
    overview = methods.split('\n\n', 1)[0]
    definition = 'attribution graphs for incorrect predictions, referred to here as error graphs'
    assert definition in overview
    assert text.index(definition) < text.index('Each error graph was compared')
    assert 'swapped the capitals assigned to A and B' in overview
    assert 'one giving the same answer as the error, but in a context where that answer was correct' in overview
    assert 'The four analyses used distinct question sets and were evaluated separately.' in overview


def test_model_description_distinguishes_common_analysis_from_model_ranking():
    text = manuscript()
    models = text.split('### 2.1 ', 1)[1].split('### 2.2 ', 1)[0]
    assert 'We used the same Jaccard similarity measure and feature-exclusion rules across all three models' in models
    assert 'providing a separate test of the same hypothesis in each model' in models
    assert 'pruning, and available prompt coverage vary together' not in models
    assert 'No pooled model-ranking test is performed.' in text


def test_question_design_explains_controls_and_keeps_fact_versions_together():
    text = manuscript()
    models = text.split('### 2.1 ', 1)[1].split('### 2.2 ', 1)[0]
    assert '30 facts, with ten each from chemistry, geography, and history' in models
    assert 'five facts were assigned to development and five to evaluation' in models
    assert 'All four question versions for a fact stayed in the same set.' in models
    assert 'preserving either the starting or reworded sentence pattern' in models
    assert 'Qwen3-4B supplied all 120 question/control graphs.' in models
    assert '147 Qwen3-4B exports' in text


def test_collection_totals_distinguish_question_designs_from_analyzed_samples():
    models = manuscript().split('### 2.1 ', 1)[1].split('### 2.2 ', 1)[0]
    assert '| Gemma-2-2B | 120/120 | 27/27 | 8: chemistry 5, history 3 |' in models
    assert '| Qwen3-1.7B | 91/120 | Not collected | 10: chemistry 5, geography 5 |' in models
    assert '| Qwen3-4B | 120/120 | 27/27 | 12: chemistry 5, geography 5, history 2 |' in models
    assert '385 available graphs in total' in models
    assert '48 and 16 graphs, respectively' in models
    assert '145/147' not in models
    assert 'November' not in models and 'September' not in models
    assert '50 graphs' not in models
    assert 'geography and history do not provide complete three-model comparisons' in models


def test_future_research_distinguishes_selection_from_computation_and_completed_work():
    text = manuscript()
    future = text.split('### 4.3 Future research: separating model activity from graph construction\n\n', 1)[1].split('## 5. Conclusion', 1)[0]
    paragraphs = future.strip().split('\n\n')
    assert len(paragraphs) == 4
    assert 'From one recorded model run' in paragraphs[0]
    assert 'one graph could explain the A token and another the B token' in paragraphs[0]
    assert 'prompt, model activity, and graph settings unchanged' in paragraphs[0]
    assert 'would not by itself establish how much of the similarity across questions comes from that choice' in paragraphs[0]
    assert 'activity recorded before features are selected for a particular output' in paragraphs[1]
    assert 'keeping feature definitions fixed and checking sensitivity to feature counts' in paragraphs[1]
    assert 'would support a contribution from shared model activity' in paragraphs[1]
    assert 'graph construction also shapes the measured relationship' in paragraphs[1]
    assert 'saved exports contain only retained features' in future
    assert 'do not consistently include those alternative outputs' in paragraphs[3]
    assert 'facts and wordings not used to select the features' in future
    assert 'unchanged-model baseline' in future and 'randomly selected features matched in number, layer, and activation' in future
    assert 'Testing several intervention strengths' in paragraphs[2]
    assert 'distinguish selective effects from general disruption' in paragraphs[2]
    assert 'the proposed tests would move the investigation' in paragraphs[3]


def test_approved_abstract_preserves_results_and_ends_with_scientific_takeaway():
    text = manuscript()
    abstract = text.split('## Abstract\n\n', 1)[1].split('## 1. Introduction', 1)[0].strip()
    assert len(abstract.split('\n\n')) == 1
    assert 'Jaccard overlap in Gemma-2-2B, Qwen3-1.7B, and Qwen3-4B' in abstract
    assert 'including after equalizing feature counts' in abstract
    assert 'six country pairs' in abstract and 'All 48 predicted letters were correct.' in abstract
    assert 'prespecified mean difference between same-country and different-country overlap was 0.0303' in abstract
    assert '95% block-bootstrap interval 0.0265–0.0338' in abstract
    assert 'with 8, 10, and 12 included evaluation facts, respectively' in abstract
    assert 'The same-country overlap advantage was 0.0628 when answer letters matched but near zero (-0.0022) when different letters represented the correct answers.' in abstract
    assert 'including five incorrect predictions' in abstract
    assert 'eight selected error comparisons from one country pair' in abstract
    assert '16 historical-date graphs from two event pairs' in abstract
    assert abstract.endswith('Together, these findings show that graph similarity can track the predicted response without establishing correct factual processing.')
    assert 'Attribution-graph comparisons should therefore distinguish' not in abstract


def test_conclusion_connects_findings_to_interpretation_without_expanding_scope():
    text = manuscript()
    conclusion = text.split('## 5. Conclusion\n\n', 1)[1].split('## Supporting analyses', 1)[0].strip()
    assert len(conclusion.split('\n\n')) == 1
    assert conclusion.startswith('Reworded questions about the same fact shared more attribution-graph features across the three analyzed model samples.')
    assert 'In Qwen3-4B, that advantage was concentrated in comparisons sharing the answer letter' in conclusion
    assert 'selected errors and historical-date comparisons' in conclusion
    assert 'without agreement on the correct factual answer' in conclusion
    assert 'the fact being queried, the response produced, and whether that response is correct' in conclusion
    assert 'causal mechanism' not in conclusion


def test_expanded_sample_methods_are_concise_and_retain_core_limits():
    text = manuscript()
    methods = text.split('### 2.8 Qwen3-1.7B analysis and verification\n\n', 1)[1].split('## 3. Results', 1)[0]
    assert len(methods.split()) <= 250
    assert len(methods.strip().split('\n\n')) == 3
    assert 'combined 91-graph Qwen3-1.7B dataset' in methods
    assert 'Sections 2.2–2.4' in methods
    assert 'before calculating the estimates but after earlier findings were known' in methods
    assert 'exploratory rather than an independent confirmatory replication' in methods
    assert 'some archived files used 0.95 output coverage' in methods
    assert 'Desired cumulative output probability was 0.99' in methods
    assert 'unchanged hosted model versions' in methods
    assert 'Supporting methods A5.1' in methods
    assert '15 secondary sign-flip tests' in methods
    assert 'excluding the primary Jaccard/average-other-fact comparison' in methods
    assert 'Output-type-matched subsets, reconstruction-error-inclusive and equal-feature-count checks, and subject-specific summaries' in methods
    assert 'outside this correction family' in methods
    assert 'Shared comparison questions limit the interpretation' in methods
    assert 'label permutations assume exchangeable factual pairings within each subject area' in methods
    assert 'do not separate shared-word or expected-answer differences from fact identity' in methods
    assert 'absolute tolerance 1e-12' not in methods
    assert '14,400 assignments' not in methods
    assert 'same recorded model run' not in methods


def test_supporting_methods_preserve_expanded_sample_settings_and_audit_units():
    text = manuscript()
    a5 = text.split('### A5 Qwen3-1.7B results in chemistry and geography\n\n', 1)[1].split('### A6 ', 1)[0]
    results, methods = a5.split('#### A5.1 Additional methods and verification\n\n', 1)
    assert 'Supporting methods A5.1 specifies these procedures and the Holm correction applied to 15 secondary tests' in results
    assert '| Same-pattern control, matched by broad output type | -0.0109 | [-0.0208, 0.0005] | 2/9 |' in results
    assert '| Reworded control, matched by broad output type | 0.1059 | [0.0918, 0.1194] | 10/10 |' in results
    for setting in ['llamascope-2-transcoder-16k-k64', 'LoRSA',
                    'at most ten candidate next tokens (`maxNLogits=10`)',
                    'node and edge thresholds of 0.8 and 0.85', '5,000-feature-node cap',
                    '`qkTopFraction=0.5` and `qkTopk=5`', '0.99', '0.95', '2.0.0b34']:
        assert setting in methods
    assert 'unchanged hosted weights cannot be independently verified' in methods
    assert 'No shorter prompts or replacement questions were introduced' in methods
    assert '10,000 fact-level bootstrap resamples' in methods
    assert 'exact one-sided sign-flip tests' in methods
    assert 'seed 20260714' in methods
    assert '5! × 5! = 14,400 assignments' in methods
    assert '15 secondary evaluation-sample sign-flip p-values, excluding the primary comparison' in methods
    assert 'feature Jaccard and cosine similarities of influence-weighted features, layer profiles, and layer-to-layer edge flow' in methods
    assert 'average other fact, most similar other fact, same-pattern invented name, and reworded invented name' in methods
    assert 'used the full eligible sample, not the subsets matched by output type' in methods
    assert 'Output-type-matched subsets, error-inclusive and equal-count checks, and subject-specific summaries were outside this correction family' in methods
    assert 'summed absolute exported influence across occurrences' in methods
    assert 'edge-flow profiles aggregated absolute edge weights between eligible feature nodes by source and target layer' in methods
    assert 'control and starting question to have the same broad next-token category' in methods
    assert '200 subsamples at K and floor(K/2)' in methods
    assert 'seed 20260905 and K defined separately within each subject\'s evaluation set' in methods
    assert 'subsamples were not treated as additional facts' in methods
    assert 'without rebuilding its comparison pool' in methods
    assert 'absolute tolerance 1e-12' in methods
    assert 'Earlier subset estimates remain in the archive and are not counted as additional evidence' in methods
    assert 'Export checks covered all 91 graphs' in methods
    assert 'word-matching checks covered the ten included evaluation facts' in methods
    assert 'token checks covered all 50 available factual starting/reworded prompts' in methods
    assert 'absolute error-node influence divided by absolute nonterminal-node influence, using nodes with valid identifiers' in methods
    assert 'not an answer-error rate or a causal contribution estimate' in methods
    assert 'these audits did not alter inclusion or primary estimates' in methods
    assert 'before the audit calculations but after earlier overlap findings were known' in methods

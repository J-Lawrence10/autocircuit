"""Guard the revised narrative's scope and reported values; not scientific validation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'docs/papers/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'
if not SOURCE.exists():
    SOURCE = ROOT.parent/'manuscript/ATTRIBUTION_GRAPH_THREE_MODEL_DRAFT.md'


def manuscript():
    return SOURCE.read_text(encoding='utf-8')


def test_results_follow_question_controls_answer_errors_checks_scope():
    text = manuscript()
    headings = re.findall(r'^### 3\.\d+ (.+)$', text, re.M)
    assert headings == [
        'Reworded questions about the same fact share more features',
        'Same-fact questions share words and expected answers',
        'Same-fact overlap is higher when the answer letter stays the same',
        'Error graphs show greater overlap with answer-matched controls',
        'Greater feature sharing between same-fact questions',
        'The history pilot yields 15 of 20 correct predictions',
    ]
    assert text.index('## Supporting analyses') > text.index('## 5. Conclusion')


def test_primary_and_exploratory_outcomes_remain_distinct():
    text = manuscript()
    assert 'Their average, the prespecified primary outcome, was 0.0303' in text
    assert 'The exploratory direct paired difference' in text
    for value in ['0.0628', '-0.0022', '0.0265–0.0338', '0.000244141',
                  '0.000732422', '0.0650', '0.0553–0.0746', 'p=0.03125', '0.2827']:
        assert value in text


def test_original_results_and_limitations_are_retained():
    text = manuscript()
    for value in ['0.170', '0.085', '0.162', '0.1983', '0.2649', '0.1851',
                  '0.2361', '-0.0187', '-0.0080', '145/147', '15/20', '20/20',
                  '23.1%', '17.2–31.4%', '4.9–14.6', '8/16']:
        assert value in text
    for phrase in ['not eight independent replications', 'not an equivalence',
                   'not causal ablations', 'no evaluation graphs were requested',
                   'observationally indistinguishable', 'not verification of a complete generated answer']:
        assert phrase in text


def test_current_figures_and_public_availability_are_consistent():
    text = manuscript()
    assert '**Working manuscript. Not peer reviewed.**' in text
    images = re.findall(r'!\[Figure (S?\d+):', text)
    assert set(images) == {str(i) for i in range(1, 7)} | {f'S{i}' for i in range(1, 9)}
    assert len(images) == 14
    assert 'No data were published or submitted externally' not in text
    assert 'GitHub submission branch' in text
    assert 'Raw Neuronpedia exports, tokenizer/model files, credentials, and downloaded reference PDFs are excluded' in text
    assert 'Sharing copy updated 8 October' not in text


def test_reader_gets_measurement_and_bridges_before_details():
    text = manuscript()
    assert '### 2.2 Measuring feature overlap' in text
    assert 'We measured feature sharing between questions using Jaccard similarity, our measure of feature overlap.' in text
    assert 'the number of shared features divided by the total number of distinct features across both graphs' in text
    assert 'Attribution graphs show patterns of activity inside a model and estimate how those patterns contribute to its prediction' in text
    assert 'multiple-choice questions containing two country names and two possible capitals, labeled A and B' in text
    assert 'Both named-country predictions were correct for their respective questions' in text
    assert 'When the model had to answer with different letters, questions asking for the same capital had nearly the same average feature overlap as questions about different countries.' in text
    assert 'The factual answer remained the same, but the greater feature overlap observed with a shared answer letter did not persist.' in text
    assert 'using the tuple `(feature family, layer, feature ID)`' in text
    assert 'Matching numerical IDs in different layers or feature families remained distinct.' in text
    assert 'A feature that appeared at multiple positions in the input was counted once.' in text
    assert 'nodes with missing or duplicated graph-node identifiers' in text
    assert 'Features were compared only between graphs from the same model.' in text
    assert 'The next question is what the association distinguishes' in text
    assert 'The matched-choice study used correct predictions. We next asked' in text
    assert 'Prespecified conditional correspondence test' in text
    assert 'Exploratory block sign-flip test' in text
    assert 'exchangeable conditional on the label and word inventory' in text


def test_supporting_figures_do_not_interrupt_main_results():
    text = manuscript()
    main = text.split('## Supporting analyses')[0]
    assert not re.search(r'!\[Figure S\d+:', main)
    assert '### A4 Comparison and sensitivity figures' in text
    assert '### 4.2 Scope and remaining questions' in text
    assert 'ordinary least-squares intercept with centered predictors equals' in text


def test_primary_comparison_is_explained_before_equation_and_links_workflow():
    text = manuscript()
    methods = text.split('### 2.2 ', 1)[1].split('### 2.3 ', 1)[0]
    assert methods.index('For each starting question, we calculated Jaccard overlap') < methods.index('`M_i =')
    assert 'every other included fact from the same model, subject, and development or evaluation set' in methods
    assert 'Figure S8 summarizes the workflow.' in methods
    assert '### A6 Feature-overlap analysis workflow' in text
    assert 'the fact/wording, answer-letter, and selected-error experiments retain their own comparisons and inclusion rules' in text


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
    assert '28 model-specific fact observations, not 28 unique independent facts' in methods
    assert 'within-subject' not in text


def test_crossed_design_distinguishes_version_labels_from_exact_templates():
    text = manuscript()
    methods = text.split('### 2.3 ', 1)[1].split('### 2.4 ', 1)[0]
    assert '27 graphs per model' in methods
    assert 'The version labels did not imply identical sentence patterns across facts.' in methods
    assert 'questions differing in fact and version as their baseline' in methods
    assert 'varied factual content and sentence pattern separately' not in text
    assert 'Both comparisons had positive average overlap differences' in text
    assert '0.074/0.118' in text and '0.101/0.064' in text


def test_current_qwen_sample_and_negative_controls_are_used_consistently():
    text = manuscript()
    assert '| Qwen3-1.7B | 91/120 | Not collected | 10: chemistry 5, geography 5 |' in text
    assert '91 collected graphs comprised 40 chemistry, 40 geography, and 11 history graphs' in text
    assert 'These are collection failures, not incorrect predictions.' in text
    assert 'all five chemistry and all five geography evaluation facts' in text
    for number in ['0.0935', '0.0894', '[0.0820, 0.0976]', '-0.0114', '-0.0109', '0.1059',
                   '0.0835', '0.0331', '0.00016', '0.1934', '14,400']:
        assert number in text
    assert 'exploratory rather than an independent confirmatory replication' in text
    assert 'eight of its ten evaluation questions shared more features with the same-pattern invented name control' in text
    assert 'No history fact had a complete control set.' in text
    assert 'Shorter history prompts were not generated or substituted' in text
    results = text.split('### 3.1 ', 1)[1].split('### 3.3 ', 1)[0]
    assert '0.0894 for Qwen3-1.7B ([0.0820, 0.0976], n=10)' in results
    assert '106 directed other-fact comparisons' in results
    assert '0.085 for Qwen3-1.7B' not in results
    assert '0/5 Qwen3-1.7B' not in results


def test_figure_captions_match_authoritative_wording():
    import sys
    sys.path.insert(0, str(ROOT/'scripts'))
    import figure_plain_language as wording
    text = manuscript()
    for stem, title in wording.TITLES.items():
        number = re.match(r'figure(S?\d+)', stem).group(1)
        assert f'![Figure {number}: {title}]' in text
        assert f'**Figure {number}. {title}.** {wording.CAPTIONS[stem]}' in text


def test_invented_name_controls_are_defined_and_legacy_terms_are_absent():
    text = manuscript()
    assert 'Invented name controls replace a real entity name with an invented name' in text
    assert not re.search(r'made.up|\bnonce\b|\ba invented\b', text, re.I)
    assert 'Mean differences remained positive at both sampling sizes' in text


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
    assert 'Paris is labeled A, but B when Paris is labeled B' in choice
    assert 'France/Germany was used only in the preliminary behavioral check' in choice
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
    assert 'The three analyses used distinct question sets and were evaluated separately.' in overview


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
    assert 'Two versions of the Columbus question were unavailable for Qwen3-4B after repeated server failures' in models
    assert '145/147' in models


def test_collection_totals_distinguish_question_designs_from_analyzed_samples():
    models = manuscript().split('### 2.1 ', 1)[1].split('### 2.2 ', 1)[0]
    assert '| Gemma-2-2B | 120/120 | 27/27 | 8: chemistry 5, history 3 |' in models
    assert '| Qwen3-1.7B | 91/120 | Not collected | 10: chemistry 5, geography 5 |' in models
    assert '| Qwen3-4B | 118/120 | 27/27 | 10: chemistry 5, geography 5 |' in models
    assert '383 available graphs in total' in models
    assert '48 and 16 graphs, respectively' in models
    assert '145/147' in models
    assert 'November' not in models and 'September' not in models
    assert '50 graphs' not in models
    assert 'requirement for support across all three subjects remains unmet' in models


def test_future_research_distinguishes_selection_from_computation_and_completed_work():
    text = manuscript()
    future = text.split('### 4.3 Future research: separating computation from graph selection\n\n', 1)[1].split('## 5. Conclusion', 1)[0]
    assert 'Both processes could contribute.' in future
    assert 'same recorded model run' in future
    assert 'holding the prompt and model activity fixed' in future
    assert 'feature activity recorded before answer-dependent selection' in future
    assert 'would not by themselves quantify its contribution to the cross-question result' in future
    assert 'saved exports contain only retained features' in future
    assert 'facts and wordings not used to select the features' in future
    assert 'unchanged-model controls' in future and 'randomly selected feature sets matched in number, layer, and activation' in future
    assert 'multiple intervention strengths' in future
    assert 'future work, not experiments performed in this study' in future


def test_expanded_sample_methods_describe_performed_analyses_and_audit_units():
    text = manuscript()
    methods = text.split('### 2.8 Qwen3-1.7B analysis and verification\n\n', 1)[1].split('## 3. Results', 1)[0]
    assert 'combined 91-graph dataset' in methods
    assert 'exploratory rather than an independent confirmatory replication' in methods
    assert 'absolute tolerance 1e-12' in methods
    assert 'some archived files used 0.95 output coverage' in methods
    assert 'Desired cumulative output probability was 0.99' in methods
    assert 'at most ten candidate next tokens (maxNLogits=10)' in methods
    assert '10,000 fact-level bootstrap resamples' in methods
    assert '5! × 5! = 14,400 assignments' in methods
    assert '15 secondary metric/contrast tests, excluding the primary comparison' in methods
    assert 'outside this correction family' in methods
    assert 'summed absolute exported influence across occurrences' in methods
    assert 'nine same-pattern and ten reworded-control comparisons' in methods
    assert '200 subsamples' in methods and 'seed 20260905' in methods
    assert 'without rebuilding its comparison pool' in methods
    assert 'Export checks covered all 91 graphs' in methods
    assert 'word-matching checks covered the ten included evaluation facts' in methods
    assert 'token checks covered all 50 available factual starting/reworded prompts' in methods
    assert 'these audits did not alter inclusion or primary estimates' in methods
    assert 'same recorded model run' not in methods

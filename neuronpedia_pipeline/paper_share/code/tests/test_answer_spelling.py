import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_answer_spelling import accepts, read, REGISTRY


def test_complete_registered_spelling_is_accepted():
    registry = read(REGISTRY)
    for value in ['Maria', ' María ', 'Mari\u0301a']:
        assert accepts('columbus_americas', 'Maria', value, registry)


def test_rule_is_not_global_accent_removal_or_prefix_matching():
    registry = read(REGISTRY)
    for value in ['Mar', 'M', 'maria', 'Mária', 'Maria.', 'Santa María', ' ']:
        assert not accepts('columbus_americas', 'Maria', value, registry)
    assert not accepts('another_fact', 'Maria', 'María', registry)
    assert not accepts('columbus_americas', 'Pinta', 'María', registry)
    assert not accepts('mercury_symbol', 'Hg', 'H', registry)
    assert accepts('wwi_start', '1914', ' 1914 ', registry)

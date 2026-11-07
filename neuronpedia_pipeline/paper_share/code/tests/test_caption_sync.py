"""Mechanical caption synchronization must not rewrite manuscript body prose."""
from unittest.mock import patch

import pytest
from scripts import sync_manuscript_figure_captions as sync


def test_caption_sync_preserves_body_and_image_destination():
    original = ('Body before.\n\n![Figure 2: Old title](C:/project/figure2_example.png)\n\n'
                '**Figure 2. Old title.** Old caption.\n\nBody after.\n')
    with patch.dict(sync.wording.TITLES, {'figure2_example': 'New title'}, clear=True), \
         patch.dict(sync.wording.CAPTIONS, {'figure2_example': 'New caption.'}, clear=True):
        updated, n = sync.reconcile(original)
    assert n == 1
    assert updated == ('Body before.\n\n![Figure 2: New title](C:/project/figure2_example.png)\n\n'
                       '**Figure 2. New title.** New caption.\n\nBody after.\n')


def test_caption_sync_rejects_missing_or_duplicate_figures():
    fragment = '![Figure 2: Title](C:/project/figure2_example.png)\n\n**Figure 2. Title.** Caption.\n'
    with patch.dict(sync.wording.TITLES, {'figure2_example': 'Title'}, clear=True), \
         patch.dict(sync.wording.CAPTIONS, {'figure2_example': 'Caption.'}, clear=True):
        with pytest.raises(ValueError, match='Figure set differs'):
            sync.reconcile('Body only.')
        with pytest.raises(ValueError, match='Duplicate'):
            sync.reconcile(fragment + fragment)

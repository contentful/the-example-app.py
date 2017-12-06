from unittest import TestCase
from contentful.errors import EntryNotFoundError

from lib.entry_state import attach_entry_state, \
                            has_pending_changes, \
                            should_show_entry_state, \
                            should_attach_entry_state


class MockEntry(object):
    def __init__(self, entry_id, updated_at='mock_updated_at', published_at='mock_published_at'):
        self.id = entry_id
        self.updated_at = updated_at
        self.published_at = published_at


class MockService(object):
    def __init__(self, published_at, updated_at):
        self.published_at = published_at
        self.updated_at = updated_at

    def __call__(self):
        return self

    def entry(self, entry_id, _api_id):
        if self.published_at is None:
            raise EntryNotFoundError('error')
        return MockEntry(entry_id, self.updated_at, self.published_at)


class Session(dict):
    def __init__(self, editorial_features=False):
        self['enable_editorial_features'] = editorial_features


class EntryStateTest(TestCase):
    # should_attach_entry_state
    def test_false_when_current_api_is_not_cpa(self):
        self.assertFalse(should_attach_entry_state('cda', Session(True)))

    def test_false_when_current_api_is_cpa_but_editorial_features_is_false(self):
        self.assertFalse(should_attach_entry_state('cpa', Session(False)))

    def test_true_when_current_api_is_cpa_and_editorial_features_is_true(self):
        self.assertTrue(should_attach_entry_state('cpa', Session(True)))

    # has_pending_changes
    def test_false_if_preview_entry_is_none(self):
        self.assertFalse(has_pending_changes(None, MockEntry('id')))

    def test_false_if_delivery_entry_is_none(self):
        self.assertFalse(has_pending_changes(MockEntry('id'), None))

    def test_false_if_both_entries_present_but_have_same_updated_at_dates(self):
        self.assertFalse(has_pending_changes(MockEntry('id'), MockEntry('id')))

    def test_true_if_both_entries_have_different_updated_at_dates(self):
        self.assertTrue(has_pending_changes(MockEntry('id'), MockEntry('id', updated_at='some_other_date')))

    # should_show_entry_state
    def test_false_if_current_api_is_cda(self):
        self.assertFalse(should_show_entry_state(MockEntry('id'), 'cda'))

    def test_false_if_current_api_is_cpa_but_entry_is_neither_draft_or_pending_changes(self):
        self.assertFalse(should_show_entry_state(MockEntry('id'), 'cpa'))

    def test_true_if_current_api_is_cpa_and_entry_is_draft(self):
        entry = MockEntry('id')
        attach_entry_state(entry, MockService(None, 'mock_updated_at'))

        self.assertTrue(should_show_entry_state(entry, 'cpa'))

    def test_true_if_current_api_is_cpa_and_entry_is_pending_changes(self):
        entry = MockEntry('id')
        attach_entry_state(entry, MockService('mock_published_at', 'other_updated_at'))

        self.assertTrue(should_show_entry_state(entry, 'cpa'))

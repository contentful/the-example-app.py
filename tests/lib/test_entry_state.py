import datetime
from unittest import TestCase
from contentful.errors import EntryNotFoundError

from lib.entry_state import attach_entry_state, \
                            has_pending_changes, \
                            should_show_entry_state, \
                            should_attach_entry_state, \
                            sanitize_datetime


class MockEntry(object):
    def __init__(self, entry_id, updated_at=datetime.datetime(2017, 12, 14), published_at=datetime.datetime(2017, 12, 14), fields=None):
        self.id = entry_id
        self.updated_at = updated_at
        self.published_at = published_at
        self._fields = fields if fields is not None else {}

    def fields(self):
        return self._fields


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
        self['editorial_features'] = editorial_features


class EntryStateTest(TestCase):
    # should_attach_entry_state
    def test_false_when_current_api_is_not_cpa(self):
        self.assertFalse(should_attach_entry_state('cda', Session('enabled')))

    def test_false_when_current_api_is_cpa_but_editorial_features_is_false(self):
        self.assertFalse(should_attach_entry_state('cpa', Session('disabled')))

    def test_true_when_current_api_is_cpa_and_editorial_features_is_true(self):
        self.assertTrue(should_attach_entry_state('cpa', Session('enabled')))

    # has_pending_changes
    def test_false_if_preview_entry_is_none(self):
        self.assertFalse(has_pending_changes(None, MockEntry('id')))

    def test_false_if_delivery_entry_is_none(self):
        self.assertFalse(has_pending_changes(MockEntry('id'), None))

    def test_false_if_both_entries_present_but_have_same_updated_at_dates(self):
        self.assertFalse(has_pending_changes(MockEntry('id'), MockEntry('id')))

    def test_true_if_both_entries_have_different_updated_at_dates(self):
        self.assertTrue(has_pending_changes(MockEntry('id'), MockEntry('id', updated_at=datetime.datetime(2017, 12, 16))))

    # should_show_entry_state
    def test_false_if_current_api_is_cda(self):
        self.assertFalse(should_show_entry_state(MockEntry('id'), 'cda'))

    def test_false_if_current_api_is_cpa_but_entry_is_neither_draft_or_pending_changes(self):
        self.assertFalse(should_show_entry_state(MockEntry('id'), 'cpa'))

    def test_true_if_current_api_is_cpa_and_entry_is_draft(self):
        entry = MockEntry('id')
        attach_entry_state(entry, MockService(None, datetime.datetime(2017, 12, 14)))

        self.assertTrue(should_show_entry_state(entry, 'cpa'))

    def test_true_if_current_api_is_cpa_and_entry_is_pending_changes(self):
        entry = MockEntry('id')
        attach_entry_state(entry, MockService(datetime.datetime(2017, 12, 14), datetime.datetime(2017, 12, 18)))

        self.assertTrue(should_show_entry_state(entry, 'cpa'))

    # sanitize_datetime
    def test_removes_milliseconds(self):
        date = datetime.datetime(2017, 12, 14, 12, 30, 30, 123)

        self.assertEqual("2017-12-14T12:30:30.000123", date.isoformat())

        self.assertEqual("2017-12-14T12:30:30", sanitize_datetime(date).isoformat())

from unittest import TestCase

from tests import MockApp
from i18n.i18n import I18n, translate, is_translation_available


class I18nTest(TestCase):
    @classmethod
    def setUpClass(klass):
        I18n(MockApp())

    # translation available
    def test_returns_false_if_translation_not_available_for_symbol(self):
        self.assertFalse(is_translation_available('foobar', 'en-US'))

    def test_returns_false_if_translation_file_not_available(self):
        self.assertFalse(is_translation_available('coursesLabel', 'foobar'))

    def test_returns_true_if_locale_is_found_and_symbol_exists(self):
        self.assertTrue(is_translation_available('coursesLabel', 'en-US'))

    # translate
    def test_returns_default_fallback_locale_when_locale_file_is_not_found(self):
        self.assertEqual(
            'Courses',
            translate('coursesLabel', 'unknown-Locale')
        )

    def test_returns_an_error_string_when_symbol_is_not_found_for_locale(self):
        self.assertEqual(
            'Translation not found for doesntExist in en-US',
            translate('doesntExist', 'en-US')
        )

    def test_returns_translated_string_when_symbol_is_found_for_locale(self):
        self.assertEqual('Courses', translate('coursesLabel', 'en-US'))
        self.assertEqual('Kurse', translate('coursesLabel', 'de-DE'))

from unittest import TestCase

from tests import MockApp
from lib.breadcrumbs import breadcrumbs, refine
from i18n.i18n import I18n


class MockResource(object):
    def __init__(self, slug='', title=''):
        self.slug = slug
        self.title = title


class BreadcrumbsTest(TestCase):
    @classmethod
    def setUpClass(klass):
        I18n(MockApp())

    # breadcrumbs
    def test_add_all_parts_of_the_url(self):
        path = '/courses/foobar/lessons'
        expected = [
            {'url': '/', 'label': 'Home'},
            {'url': '/courses', 'label': 'Courses'},
            {'url': '/courses/foobar', 'label': 'foobar'},
            {'url': '/courses/foobar/lessons', 'label': 'Lessons'}
        ]

        self.assertEqual(
            breadcrumbs(path, 'en-US'),
            expected
        )

    def test_localizes_static_parts_of_the_url(self):
        path = '/courses/foobar/lessons'
        expected = [
            {'url': '/', 'label': 'Startseite'},
            {'url': '/courses', 'label': 'Kurse'},
            {'url': '/courses/foobar', 'label': 'foobar'},
            {'url': '/courses/foobar/lessons', 'label': 'Lektionen'}
        ]

        self.assertEqual(
            breadcrumbs(path, 'de-DE'),
            expected
        )

    # refine
    def test_does_nothing_if_no_slugs_match(self):
        path = '/courses/foobar/lessons'

        expected = [
            {'url': '/', 'label': 'Startseite'},
            {'url': '/courses', 'label': 'Kurse'},
            {'url': '/courses/foobar', 'label': 'foobar'},
            {'url': '/courses/foobar/lessons', 'label': 'Lektionen'}
        ]

        self.assertEqual(
            refine(
                breadcrumbs(path, 'de-DE'),
                MockResource()
            ),
            expected
        )

    def test_replaces_dynamic_parts_of_urls_with_resource_titles_if_slugs_math(self):
        path = '/courses/foobar/lessons'

        expected = [
            {'url': '/', 'label': 'Startseite'},
            {'url': '/courses', 'label': 'Kurse'},
            {'url': '/courses/foobar', 'label': 'Some Foobar!'},
            {'url': '/courses/foobar/lessons', 'label': 'Lektionen'}
        ]

        self.assertEqual(
            refine(
                breadcrumbs(path, 'de-DE'),
                MockResource('foobar', 'Some Foobar!')
            ),
            expected
        )

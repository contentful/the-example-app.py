from os import environ

from tests import IntegrationTestBase


class AppTest(IntegrationTestBase):
    # routes are present
    def test_index(self):
        self.assertSuccess(self.app.get('/'))

    def test_courses(self):
        self.assertSuccess(self.app.get('/courses'))

    def test_courses_by_slug(self):
        self.assertSuccess(self.app.get('/courses/hello-contentful'))

    def test_courses_categories_redirect(self):
        self.assertRedirect(self.app.get('/courses/categories'))

    def test_courses_by_category(self):
        self.assertSuccess(self.app.get('/courses/categories/getting-started'))

    def test_course_lessons_redirect(self):
        self.assertRedirect(self.app.get('/courses/hello-contentful/lessons'))

    def test_course_lesson(self):
        self.assertSuccess(self.app.get('/courses/hello-contentful/lessons/content-model'))

    def test_get_settings(self):
        self.assertSuccess(self.app.get('/settings'))

    def test_post_settings(self):
        self.assertCreated(self.app.post('/settings', data=dict(
            spaceId=environ.get('CONTENTFUL_SPACE_ID'),
            deliveryToken=environ.get('CONTENTFUL_DELIVERY_TOKEN'),
            previewToken=environ.get('CONTENTFUL_PREVIEW_TOKEN')
        )))

    def test_imprint(self):
        self.assertSuccess(self.app.get('/imprint'))

    def test_editorial_features_are_shown_if_editorial_features_are_enabled(self):
        self.assertIn(b'Edit in the Contentful web app', self.app.get('/?editorial_features=enabled').data)

    def test_query_strings_are_sanitized_to_only_include_locale_and_api(self):
        response = self.app.get('/?api=cpa&locale=en-US&editorial_features=enabled').data
        self.assertIn(b'/courses?api=cpa&amp;locale=en-US', response)

        # Doesn't add additional parameters
        self.assertNotIn(b'/courses?api=cpa&amp;locale=en-US&amp;', response)

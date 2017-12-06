from os import environ

from tests import IntegrationTestBase


class AppTest(IntegrationTestBase):
    # routes are present
    def test_index(self):
        self.assertSuccess(self.app.get('/'))

    def test_courses(self):
        self.assertSuccess(self.app.get('/courses'))

    def test_courses_by_slug(self):
        self.assertSuccess(self.app.get('/courses/hello-world'))

    def test_courses_categories_redirect(self):
        self.assertRedirect(self.app.get('/courses/categories'))

    def test_courses_by_category(self):
        self.assertSuccess(self.app.get('/courses/categories/getting-started'))

    def test_course_lessons_redirect(self):
        self.assertRedirect(self.app.get('/courses/hello-world/lessons'))

    def test_course_lesson(self):
        self.assertSuccess(self.app.get('/courses/hello-world/lessons/architecture'))

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

from tests import IntegrationTestBase


class CoursesTest(IntegrationTestBase):
    def test_renders_all_courses(self):
        response = self.app.get('/courses')
        self.assertIn(b'All courses', response.data)

    def test_renders_category(self):
        response = self.app.get('/courses/categories/getting-started')
        self.assertIn(b'Getting started (1)', response.data)

    def test_renders_course_overview(self):
        response = self.app.get('/courses/hello-world')
        data = response.data

        self.assertIn(b'Table of contents', data)
        self.assertIn(b'Course overview', data)
        self.assertIn(b'Start course', data)

    def test_renders_lesson(self):
        response = self.app.get('/courses/hello-world/lessons/architecture')
        self.assertIn(b'Go to the next lesson', response.data)

    # Errors
    def test_404_on_unknown_course_slug(self):
        response = self.app.get('/courses/foobar')

        self.assertNotFound(response)
        self.assertIn(b'Oops, something went wrong (404)', response.data)

    def test_404_on_unkown_category_slug(self):
        response = self.app.get('/courses/categories/foobar')

        self.assertNotFound(response)
        self.assertIn(b'Oops, something went wrong (404)', response.data)

    def test_404_on_unknown_course_slug_for_lessons(self):
        response = self.app.get('/courses/foobar/lessons/architecture')

        self.assertNotFound(response)
        self.assertIn(b'Oops, something went wrong (404)', response.data)

    def test_404_on_unknown_lesson_slug_for_lessons(self):
        response = self.app.get('/courses/hello-world/lessons/foobar')

        self.assertNotFound(response)
        self.assertIn(b'Oops, something went wrong (404)', response.data)

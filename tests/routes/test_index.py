from tests import IntegrationTestBase


class IndexTest(IntegrationTestBase):
    def test_renders_index(self):
        response = self.app.get('/').data

        self.assertIn(b'Learn how to build your own applications with Contentful.', response)
        self.assertIn(b'view course', response)

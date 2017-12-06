from tests import IntegrationTestBase


class ImprintTest(IntegrationTestBase):
    def test_render_imprint(self):
        response = self.app.get('/imprint').data

        self.assertIn(b'Company', response)
        self.assertIn(b'Contentful GmbH', response)

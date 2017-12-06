from unittest import TestCase

from app import app
from i18n.i18n import I18n


class MockApp(object):
    def add_template_filter(self, fn):
        pass


class IntegrationTestBase(TestCase):
    def setUp(self):
        I18n(app)
        app.testing = True
        self.app = app.test_client()

    def _assertStatusCode(self, code, response):
        self.assertEqual(code, response.status_code)

    def assertSuccess(self, response):
        self._assertStatusCode(200, response)

    def assertCreated(self, response):
        self._assertStatusCode(201, response)

    def assertRedirect(self, response):
        self._assertStatusCode(302, response)

    def assertNotFound(self, response):
        self._assertStatusCode(404, response)

    def assertConflict(self, response):
        self._assertStatusCode(409, response)

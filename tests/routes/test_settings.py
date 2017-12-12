from tests import IntegrationTestBase


class SettingsTest(IntegrationTestBase):
    def test_renders_settings_page(self):
        response = self.app.get('/settings').data

        self.assertIn(b'To query and get content using the APIs, client applications need to authenticate with both the Space ID and an access token.', response)

    def test_post_updates_values(self):
        response = self.app.post('/settings', data=dict(
                spaceId='2qyxj1hqedht',
                deliveryToken='97dd6f2251320afebc6416acb12a6c47ac836bbaea815eb55e7d2d59b80e79f3',
                previewToken='bfc009b1ec707da40d875e1942dbb009eea7d1c19785b7dbd90ecf2cdfd1d989'
            )
        ).data

        self.assertIn(b'Changes saved successfully!', response)
        self.assertIn(b'TEA', response)

    def test_reset_restores_defaults(self):
        # Setup
        response = self.app.post('/settings', data=dict(
                spaceId='2qyxj1hqedht',
                deliveryToken='97dd6f2251320afebc6416acb12a6c47ac836bbaea815eb55e7d2d59b80e79f3',
                previewToken='bfc009b1ec707da40d875e1942dbb009eea7d1c19785b7dbd90ecf2cdfd1d989'
            )
        ).data

        self.assertIn(b'Changes saved successfully!', response)
        self.assertIn(b'TEA', response)

        # Check session state
        response = self.app.get('/settings').data
        self.assertIn(b'TEA', response)

        # Reset session
        response = self.app.post('/settings/reset').data
        self.assertIn(b'The example app space v1', response)

    # Errors
    def test_display_field_required_errors_if_on_any_of_the_text_inputs_input_is_missing(self):
        response = self.app.post('/settings', data=dict(
                spaceId='',
                deliveryToken='97dd6f2251320afebc6416acb12a6c47ac836bbaea815eb55e7d2d59b80e79f3',
                previewToken='bfc009b1ec707da40d875e1942dbb009eea7d1c19785b7dbd90ecf2cdfd1d989'
            )
        )
        body = response.data

        self.assertConflict(response)
        self.assertIn(b'Some errors occurred. Please check the error messages next to the fields.', body)
        self.assertIn(b'This field is required', body)

    def test_displays_space_or_token_error_if_space_or_token_are_incorrect(self):
        response = self.app.post('/settings', data=dict(
                spaceId='foobar',
                deliveryToken='97dd6f2251320afebc6416acb12a6c47ac836bbaea815eb55e7d2d59b80e79f3',
                previewToken='bfc009b1ec707da40d875e1942dbb009eea7d1c19785b7dbd90ecf2cdfd1d989'
            )
        )
        body = response.data

        self.assertConflict(response)
        self.assertIn(b'Some errors occurred. Please check the error messages next to the fields.', body)
        self.assertIn(b'This space does not exist or your access token is not associated with your space.', body)

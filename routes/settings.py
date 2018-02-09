from os import environ
from flask import Blueprint, request, session

from routes.base import locale, \
                        api_id, \
                        contentful, \
                        update_session_for, \
                        render_with_globals, \
                        VIEWS_PATH, \
                        check_errors, \
                        space_id, \
                        delivery_token, \
                        preview_token, \
                        is_using_custom_credentials
from routes.errors import wrap_errors
from i18n.i18n import translate


settings = Blueprint('settings', __name__, template_folder=VIEWS_PATH)


@settings.route('/settings')
@wrap_errors
def show_settings():
    current_space_id = space_id()
    current_delivery_token = delivery_token()
    current_preview_token = preview_token()

    errors = check_errors(
        current_space_id,
        current_delivery_token,
        current_preview_token
    )

    if errors:
        restore_session_to_last_valid_values()

    space = contentful().space(api_id())
    return render_with_globals(
        'settings',
        title=translate('settingsLabel', locale().code),
        errors=errors,
        has_errors=bool(errors),
        success=False,
        space=space,
        is_using_custom_credentials=is_using_custom_credentials(session),
        space_id=current_space_id,
        delivery_token=current_delivery_token,
        preview_token=current_preview_token,
        host=request.url_root
    )


@settings.route('/settings', methods=['POST'])
@wrap_errors
def save_settings():
    space_id = request.values.get('spaceId', None)
    delivery_token = request.values.get('deliveryToken', None)
    preview_token = request.values.get('previewToken', None)
    editorial_features = bool(request.values.get('editorialFeatures', False))

    errors = check_errors(space_id, delivery_token, preview_token)

    if not errors:
        update_session_for('space_id', space_id)
        update_session_for('delivery_token', delivery_token)
        update_session_for('preview_token', preview_token)
        update_session_for('editorial_features', 'enabled' if editorial_features else 'disabled')

    space = contentful().space(api_id())
    return render_with_globals(
        'settings',
        title=translate('settingsLabel', locale().code),
        errors=errors,
        has_errors=bool(errors),
        success=not bool(errors),
        space=space,
        is_using_custom_credentials=is_using_custom_credentials(session),
        host=request.url_root
    ), 201 if not errors else 409


@settings.route('/settings/reset', methods=['POST'])
@wrap_errors
def reset_settings():
    session.pop('space_id', None)
    session.pop('delivery_token', None)
    session.pop('preview_token', None)
    session.pop('editorial_features', None)

    space = contentful().space(api_id())

    return render_with_globals(
        'settings',
        title=translate('settingsLabel', locale().code),
        errors={},
        has_errors=False,
        success=False,
        space=space,
        is_using_custom_credentials=is_using_custom_credentials(session),
        host=request.url_root
    )


def restore_session_to_last_valid_values():
    """Restores last valid credentials."""

    session['space_id'] = session.get(
        'last_valid_space_id',
        environ.get('CONTENTFUL_SPACE_ID')
    )
    session['delivery_token'] = session.get(
        'last_valid_delivery_token',
        environ.get('CONTENTFUL_DELIVERY_TOKEN')
    )
    session['preview_token'] = session.get(
        'last_valid_preview_token',
        environ.get('CONTENTFUL_PREVIEW_TOKEN')
    )

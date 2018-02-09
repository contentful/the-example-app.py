from flask import render_template, request, session, redirect, url_for
from os import environ, path
from contentful.errors import HTTPError
from contentful.locale import Locale

from lib.breadcrumbs import breadcrumbs
from i18n.i18n import translate
from services.contentful import Contentful


VIEWS_PATH = path.join(path.dirname(__name__), '..', 'views')
DEFAULT_API = 'cda'
DEFAULT_LOCALE_CODE = 'en-US'
DEFAULT_LOCALE = Locale({
    'code': DEFAULT_LOCALE_CODE,
    'name': 'U.S. English',
    'default': True
})


def before_request():
    """Updates session with values coming from the query string if present.
    If credentials are invalid, set error flag, for error wrapper to redirect
    to settings page.
    """

    if is_changing_credentials() and not session.get('has_errors', False):
        errors = check_errors(
            request.args.get(
                'space_id',
                environ.get('CONTENTFUL_SPACE_ID', None)
            ),
            request.args.get(
                'delivery_token',
                environ.get('CONTENTFUL_DELIVERY_TOKEN', None)
            ),
            request.args.get(
                'preview_token',
                environ.get('CONTENTFUL_PREVIEW_TOKEN', None)
            )
        )

        session['has_errors'] = bool(errors)
        if errors:
            session['last_valid_space_id'] = space_id()
            session['last_valid_delivery_token'] = delivery_token()
            session['last_valid_preview_token'] = preview_token()

        for key in ['space_id', 'delivery_token', 'preview_token']:
            update_session_for(key)
        update_session_for('editorial_features', coercion=lambda x: x == 'enabled')

        if errors:
            return redirect(url_for('settings.show_settings'))
    else:
        if session.get('has_errors', False):
            del session['has_errors']


def is_changing_credentials():
    """Checks if the sent query string is attempting to change the current credentials."""

    current_space_id = space_id()
    current_delivery_token = delivery_token()
    current_preview_token = preview_token()

    attempted_space_id = request.args.get('space_id', None)
    attempted_delivery_token = request.args.get('delivery_token', None)
    attempted_preview_token = request.args.get('preview_token', None)

    return (
        (attempted_space_id is not None and
            current_space_id != attempted_space_id) or
        (attempted_delivery_token is not None and
            current_delivery_token != attempted_delivery_token) or
        (attempted_preview_token is not None and
            current_preview_token != attempted_preview_token)
    )


def update_session_for(key, with_value=None, coercion=None):
    """Updates session.

    :param key: Session key to update. If no 'with_value' sent,
                looks for that value in the query string.
    :param with_value: Value to store in the session.
    :param coercion: Coercion to apply to the value before storing.
    """

    if key in request.args:
        if with_value is None:
            with_value = request.args[key]
        if coercion is not None:
            with_value = coercion(with_value)
    if with_value is not None:
        session[key] = with_value


def contentful():
    """Returns an instance of the Contentful service with the found credentials."""

    return Contentful.instance(
        space_id(),
        delivery_token(),
        preview_token(),
        environ.get('CONTENTFUL_HOST', None)
    )


def locales():
    """Returns the list of available locales."""

    try:
        return contentful().space(api_id).locales
    except HTTPError:
        return [DEFAULT_LOCALE]


def locale():
    """Returns the currently selected locale."""

    try:
        for locale in locales():
            if locale.code == request.args.get('locale', DEFAULT_LOCALE_CODE):
                return locale
    except HTTPError:
        return DEFAULT_LOCALE


def api_id():
    """Returns the currently selected API ID."""

    return request.args.get('api', DEFAULT_API)


def current_api():
    """Returns the currently selected API data."""
    return {
        'cda': {
            'label': translate('contentDeliveryApiLabel', locale().code),
            'id': 'cda'
        },
        'cpa': {
            'label': translate('contentPreviewApiLabel', locale().code),
            'id': 'cpa'
        }
    }[api_id()]


def query_string():
    """Returns a sanitized query string."""

    rejected_keys = [
        'space_id',
        'delivery_token',
        'preview_token',
        'editorial_features'
    ]
    args = {k: v for k, v
            in request.args.items()
            if k not in rejected_keys}

    if not args:
        return ''
    return '?{0}'.format(
        '&'.join(
            '{0}={1}'.format(k, v) for k, v
            in args.items()
        )
    )


def raw_breadcrumbs():
    """Returns the breadcrumbs for the current request."""

    return breadcrumbs(request.path, locale().code)


def format_meta_title(title, locale):
    """Formats the title and localizes it.

    :param title: Current page title.
    :param locale: Desired locale.
    :return: Localized formatted string.
    """
    if not title:
        return translate('defaultTitle', locale)
    return "{0} - {1}".format(
        title.capitalize(),
        translate('defaultTitle', locale)
    )

def parameterized_url():
    """Formats a query string url with deep link
    parameters for space, delivery key and preview key.
    """

    session_space_id = session.get('space_id', None)
    session_delivery_token = session.get('delivery_token', None)
    session_preview_token = session.get('preview_token', None)
    session_editorial_features = session.get('editorial_features', None)
    current_api_id = api_id()
    editorial_features_query = "&editorial_features=enabled" if session_editorial_features and session_editorial_features is not None else "&editorial_features=disabled"

    if (session_space_id is not None and
        session_space_id != environ['CONTENTFUL_SPACE_ID'] and
        session_delivery_token is not None and
        session_delivery_token != environ['CONTENTFUL_DELIVERY_TOKEN'] and
        session_preview_token is not None and
        session_preview_token != environ['CONTENTFUL_PREVIEW_TOKEN']):
        return "?space_id={0}&preview_token={1}&delivery_token={2}&api={3}{4}".format(session_space_id, session_preview_token, session_delivery_token, current_api_id, editorial_features_query)

    return ""


def check_errors(space_id, delivery_token, preview_token):
    """Checks if sent space_id, delivery_token and preview_token
    are a valid combination. Returns formatted output for error
    display on each field.

    :param space_id
    :param delivery_token
    :param preview_token

    :return: Formated errors dict.
    """

    errors = {}

    check_field_required(errors, space_id, 'spaceId')
    check_field_required(errors, delivery_token, 'deliveryToken')
    check_field_required(errors, preview_token, 'previewToken')

    if not errors:
        validate_space_token_combination(errors, space_id, delivery_token)
        validate_space_token_combination(errors, space_id, preview_token, True)

    return errors


def check_field_required(errors, element, field_name):
    """Checks if a required field is present."""

    if not element:
        append_error_message(
            errors,
            field_name,
            translate('fieldIsRequiredLabel', locale().code)
        )


def append_error_message(errors, field_name, message):
    """Appends error message to errors dict."""

    if field_name not in errors:
        errors[field_name] = []
    if message not in errors[field_name]:
        errors[field_name].append(message)


def validate_space_token_combination(
        errors, space_id, access_token, is_preview=False):
    """Validates if client is authenticated."""

    try:
        Contentful.create_client(space_id, access_token, is_preview)
    except HTTPError as e:
        token_field = 'previewToken' if is_preview else 'deliveryToken'

        if e.status_code == 401:
            error_label = 'deliveryKeyInvalidLabel'
            if is_preview:
                error_label = 'previewKeyInvalidLabel'

            append_error_message(
                errors,
                token_field,
                translate(error_label, locale().code)
            )
        elif e.status_code == 404:
            append_error_message(
                errors,
                'spaceId',
                translate('spaceOrTokenInvalid', locale().code)
            )
        else:
            append_error_message(
                errors,
                token_field,
                translate('somethingWentWrongLabel', locale().code)
            )


def space_id():
    """Returns the current space ID."""

    return session.get(
        'space_id',
        environ.get('CONTENTFUL_SPACE_ID', None)
    )


def delivery_token():
    """Returns the current delivery token."""

    return session.get(
        'delivery_token',
        environ.get('CONTENTFUL_DELIVERY_TOKEN', None)
    )


def preview_token():
    """Returns the current preview token."""

    return session.get(
        'preview_token',
        environ.get('CONTENTFUL_PREVIEW_TOKEN', None)
    )


def render_with_globals(template_name, **params):
    """Renders the desired template with the shared state included.

    :param template_name: Name of the template to render.
    :param params: Additional state to send to the template.
    :return: Rendered template.
    """

    global_parameters = {
        'title': None,
        'locales': locales(),
        'current_locale': locale(),
        'current_api': current_api(),
        'current_path': request.path,
        'query_string': query_string(),
        'breadcrumbs': raw_breadcrumbs(),
        'editorial_features': session.get('editorial_features', '').lower() == 'enabled'.lower(),
        'space_id': space_id(),
        'delivery_token': delivery_token(),
        'preview_token': preview_token(),
        'environ': environ
    }
    global_parameters.update(params)

    return render_template(
        '{0}.html'.format(template_name),
        **global_parameters
    )

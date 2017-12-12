from flask import render_template, request, session
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
    """Updates session with values coming from the query string if present."""

    update_session_for('space_id')
    update_session_for('delivery_token')
    update_session_for('preview_token')
    update_session_for(
        'enable_editorial_features',
        coercion=lambda value: value is not None
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
        session.get(
            'space_id',
            environ.get('CONTENTFUL_SPACE_ID', None)
        ),
        session.get(
            'delivery_token',
            environ.get('CONTENTFUL_DELIVERY_TOKEN', None)
        ),
        session.get(
            'preview_token',
            environ.get('CONTENTFUL_PREVIEW_TOKEN', None)
        )
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
        'enable_editorial_features'
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
        'editorial_features': session.get('enable_editorial_features', False),
        'space_id': session.get(
            'space_id',
            environ.get('CONTENTFUL_SPACE_ID', None)
        ),
        'delivery_token': session.get(
            'delivery_token',
            environ.get('CONTENTFUL_DELIVERY_TOKEN', None)
        ),
        'preview_token': session.get(
            'preview_token',
            environ.get('CONTENTFUL_PREVIEW_TOKEN', None)
        ),
        'environ': environ
    }
    global_parameters.update(params)

    return render_template(
        '{0}.html'.format(template_name),
        **global_parameters
    )

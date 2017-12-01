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
    update_session_for('space_id')
    update_session_for('delivery_token')
    update_session_for('preview_token')
    update_session_for('editorial_features')


def update_session_for(key, with_value=None):
    if key in request.args:
        if with_value is None:
            session[key] = request.args[key]
        else:
            session[key] = with_value


def contentful():
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
    try:
        return contentful().space(api_id).locales
    except HTTPError:
        return [DEFAULT_LOCALE]


def locale():
    try:
        for locale in locales():
            if locale.code == request.args.get('locale', DEFAULT_LOCALE_CODE):
                return locale
    except HTTPError:
        return DEFAULT_LOCALE


def api_id():
    return request.args.get('api', DEFAULT_API)


def current_api():
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
    return breadcrumbs(request.path, locale().code)


def format_meta_title(title, locale):
    if not title:
        return translate('defaultTitle', locale)
    return "{0} - {1}".format(
        title.capitalize(),
        translate('defaultTitle', locale)
    )


def render_with_globals(template_name, **params):
    global_parameters = {
        'title': None,
        'current_locale': locale(),
        'current_api': current_api(),
        'current_path': request.path,
        'query_string': query_string(),
        'breadcrumbs': raw_breadcrumbs(),
        'editorial_features': session.get('editorial_features', False),
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
        'format_meta_title': format_meta_title,
        'translate': translate
    }
    global_parameters.update(params)

    return render_template(
        '{0}.html'.format(template_name),
        **global_parameters
    )

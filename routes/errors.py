import traceback
from os import environ
from functools import wraps
from contentful.errors import HTTPError, EntryNotFoundError

from routes.base import render_with_globals


def wrap_errors(route_fn):
    @wraps(route_fn)
    def decorated_function(*args, **kwargs):
        try:
            return route_fn(*args, **kwargs)
        except EntryNotFoundError as e:
            return render_error(404, e, traceback.format_exc())
        except HTTPError as e:
            return render_error(e.status_code, e, traceback.format_exc())
        except Exception as e:
            return render_error(500, e, traceback.format_exc())
    return decorated_function


def render_error(status_code, error, stacktrace):
    return render_with_globals(
        'error',
        error=error,
        stacktrace=stacktrace,
        status=status_code,
        environment=environ.get('APP_ENV', None)
    ), status_code

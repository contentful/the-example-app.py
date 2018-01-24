import os
from datetime import timedelta

from flask import Flask, session
from flask_sslify import SSLify
from dotenv import load_dotenv

from i18n.i18n import I18n
from lib.entry_state import should_show_entry_state
from lib.markdown import markdown

from routes.base import before_request, format_meta_title, parameterized_url
from routes.errors import pretty_json

from routes.index import index
from routes.courses import courses
from routes.imprint import imprint
from routes.settings import settings


DEFAULT_PORT = 3000
STATIC_FOLDER_PATH = os.path.join(os.path.dirname(__file__), 'public')

# Load global settings
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize app
app = Flask(
    __name__,
    static_url_path='',
    static_folder=STATIC_FOLDER_PATH
)

# Set app environment
app.debug = os.environ.get('APP_ENV', 'development') != 'production'

# Register session secret and properties
# This will purposely fail if not found
app.secret_key = os.environ['SESSION_SECRET']

# On localhost, Secure cookies are not retrieved from the browser in newer
# Chrome and Firefox versions. So to test, we need to disable secure cookies.
app.config['SESSION_COOKIE_SECURE'] = not app.debug
app.config['REMEMBER_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_HTTPONLY'] = True

# Set session timeout to 2 days
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=2)


# Make session cookie-based
def set_session_permanency():
    session.permanent = True


# Register Markdown engine
app.add_template_filter(markdown)

# Register HTTPS Extension
SSLify(app)
app.config['PREFERRED_URL_SCHEME'] = 'https'

# Register I18n engine
I18n(app)

# Assign Before Request Filters
app.before_request(set_session_permanency)
app.before_request(before_request)

# Request Route Middleware
app.register_blueprint(index)
app.register_blueprint(courses)
app.register_blueprint(imprint)
app.register_blueprint(settings)

# Register Helpers
app.add_template_global(format_meta_title)
app.add_template_global(parameterized_url)
app.add_template_global(should_show_entry_state)
app.add_template_filter(pretty_json)


if __name__ == '__main__':
    app.run(
        port=int(os.environ.get('PORT', DEFAULT_PORT)),
        threaded=True
    )

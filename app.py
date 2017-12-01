import os
from datetime import timedelta

from flask import Flask, session
from flask_misaka import Misaka
from flask_sslify import SSLify
from dotenv import load_dotenv

from i18n.i18n import initialize_translations

from routes.base import before_request

from routes.index import index
from routes.courses import courses
from routes.imprint import imprint
from routes.settings import settings


DEFAULT_PORT = 3000

# Load global settings
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

if os.environ.get('APP_ENV', 'development') == 'production':
    app.debug = False
else:
    app.debug = True

# Register Session Secret
app.secret = os.environ['SESSION_SECRET']  # This will purposely fail if not found

# Set session timeout to 2 days
# Session will refresh on each visit
@app.before_request
def set_session_timeout():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=2)

# Register Markdown engine
Misaka(app)

# Register HTTPS Extension
SSLify(app)

# Initialize translation engine
initialize_translations()

# Assign Before Request Filter
app.before_request(before_request)

# Add Route Middleware
app.register_blueprint(index)
app.register_blueprint(courses)
app.register_blueprint(imprint)
app.register_blueprint(settings)


if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', DEFAULT_PORT)))

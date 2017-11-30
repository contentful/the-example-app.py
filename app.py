import os

from flask import Flask
from flask_misaka import Misaka
from dotenv import load_dotenv

from i18n.i18n import initialize_translations

from routes.base import before_request
from routes.courses import courses


DEFAULT_PORT = 3000

# Load global settings
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

# Register Markdown engine
Misaka(app)

# Initialize translation engine
initialize_translations()

# Assign Before Request Filter
app.before_request(before_request)

# Add Route Middleware
app.register_blueprint(courses)


if __name__ == '__main__':
    app.run(port=os.environ.get('PORT', DEFAULT_PORT))

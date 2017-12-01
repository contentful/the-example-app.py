from flask import Blueprint

from routes.base import locale, render_with_globals, VIEWS_PATH
from routes.errors import wrap_errors
from i18n.i18n import translate


imprint = Blueprint('imprint', __name__, template_folder=VIEWS_PATH)


@imprint.route('/imprint')
@wrap_errors
def show_imprint():
    return render_with_globals(
        'imprint',
        title=translate('imprintLabel', locale().code)
    )

import CommonMark
from flask import Markup


def markdown(text):
    """Filter for turning text into markdown.

    :param text: String to be transformed.
    :return: Transformed html string.

    Usage:

        {{ 'Some *markdown*'|markdown }}
        "Some <strong>markdown</strong>"
    """
    return Markup(CommonMark.commonmark(text))

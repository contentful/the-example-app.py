import json
import os
import glob

TRANSLATIONS = {}

FALLBACK_LOCALE_CODE = 'en-US'


def I18n(app):
    """Initializes the I18n engine.

    :param app: An object that answers to 'add_template_filter(fn)'.
    """

    if TRANSLATIONS:
        return

    locales_path = os.path.join(
        os.path.dirname(__file__), '..', 'public', 'locales', 'json'
    )

    try:
        for file_name in glob.glob(os.path.join(locales_path, '*.json')):
            locale_name = os.path.basename(file_name).replace('.json', '')

            with open(file_name, 'r', encoding='utf8') as f:
                TRANSLATIONS[locale_name] = json.loads(f.read())

        app.add_template_filter(trans)
    except Exception as e:
        print('Error loading localization files.')
        print(e)


def trans(symbol, locale='en-US'):
    """Translation filter for templates.
    Fetches the current locale from the request.

    :param symbol: String to be localized.
    :param locale: String representing locale to localize in.
    :return: Localized string.

    Usage:

        {{ 'coursesLabel'|trans(current_locale.code) }}
        "Courses"
    """

    return translate(symbol, locale)


def translate(symbol, locale='en-US'):
    """Translates a symbol for a given locale.

    :param symbol: String to be localized.
    :param locale: Locale file to look the localization at.
    :return: Localized string.

    Usage:

        >>> translate('coursesLabel', 'en-US')
        "Courses"
    """

    locale_dict = TRANSLATIONS.get(locale, None)
    if locale_dict is None:
        locale_dict = TRANSLATIONS[FALLBACK_LOCALE_CODE]

    translated_value = locale_dict.get(symbol, None)
    if translated_value is None:
        return 'Translation not found for {0} in {1}'.format(symbol, locale)

    return translated_value


def is_translation_available(symbol, locale='en-US'):
    """Returns if a translation is available for the symbol in a given locale.

    :param symbol: String to be localized.
    :param locale: Locale file to look the localization at.
    :return: True/False

    Usage:

        >>> is_translation_available('coursesLabel', 'en-US')
        True
        >>> is_translation_available('nonExistent', 'en-US')
        False
        >>> is_translation_available('coursesLabel', 'non-Existent')
        False
    """

    return bool(TRANSLATIONS.get(locale, {}).get(symbol, False))

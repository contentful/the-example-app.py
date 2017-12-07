from i18n.i18n import translate, is_translation_available


def breadcrumbs(path, locale_code):
    """Generated breadcrumb data from a path on a specific locale.

    :param path: URL Path to generate breadcrumbs from.
    :param locale_code: Locale into which translate known parts of the breadcrumbs.
    :return: Array of dictionaries with breadcrumb information.

    Usage:

        >>> breadcrumbs('/', 'en-US')
        [{'url': '/', 'label': 'Home'}]

        >>> breadcrumbs('/courses/hello-world', 'de-DE')
        [{'url': '/', 'label': 'Startseite'},
         {'url': '/courses', 'label': 'Kurse'},
         {'url': '/courses/hello-world', 'label': 'hello-world'}]
    """

    crumbs = []

    crumbs.append({
        'url': '/',
        'label': translate('homeLabel', locale_code)
    })

    parts = path.split('/')[1:]

    for index, part in enumerate(parts):
        label = part.replace('-', ' ')
        if is_translation_available('{0}Label'.format(label), locale_code):
            label = translate('{0}Label'.format(label), locale_code)

        path = '/'.join(parts[0:index + 1])

        crumbs.append({
            'url': '/{0}'.format(path),
            'label': label
        })
    return crumbs


def refine(crumbs, resource):
    """Refines breadcrumbs with resource titles when matching.

    :param crumbs: Array of dictionaries with breadcrumb information.
    :param resource: A Contentful entry, which contains a slug and title.
    :return: Array of dictionaries with breadcrumb information.

    Usage:

        >>> refine(breadcrumbs('/courses/hello-world', 'en-US'), course)
        [{'url': '/', 'label': 'Home'},
         {'url': '/courses', 'label': 'Courses'},
         {'url': '/courses/hello-world', 'label': 'Hello world'}]
    """

    for crumb in crumbs:
        if crumb['label'].replace(' ', '-') == resource.slug:
            crumb['label'] = resource.title
            break
    return crumbs

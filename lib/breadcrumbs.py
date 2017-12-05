from i18n.i18n import translate, is_translation_available


def breadcrumbs(path, locale_code):
    crumbs = []

    crumbs.append({
        'url': '/',
        'label': translate('homeLabel', locale_code)
    })

    parts = path.split('/')[1:-1]

    for index, part in enumerate(parts):
        label = part.replace('-', ' ')
        if is_translation_available('{0}Label'.format(label), locale_code):
            label = translate('{0}Label'.format(label), locale_code)

        path = '/'.join(parts[0:index])

        crumbs.append({
            'url': '/{0}'.format(path),
            'label': label
        })
    return crumbs


def refine(crumbs, resource):
    for crumb in crumbs:
        if crumb['label'].replace(' ', '-') == resource.slug:
            crumb['label'] = resource.title
            break
    return crumbs

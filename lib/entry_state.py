from routes.base import contentful
from contentful.errors import EntryNotFoundError


def published_entry(entry, service=contentful):
    """Returns the published version of a preview entry.

    :param entry: Entry from the Preview API.
    :param service: Contentful service source.
    :return: Contentful Delivery Entry.
    """

    try:
        return service().entry(entry.id, 'cda')
    except EntryNotFoundError:
        return None


def attach_entry_state(entry, service=contentful):
    """Attachs entry state to a preview entry.

    :param entry: Entry from the Preview API.
    :param service: Contentful service source.
    """

    delivery_entry = published_entry(entry, service)

    entry.__dict__['draft'] = any(
        delivery_resource is None
        for _preview_resource, delivery_resource
        in known_resources_for(entry, delivery_entry)
    )
    entry.__dict__['pending_changes'] = any(
        has_pending_changes(
            preview_resource,
            delivery_resource
        ) for preview_resource, delivery_resource
        in known_resources_for(entry, delivery_entry)
    )


def known_resources_for(preview_entry, delivery_entry):
    """Returns matching resources between Preview and Delivery APIs.
    We check only for the main resource itself and for nested modules.

    :param preview_entry: Entry from the Preview API.
    :param delivery_entry: Entry from the Delivery API.
    :return: Array of tuples with matching resources.
    """

    resources = []
    for field, value in preview_entry.fields().items():
        if 'modules' in field:
            for preview_resource in value:
                resources.append((
                    preview_resource,
                    find_matching_resource(
                        preview_resource,
                        delivery_entry,
                        field
                    )
                ))
    resources.append((preview_entry, delivery_entry))

    return resources


def find_matching_resource(preview_resource, delivery_entry, search_field):
    """Returns matching resource for a specific field.

    :param preview_resource: Entry from the Preview API to match.
    :param delivery_entry: Entry to search from, from the Delivery API.
    :param search_field: Field in which to search in the delivery entry.
    :return: Entry from the Delivery API or None.
    """

    for delivery_resource in delivery_entry.fields().get(search_field, []):
        if preview_resource.id == delivery_resource.id:
            return delivery_resource


def has_pending_changes(preview_entry, delivery_entry):
    """Returns wether or not an entry has pending changes.

    :param preview_entry: Entry from the Preview API.
    :param delivery_entry: Entry from the Delivery API.
    :return: True/False
    """

    if preview_entry is None or delivery_entry is None:
        return False

    sanitized_preview_updated_at = sanitize_datetime(
        preview_entry.updated_at
    )
    sanitized_delivery_updated_at = sanitize_datetime(
        delivery_entry.updated_at
    )

    return sanitized_preview_updated_at != sanitized_delivery_updated_at


def sanitize_datetime(date):
    """In order to have a more accurate comparison due to minimal delays
    upon publishing entries. We strip milliseconds from the dates we compare.

    :param date: datetime.datetime
    :return: datetime.datetime without milliseconds.
    """

    return date.replace(microsecond=0)


def should_show_entry_state(entry, current_api_id):
    """Returns wether or not entry state should be shown.

    :param entry: Contentful entry.
    :param current_api_id: Current API selected.
    :return: True/False
    """

    return (
        current_api_id == 'cpa' and
        (
            entry.__dict__.get('draft', False) or
            entry.__dict__.get('pending_changes', False)
        )
    )


def should_attach_entry_state(current_api_id, session):
    """Returns wether or not entry state should be attached

    :param current_api_id: Current API selected.
    :param session: Current session data.
    :return: True/False
    """

    return (
        current_api_id == 'cpa' and
        bool(session.get('editorial_features', None))
    )

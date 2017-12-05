from flask import session
from routes.base import contentful, current_api
from contentful.errors import EntryNotFoundError


def published_entry(entry):
    try:
        return contentful().entry(entry.id, 'cda')
    except EntryNotFoundError:
        return None


def attach_entry_state(entry):
    delivery_entry = published_entry(entry)

    entry.__dict__['draft'] = delivery_entry is None
    entry.__dict__['pending_changes'] = has_pending_changes(entry, delivery_entry)


def has_pending_changes(preview_entry, delivery_entry):
    return (
        preview_entry is not None and
        delivery_entry is not None and
        preview_entry.updated_at != delivery_entry.updated_at
    )


def should_show_entry_state(entry):
    return (
        current_api()['id'] == 'cpa' and
        entry.__dict__.get('draft', False) and
        entry.__dict__.get('pending_changes', False)
    )


def should_attach_entry_state():
    return (
        current_api()['id'] == 'cpa' and
        session.get('editorial_features', False)
    )

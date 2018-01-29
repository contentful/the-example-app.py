from contentful import Client
from contentful.errors import EntryNotFoundError


class Contentful(object):
    """Service wrapping both Delivery and Preview APIs.
    Allows to run queries against either API.
    """

    @classmethod
    def instance(klass, space_id, delivery_token, preview_token, host=None):
        """Returns an instance of the Contentful service.
        Only changes the instance if different credentials are sent.
        """

        if '_instance' not in klass.__dict__:
            klass._instance = None

        if (
              klass._instance is None or
              klass._instance.space_id != space_id or
              klass._instance.delivery_token != delivery_token or
              klass._instance.preview_token != preview_token
           ):
            klass._instance = klass(space_id, delivery_token, preview_token, host)
        return klass._instance

    @classmethod
    def create_client(klass, space_id, access_token, is_preview=False, host=None):
        """Creates a Contentful Delivery or Preview API client."""
        if host is None:
            host = "contentful"

        options = {
            'application_name': 'the-example-app.py',
            'application_version': '1.0.0',
            'api_url': 'cdn.{0}.com'.format(host)
        }
        if is_preview:
            options['api_url'] = 'preview.{0}.com'.format(host)            

        return Client(space_id, access_token, **options)

    def client(self, api_id):
        """Returns the Delivery or Preview API client."""

        if api_id == 'cda':
            return self.delivery_client
        return self.preview_client

    def space(self, api_id):
        """Returns the current space."""

        return self.client(api_id).space()

    def courses(self, api_id, locale, options=None):
        """Fetches all courses."""

        if options is None:
            options = {}

        query = {
            'content_type': 'course',
            'locale': locale,
            'order': '-sys.createdAt',
            'include': 6
        }
        query.update(options)

        return self.client(api_id).entries(query)

    def course(self, slug, api_id, locale):
        """Fetches a course by slug."""

        courses = self.courses(api_id, locale, {
            'fields.slug': slug
        })
        if courses:
            return courses[0]
        raise EntryNotFoundError(
            'Course not found for slug: {0}'.format(slug)
        )

    def courses_by_category(self, category_id, api_id, locale):
        """Fetches all courses for a category."""

        return self.courses(
            api_id,
            locale,
            {'fields.categories.sys.id': category_id}
        )

    def categories(self, api_id, locale):
        """Fetches all categories."""

        return self.client(api_id).entries({
            'content_type': 'category',
            'locale': locale
        })

    def landing_page(self, slug, api_id, locale):
        """Fetches a landing page by slug."""

        pages = self.client(api_id).entries({
            'content_type': 'layout',
            'locale': locale,
            'include': 6,
            'fields.slug': slug
        })
        if pages:
            return pages[0]
        raise EntryNotFoundError(
            'Landing Page not found for slug: {0}'.format(slug)
        )

    def entry(self, entry_id, api_id):
        """Fetches an entry by ID."""

        return self.client(api_id).entry(entry_id, {'include': 6})

    def __init__(self, space_id, delivery_token, preview_token, host=None):
        self.space_id = space_id
        self.delivery_token = delivery_token
        self.preview_token = preview_token
        self.host = host

        self.delivery_client = self.__class__.create_client(
            space_id,
            delivery_token,
            host = host
        )
        self.preview_client = self.__class__.create_client(
            space_id,
            preview_token,
            True,
            host = host
        )

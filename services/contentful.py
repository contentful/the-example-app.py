from contentful import Client
from contentful.errors import EntryNotFoundError


class Contentful(object):
    @classmethod
    def instance(klass, space_id, delivery_token, preview_token):
        if '_instance' not in klass.__dict__:
            klass._instance = None

        if (
              klass._instance is None or
              klass._instance.space_id != space_id or
              klass._instance.delivery_token != delivery_token or
              klass._instance.preview_token != preview_token
           ):
            klass._instance = klass(space_id, delivery_token, preview_token)
        return klass._instance

    @classmethod
    def create_client(klass, space_id, access_token, is_preview=False):
        options = {
            'application_name': 'the-example-app.py',
            'application_version': '1.0.0'
        }
        if is_preview:
            options['api_url'] = 'preview.contentful.com'

        return Client(space_id, access_token, **options)

    def client(self, api_id):
        if api_id == 'cda':
            return self.delivery_client
        return self.preview_client

    def space(self, api_id):
        return self.client(api_id).space()

    def courses(self, api_id, locale, options=None):
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
        courses = self.courses(api_id, locale, {
            'fields.slug': slug
        })
        if courses:
            return courses[0]
        raise EntryNotFoundError(
            'Course not found for slug: {0}'.format(slug)
        )

    def courses_by_category(self, category_id, api_id, locale):
        return self.courses(
            api_id,
            locale,
            {'fields.categories.sys.id': category_id}
        )

    def categories(self, api_id, locale):
        return self.client(api_id).entries({
            'content_type': 'category',
            'locale': locale
        })

    def landing_page(self, slug, api_id, locale):
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
        return self.client(api_id).entry(entry_id)

    def __init__(self, space_id, delivery_token, preview_token):
        self.space_id = space_id
        self.delivery_token = delivery_token
        self.preview_token = preview_token

        self.delivery_client = self.__class__.create_client(
            space_id,
            delivery_token
        )
        self.preview_client = self.__class__.create_client(
            space_id,
            preview_token,
            True
        )

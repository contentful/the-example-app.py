from flask import Blueprint, redirect, url_for, session
from contentful.errors import EntryNotFoundError

from routes.base import contentful, \
                        api_id, \
                        locale, \
                        render_with_globals, \
                        raw_breadcrumbs, \
                        VIEWS_PATH
from lib.breadcrumbs import refine
from lib.entry_state import should_attach_entry_state, \
                            attach_entry_state
from routes.errors import wrap_errors
from i18n.i18n import translate


courses = Blueprint('courses', __name__, template_folder=VIEWS_PATH)


@courses.route('/courses')
@wrap_errors
def show_courses():
    courses = contentful().courses(api_id(), locale().code)
    categories = contentful().categories(api_id(), locale().code)

    if should_attach_entry_state():
        for course in courses:
            attach_entry_state(course)

    return render_with_globals(
        'courses',
        title='{0} ({1})'.format(
            translate('allCoursesLabel', locale().code),
            len(courses)
        ),
        courses=courses,
        categories=categories
    )


@courses.route('/courses/categories')
def courses_categories_route():
    return redirect(url_for('show_courses'))


@courses.route('/courses/categories/<category_slug>')
@wrap_errors
def show_courses_by_category(category_slug):
    categories = contentful().categories(api_id(), locale().code)

    active_category = None
    for category in categories:
        if category.slug == category_slug:
            active_category = category
            break
    if active_category is None:
        raise EntryNotFoundError(
            'Category not found for slug: {0}'.format(category_slug)
        )

    courses = contentful().courses_by_category(
        active_category.id,
        api_id(),
        locale().code
    )

    if should_attach_entry_state():
        for course in courses:
            attach_entry_state(course)

    return render_with_globals(
        'courses',
        title='{0} ({1})'.format(active_category.title, len(courses)),
        courses=courses,
        categories=categories,
        breadcrumbs=refine(raw_breadcrumbs(), active_category)
    )


@courses.route('/courses/<slug>')
@wrap_errors
def find_courses_by_slug(slug):
    course = contentful().course(slug, api_id(), locale().code)
    lessons = course.lessons

    visited_lessons = session.get('visited_lessons', [])
    if course.id not in visited_lessons:
        visited_lessons.append(course.id)
    session['visited_lessons'] = visited_lessons

    if should_attach_entry_state():
        attach_entry_state(course)

    return render_with_globals(
        'course',
        title=course.title,
        course=course,
        lessons=lessons,
        lesson=None,
        next_lesson=lessons[0] if len(lessons) > 0 else None,
        visited_lessons=visited_lessons,
        breadcrumbs=refine(raw_breadcrumbs(), course)
    )


@courses.route('/courses/<slug>/lessons')
def course_by_slug_lessons_route(slug):
    return redirect(url_for('find_courses_by_slug', slug=slug))


@courses.route('/courses/<course_slug>/lessons/<lesson_slug>')
@wrap_errors
def find_lesson_by_slug(course_slug, lesson_slug):
    course = contentful().course(course_slug, api_id(), locale().code)
    lessons = course.lessons

    lesson = None
    for l in lessons:
        if l.slug == lesson_slug:
            lesson = l
            break
    if lesson is None:
        raise EntryNotFoundError(
            'Lesson not found for slug: {0}'.format(lesson_slug)
        )

    visited_lessons = session.get('visited_lessons', [])
    if lesson.id not in visited_lessons:
        visited_lessons.append(lesson.id)
    session['visited_lessons'] = visited_lessons

    next_lesson = find_next_lesson(lessons, lesson.slug)

    if should_attach_entry_state():
        attach_entry_state(course)
        attach_entry_state(lesson)

    return render_with_globals(
        'course',
        title=course.title,
        course=course,
        lessons=lessons,
        lesson=lesson,
        next_lesson=next_lesson,
        visited_lessons=visited_lessons,
        breadcrumbs=refine(
            refine(
                raw_breadcrumbs(),
                course
            ),
            lesson
        )
    )


def find_next_lesson(lessons, lesson_slug=None):
    if lesson_slug is None:
        return lessons[0] if len(lessons) > 0 else None

    for index, lesson in enumerate(lessons):
        if lesson.slug == lesson_slug:
            return lessons[index + 1] if len(lessons) > index + 1 else None

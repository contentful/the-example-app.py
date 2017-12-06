import os

ANALYTICS_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'analytics.html'
)
LAYOUT_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..',
    '..',
    'views',
    'layout.html'
)

def append_analytics():
    layout_content = None
    analytics_content = None

    with open(LAYOUT_FILE, 'r') as lf:
        layout_content = lf.read()
    with open(ANALYTICS_FILE, 'r') as af:
        analytics_content = af.read()

    layout_content = layout_content.replace('<!--ANALYTICS-->', analytics_content)

    with open(LAYOUT_FILE, 'w') as lf:
        lf.write(layout_content)


if __name__ == '__main__':
    append_analytics()

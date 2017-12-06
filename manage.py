import sys
from bin.vendor import deploy

# This file is here only for Heroku to statically build assets

if __name__ == '__main__':
    if 'collectstatic' in sys.argv:
        deploy.append_analytics()

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#DATABASE_URI = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
#    dbuser=os.environ['DBUSER'],
#    dbpass=os.environ['DBPASS'],
#    dbhost=os.environ['DBHOST'],
#    dbname=os.environ['DBNAME']
#)

DATABASE_URI = 'sqlite:///tokens.db'

TIME_ZONE = 'UTC'

STATICFILES_DIRS = (str(BASE_DIR.joinpath('static')),)
STATIC_URL = 'static/'


FLASK_RUN_PORT=80
FLASK_RUN_HOST="0.0.0.0"

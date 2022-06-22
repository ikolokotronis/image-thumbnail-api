web: gunicorn image_thumbnail_api.wsgi:application --log-file - --log-level debug
python manage.py collectstatic --noinput
manage.py migrate


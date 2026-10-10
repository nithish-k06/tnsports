release: python manage.py check_db && python manage.py migrate
web: gunicorn soprts.wsgi:application --bind 0.0.0.0:$PORT

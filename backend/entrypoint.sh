python manage.py migrate
python manage.py collectstatic --noinput
cp -r /app/collected_static/. /backend_static/static/
python manage.py add_ingridients
python manage.py add_tags
gunicorn foodgram.wsgi:application --bind 0:8000 

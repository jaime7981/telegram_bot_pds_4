workers=2
errorlog = "/django/logs/django_web_app.gunicorn.error"
accesslog = "/django/logs/django_web_app.gunicorn.access"
loglevel = "debug"

bind = ['0.0.0.0:8000']
# Django App

## Carpetas y Archivos Importantes
## manage.py
Descripcion: archivo ejecutable que permite ejecutar ciertas acciones de la app, se usa tipo `python manage.py algun_comando`
### Comandos tipicos
 - makemigrations: Si ya existe una bbdd, prepara los datos para ser migrados luego de algun cambio en los modelos
 - migrate: Migra los datos en la bbdd para quebpuedan ser utilizados efectivamente
## telegram_bot
Descripcion: Es la carpeta que contiene la configuracion de la app, creada con el comando `django-admin createproject telegram_bot` 
 - urls.py: Es el archivo que contiene las rutas
 - settings.py: Contiene la configuracion de la app, asi como base de datos, ruta de archivos estaticos, etc.
## bot_api
Descripcion: Es un modulo creado con el comando `python manage.py startapp bot_api`, aqui se pueden encontrar la configuracion de modelos, vistas, se pueden agregar rutas y serializadores, etc.
 - views.py: Renderiza vistas en forma de funciones o clases, generalmente las rutas (url) toma como argumento alguna funcion de aqui
 - models.py: Aqui se definen los modelos de la bbdd, asi como campos (int, char, file, etc) y relaciones (pk)
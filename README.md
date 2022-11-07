# Telegram Bot PDS 4

## Run Docker
 - Abrir app docker desktop
 - En consola o GUI hacer build si se han echo cambios
 - Correr contenedores (Localmente no es necesario correr certbot)
 - Si se quiere hacer build y correr todos contenedores usar con con comando `docker-compose up --build`
 - Si solo se quiere hacer correr lo contenedores `docker-compose up`
 - Correr sin logs `docker-compose up -d`
 - Listar contenedores `docker ps`
 - Entrar en un contenedor `docker exec -it {nombre contenedor} bash`

## Make Bot Requests
 - https://api.telegram.org/bot<token>/METHOD_NAME
 - set Webhook: `curl -F "url=https://developmentcl.xyz/webhook/" https://api.telegram.org/bot5668389701:AAHWwdNxz6fbX3lh4RfhSyuZvnHpOFHT9IQ/setWebhook`
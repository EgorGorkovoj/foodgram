# Проект Foodgram
### Описание:
**Проект Foodgram** сайт, на котором пользователи могут публиковать свои **рецепты**, добавлять чужие рецепты в **избранное** и **подписываться** на публикации других авторов. Зарегистрированные пользователи также будет доступен сервис **«Список покупок»**. Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Технологии:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)

## Запуск проекта в контейнере
Клонируйте репозиторий и перейдите в него в командной строке.
Создайте и активируйте виртуальное окружение, установите зависимости:
```
git clone https://github.com/Seniacat/Foodgram.git
cd foodgram
python -m venv venv
source venv/Script/activate
python -m pip install --upgrade pip
cd backend
pip install -r requirements.txt
```
Должен быть свободен порт 8080. PostgreSQL поднимается на 5432 порту, он тоже должен быть свободен.
Cоздать и открыть файл .env с переменными окружения:
```
touch .env
```
Заполнить .env файл с переменными окружения по примеру (SECRET_KEY см. в файле settings.py):
```
POSTGRES_DB=postgres
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=my_password
DB_NAME=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=*********
DEBUG=False
ALLOWED_HOSTS=**.**.**.**,localhost,127.0.0.1,your.domen.com
```
Установить и запустить приложения в контейнерах (образ для контейнера загружается из DockerHub):
```
$ docker compose -f docker-compose.production.yml up --build
```
Запустить миграции, создать суперюзера, собрать статику и заполнить в БД таблицы с ингредиентами:
```
docker compose -f docker.compose.production.yml exec backend python manage.py migrate

docker compose -f docker.compose.production.yml exec backend python manage.py createsuperuser

docker compose -f docker.compose.production.yml exec backend python manage.py collectstatic

docker compose -f docker.compose.production.yml exec backend python manage.py cp -r /app/collected_static/. /backend_static/static/

docker compose -f docker.compose.production.yml execc backend python manage.py load_ingredients
```

### Доп. информация.
Все API эндпоинта можно посмотреть в документации к проекту по адресу:
```
http://localhost/api/docs/
```

### Автор
- [Горьковой Егор](https://github.com/EgorGorkovoj)
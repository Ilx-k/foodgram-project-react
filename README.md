![foodgram-project-react Workflow Status](https://github.com/xofmdo/foodgram-project-react/actions/workflows/main.yml/badge.svg) 

# Продуктовый помощник Foodgram  

 

Адрес сайта: https://piratefoodgram.zapto.org/  

 

Email администратора: ilkham.kashapov@gmail.com 

Логин администратора: Ilxpirate 

Пароль администратора: admin49  

 

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/) 

[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/) 

[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/) 

[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/) 

[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/) 

[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/) 

[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/) 

[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/) 

[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub) 

[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions) 

[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=008080)](https://cloud.yandex.ru/) 

 

## Описание проекта Foodgram 

Это онлайн-сервис и API для него. На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 

 

 

## Инструкции по установке 

### Локальная установка 

1. Клонируйте репозиторий: 

``` 

git clone git@github.com:Ilx-k/foodgram-project-react.git 

cd foodgram-project-react 

``` 

 

2. В корневом каталоге создайте файл .env, с переменными окружения. 

/POSTGRES_USER=**** 

/POSTGRES_PASSWORD=**** 

/POSTGRES_DB=**** 

/DB_HOST=db 

/DB_PORT=5432 

/SECRET_KEY=**** 

/ALLOWED_HOSTS=**** 

/DEBUG_MODE=False 

 

3. Создайте виртуальное окружение: 

``` 

python -m venv venv 

``` 

4. Активируйте виртуальное окружение 

* для Linux/Mac: 

```source venv/bin/activate``` 

 

* для Windows: 

```source venv/Scripts/activate``` 

 

4. Установите зависимости из файла requirements.txt: 

``` 

pip install -r backend/requirements.txt 

``` 

5. В foodgram/setting.py замените PostgreSQL на встроенную SQLite: 

``` 

DATABASES = { 

    'default': { 

        'ENGINE': 'django.db.backends.sqlite3', 

        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'), 

    } 

} 

``` 

 

6. Примените миграции: 

``` 

python manage.py makemigrations 

python manage.py migrate 

``` 

7. Соберите статику: 

``` 

python manage.py collectstatic --no-input 

``` 

8. Создайте суперпользователя: 

``` 

python manage.py createsuperuser 

``` 

9. Загрузите данные в модель (ингредиенты): 

``` 

python manage.py load 

``` 

10. В папке с файлом manage.py выполните команду для запуска локально: 

``` 

python manage.py runserver 

``` 

Локально документация доступна по адресу: 

``` 

http://127.0.0.1:8000/api/docs/ 

``` 

 

### Запуск проекта в контейнерах: 

 

1. Установить docker и docker-compose. 

[Инструкция по установки (Win/Mac/Linux)](https://docs.docker.com/compose/install/) 

 

- Linux: 

``` 

sudo apt install curl                                    

curl -fsSL https://get.docker.com -o get-docker.sh       

sh get-docker.sh                                         

sudo apt-get install docker-compose-plugin               

``` 

 

 

2. Cоздайте и заполните .env файл в корневом каталоге  

``` 

POSTGRES_USER=**** 

POSTGRES_PASSWORD=**** 

POSTGRES_DB=**** 

DB_HOST=db 

DB_PORT=5432 

SECRET_KEY=**** 

ALLOWED_HOSTS=**** 

DEBUG_MODE=False 

 

``` 

 

3. Из папки infra/ разверните контейнеры при помощи docker-compose: 

``` 

docker-compose up -d --build 

``` 

4. Выполните миграции: 

``` 

docker-compose exec backend python manage.py makemigrations 

docker-compose exec backend python manage.py migrate 

``` 

5. Создайте суперпользователя: 

``` 

docker-compose exec backend python manage.py createsuperuser 

``` 

6. Соберите статику: 

``` 

docker-compose exec backend python manage.py collectstatic --no-input 

``` 

7. Наполните базу данных (ингредиентами).  

``` 

docker-compose exec backend python manage.py add_tags 

docker-compose exec backend python manage.py add_ingredients 

``` 

Проект доступен по адресу: 

 

``` 

http://localhost/ 

``` 

Документация доступна по адресу: 

``` 

http://localhost/api/docs/ 

``` 

8. Остановка проекта: 

``` 

docker-compose down 

``` 

 

## Инфраструктура проекта 

**Главная** - https://localhost/recipes/ \ 

**API** - https://localhost/api/ \ 

**Redoc** - https://localhost/api/docs/ \ 

**Админка** -https://localhost/admin/ 

 

## Примеры запросов 

1. Получение списка рецептов: \ 

   **GET** `/api/recipes/` \ 

   REQUEST 

   ```json 

   { 

     "count": 123, 

     "next": "http://127.0.0.1:8000/api/recipes/?page=2", 

     "previous": "http://127.0.0.1:8000/api/recipes/?page=1", 

     "results": [ 

       { 

         "id": 0, 

         "tags": [ 

           { 

             "id": 0, 

             "name": "Завтрак", 

             "color": "green", 

             "slug": "breakfast" 

           } 

         ], 

         "author": { 

           "email": "ya@ya.ru", 

           "id": 0, 

           "username": "user", 

           "first_name": "Ivan", 

           "last_name": "Zivan", 

           "is_subscribed": false 

         }, 

         "ingredients": [ 

           { 

             "id": 0, 

             "name": "Курица", 

             "measurement_unit": "г", 

             "amount": 100 

           } 

         ], 

         "is_favorited": false, 

         "is_in_shopping_cart": false, 

         "name": "string", 

         "image": "https://backend:8000/media/recipes/images/image.jpeg", 

         "text": "string", 

         "cooking_time": 10 

       } 

     ] 

   } 

   ``` 

2. Регистрация пользователя: \ 

   **POST** `/api/users/` \ 

   RESPONSE 

   ```json 

   { 

     "email": "ya@ya.ru", 

     "username": "user", 

     "first_name": "Ivan", 

     "last_name": "Zivan", 

     "password": "super_password1" 

   } 

   ``` 

   REQUEST 

   ```json 

   { 

   "email": "ya@ya.ru", 

   "id": 0, 

   "username": "user", 

   "first_name": "Ivan", 

   "last_name": "Zivan" 

   } 

   ``` 

3. Подписаться на пользователя: \ 

   **POST** `/api/users/{id}/subscribe/` 

   REQUEST 

   ```json 

   { 

     "email": "user@example.com", 

     "id": 0, 

     "username": "user", 

     "first_name": "Ivan", 

     "last_name": "Zivan", 

     "is_subscribed": true, 

     "recipes": [ 

       { 

         "id": 0, 

         "name": "string", 

         "image": "https://backend:8000/media/recipes/images/image.jpeg", 

         "cooking_time": 10 

       } 

     ], 

     "recipes_count": 1 

   } 

   ``` 

## Об авторе 

Ilkham Kashapov 

https://github.com/Ilx-k 

 

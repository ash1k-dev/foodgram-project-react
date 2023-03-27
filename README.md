# Проект "Foodgram"
[![API for YaMDB project workflow](https://github.com/ash1k-dev/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/ash1k-dev/foodgram-project-react/actions/workflows/main.yml)



## Описание проекта:

Проект "Foodgram" создан для публикации своих рецептов и просмотра рецептов других пользователей с возможностью подписки. Присутствует функция фильтрации и выгрузки необходимых продуктов для понравившиегося блюда


## Технологии:

- Python 3
- Django
- Django REST Framework
- Djoser
- Docker
- Nginx
- Postgres

# Установка:

1. Клонируйте репозиторий и перейдите в него:

```sh
cd foodgram-project-react
```

2. В директории infra создайте файл .env(), согласно примеру:
   
```sh
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

3. Запустите контейнеры с помощью docker-compose:


```sh
docker-compose up -d 
```

4. Заполните БД:
   
```sh
docker-compose exec web python manage.py makemigrations --noinput
docker-compose exec web python manage.py migrate --noinput
```

5. Создайте суперпользователя:
   
```sh
docker-compose exec web python manage.py createsuperuser
```

6. Соберите статические файлы:
   
```sh
docker-compose exec web python manage.py collectstatic --no-input
```

7. Заполните БД тестовыми данными:
   
```sh
docker-compose exec web python manage.py load_ingridients
```

Автор проекта: [Роман Третьяков](https://github.com/ash1k-dev)
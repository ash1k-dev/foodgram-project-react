# Проект "Foodgram"
[![API for YaMDB project workflow](https://github.com/ash1k-dev/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/ash1k-dev/foodgram-project-react/actions/workflows/main.yml)

## ip сервера: 51.250.11.18

## Логин для входа:yandex

## Пароль: practicum

## Email: yandex@yandex.ru


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


# Установка(на сервере):

1. Установите на сервере Docker, Docker Compose:

```sh
sudo apt install curl                            
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh                                        
sudo apt-get install docker-compose-plugin   
```

2. Разместите на сервере файлы docker-compose.yml, nginx.conf
   

3. Создайте переменные окружения для GitHub Actions:


```sh
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # пароль для ssh
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```

4. Заполните БД:
   
```sh
sudo docker-compose exec web python manage.py makemigrations --noinput
sudo docker-compose exec web python manage.py migrate --noinput
```

5. Создайте суперпользователя:
   
```sh
sudo docker-compose exec web python manage.py createsuperuser
```

6. Соберите статические файлы:
   
```sh
sudo docker-compose exec web python manage.py collectstatic --no-input
```

7. Заполните БД тестовыми данными:
   
```sh
sudo docker-compose exec web python manage.py load_ingridients
```

# Установка(локально):

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
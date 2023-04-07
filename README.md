## *Foodgram*
___

## *Описание проекта*
«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты,
добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
___

### *Технологии*
- Python 3.7
- Django 3.2
- Djangorestframework 3.13.1
- Docker
___

## *Запуск проекта в контейнере*
Скачать и установить [Docker](https://www.docker.com/).
Зайти в директорию infra и выполнить команды:
```sh
docker-compose up -d

docker-compose exec backend python manage.py makemigrations

docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py collectstatic --no-input

docker-compose exec backend python manage.py import_csv

docker-compose exec backend python manage.py createsuperuser
```
** На Linux запускать команды через sudo.
___

## *Дополнительная информация*

Backend проекта подготовил [Орлов Сергей](https://github.com/sergio7523).

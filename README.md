### *Технологии*
- Python 3.7
- Django 3.2
- Djangorestframework 3.13.1
- Docker
___

## *Описание проекта*
«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты,
добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
___


## *Запуск проекта в контейнере*
Для запуска проекта в контейнерах у Вас должен быть установлен [Docker](https://www.docker.com/).
Зайти в папку infra и выполнить команды:
- docker-compose up -d
- docker-compose exec backend python manage.py makemigrations
- docker-compose exec backend python manage.py migrate
- docker-compose exec backend python manage.py collectstatic --no-input
- docker-compose exec backend python manage.py import_csv
- docker-compose exec backend python manage.py createsuperuser
___

## *Дополнительная информация*

Backend проекта подготовил [Орлов Сергей](https://github.com/sergio7523).

«Продуктовый помощник» — это сайт, на котором можно публиковать собственные рецепты,
добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.

Технологии:

Python 3.7
Django 3.2

Запуск приложения в контейнерах:

sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py collectstatic --no-input
sudo docker-compose exec backend python manage.py import_csv
sudo docker-compose exec backend python manage.py createsuperuser
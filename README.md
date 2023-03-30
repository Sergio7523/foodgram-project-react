# praktikum_new_diplom

```bash
docker-compose up -d --build
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py import_csv
docker-compose exec backend python manage.py createsuperuser
```
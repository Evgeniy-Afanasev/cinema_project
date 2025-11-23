# Run app:
> docker compose -f docker-compose.yml up -d --build

# Run app with tests:
> docker compose -f docker-compose.tests.yml up -d --build

# Stop app:
> docker compose -f docker-compose.yml -f docker-compose.tests.yml down -v

# Create superuser
> В контейнере авторизации выполнить
> python create_superuser.py --email email@email.com --login login --password pass

# movies api doc:
> http://localhost/movies/api/openapi#/

# auth doc
> http://localhost/auth/docs#/
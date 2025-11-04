# Run app:
> docker compose -f docker-compose.yml up -d --build

# Run app with tests:
> docker compose -f docker-compose.tests.yml up -d --build

# Stop app:
> docker compose -f docker-compose.yml -f docker-compose.tests.yml down -v

# Api doc:
> http://localhost/api/openapi
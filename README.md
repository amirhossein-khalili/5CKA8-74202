# Guide to Running the Project

This guide covers both Docker Compose and Makefile methods for launching the booking system.

---

## Prerequisites

- **Docker** (and Docker Engine running)
- **Docker Compose**
- **Make**
- **Python 3.12+** (for local management commands)
- **PostgreSQL** (if not using Docker for the database)

Ensure you have cloned the repository and are in its root directory.

### 1. Using Docker Compose

1. Copy the example environment:

   ```bash
   cp example.env .env
   # Edit .env to configure DB credentials, JWT secrets, etc.
   ```

2. Build and start all services:

   ```bash
   docker-compose up --build
   ```

3. Apply migrations and seed data (in a separate shell):

   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py seed_restaurant
   ```

4. The API will be available at `http://localhost:8000/api/`.

### 2. Using the Makefile

1. Copy and configure environment variables:

   ```bash
   cp example.env .env
   ```

2. Start the PostgreSQL service (named in Docker Compose):

   ```bash
   make postgres
   ```

3. Run database migrations:

   ```bash
   python manage.py migrate
   ```

4. Seed the database:

   ```bash
   make seed  # or `python manage.py seed_restaurant`
   ```

5. Launch the development server:

   ```bash
   python manage.py runserver
   ```

---

## Accessing the API & Documentation

- **Swagger UI**: `http://localhost:8000/swagger/`
- **Postman Collection**: `docs/postman/restaurant-booking.postman_collection.json`

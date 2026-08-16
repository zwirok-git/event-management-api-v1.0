# Event Management API

REST API for creating and managing events, user registration, event participation, JWT authentication, filtering, search, and automatic event archiving.

## Tech Stack

- Python 3.13
- Django 6.1
- Django REST Framework 3.18
- PostgreSQL 17
- Redis 7
- Celery + Celery Beat
- Simple JWT
- drf-spectacular / Swagger UI
- django-filter
- Docker / Docker Compose

## Features

- User registration
- JWT authentication and token refresh
- Current-user (`me`) endpoint
- Create, list, and retrieve events
- Event registration / unregistration
- Organizer-only participant list
- Event capacity management
- `members_count` and `left_places`
- Search by event title and location
- Filtering by location
- Ordering by start date, title, and maximum capacity
- Pagination
- Automatic archiving of finished events with Celery Beat
- OpenAPI schema and Swagger UI
- PostgreSQL and Redis through Docker Compose

## API Documentation

After starting the application, Swagger UI is available at:

```text
http://localhost:8000/api/docs/
```

OpenAPI schema:

```text
http://localhost:8000/api/schema/
```

## Authentication

The API uses JWT authentication.

### Register

```http
POST /api/users/signup/
```

Example:

```json
{
  "username": "alex",
  "first_name": "Alex",
  "last_name": "Smith",
  "email": "alex@example.com",
  "password": "StrongPassword123!",
  "repeat_password": "StrongPassword123!"
}
```

### Login

```http
POST /api/users/login/
```

Returns an access token and refresh token.

Use the access token in protected requests:

```http
Authorization: Bearer <access_token>
```

### Refresh token

```http
POST /api/users/token/refresh/
```

Example:

```json
{
  "refresh": "<refresh_token>"
}
```

## Users

### Current user

```http
GET /api/users/me/
```

The endpoint also supports:

```text
PUT   /api/users/me/
PATCH /api/users/me/
DELETE /api/users/me/
```

Authentication is required.

## Events

### List events

```http
GET /api/events/
```

The event list is publicly available.

Events that have been archived are excluded from the queryset.

### Create event

```http
POST /api/events/
```

Authentication is required.

Example:

```json
{
  "title": "Python Meetup",
  "description": "Django and Python discussion",
  "start_date": "2026-09-01 18:00",
  "location": "Kyiv",
  "max_members": 20
}
```

The organizer is taken from the authenticated user and cannot be supplied by the client.

### Event details

```http
GET /api/events/{id}/
```

The endpoint is publicly available.

The response depends on the authenticated user:

- Public users receive public event information.
- The event organizer additionally receives the list of registered members.

### Register for an event

```http
POST /api/events/{id}/register/
```

Authentication is required.

A user cannot:

- register twice;
- register for their own event;
- register after the event has started;
- register when the event is full.

### Unregister from an event

```http
DELETE /api/events/{id}/unregister/
```

Authentication is required.

### Event deletion

Events are intentionally not exposed through `DELETE /api/events/{id}/`.

Finished events are archived automatically instead.

## Filtering, Search and Ordering

### Filtering

Filter by location:

```http
GET /api/events/?location=Kyiv
```

### Search

Search by title or location:

```http
GET /api/events/?search=python
```

### Ordering

Supported ordering fields:

- `start_date`
- `title`
- `max_members`

Examples:

```http
GET /api/events/?ordering=start_date
GET /api/events/?ordering=-start_date
GET /api/events/?ordering=title
```

### Combining parameters

```http
GET /api/events/?location=Kyiv&search=python&ordering=start_date
```

## Pagination

The API uses DRF `LimitOffsetPagination`.

Example:

```http
GET /api/events/?limit=10&offset=20
```

Default page size:

```text
20
```

## Event Archiving

Finished events are automatically archived by Celery.

The scheduled task:

```text
events.tasks.archive_finished_events
```

runs daily at:

```text
00:01 UTC
```

It marks events whose `start_date` has passed as archived.

Archived events are no longer returned by the public event queryset.

## Project Structure

```text
event-management-api/
├── config/
│   ├── celery.py
│   ├── env.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
│   └── models/
│       └── base.py
├── events/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── urls.py
│   └── views.py
├── users/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── manage.py
```

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Environment variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=change-me
POSTGRES_DB=event_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0
```

Do not commit `.env` to the repository.

### Start the project

```bash
docker compose up --build
```

The application automatically applies Django migrations before starting the development server.

The services are:

```text
app     Django application
db      PostgreSQL
redis   Redis
celery  Celery worker
beat    Celery Beat scheduler
```

The API will be available at:

```text
http://localhost:8000/
```

Swagger:

```text
http://localhost:8000/api/docs/
```

### Create a superuser

```bash
docker compose exec app python manage.py createsuperuser
```

### Stop the project

```bash
docker compose down
```

To remove the persistent database and Redis volumes as well:

```bash
docker compose down -v
```

## Running Locally Without Docker

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure PostgreSQL and Redis, then run:

```bash
python manage.py migrate
python manage.py runserver
```

Run Celery worker:

```bash
celery -A config worker -l info
```

Run Celery Beat:

```bash
celery -A config beat -l info
```

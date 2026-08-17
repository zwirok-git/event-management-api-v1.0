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

- REST API built with Django REST Framework
- User registration
- JWT authentication and token refresh
- Current-user (`me`) endpoint
- Create, list, retrieve, update, and delete events
- Organizer-specific event details
- Event registration / unregistration
- Organizer cannot register for their own event
- Event capacity validation
- Registration is closed once the event has started
- `members_count`, `left_places`, and `is_registered`
- Search by event title, location, and organizer username
- Filtering by location and organizer username
- Ordering by start date, title, and maximum capacity
- Limit/offset pagination
- Automatic archiving of finished events with Celery Beat
- Django Admin for users and events
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

Archived events are excluded from the public event queryset.

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

The start date cannot be in the past.

The title and location are normalized by trimming surrounding whitespace.

An organizer cannot create another event with the same title, location, and start time.

### Event details

```http
GET /api/events/{id}/
```

The endpoint is publicly available.

The response depends on the authenticated user:

- Public users receive public event information.
- The event organizer additionally receives the list of registered members.
- `is_registered` indicates whether the authenticated user is registered for the event.

### Update an event

```http
PUT /api/events/{id}/
PATCH /api/events/{id}/
```

Only the event organizer can update the event.

An event cannot be updated after a participant has registered for it.

Update operations use a database transaction and row-level locking with `select_for_update()` to protect this business rule when registration and modification happen concurrently.

### Delete an event

```http
DELETE /api/events/{id}/
```

Only the event organizer can delete the event.

An event cannot be deleted after a participant has registered for it.

Delete operations use a database transaction and row-level locking with `select_for_update()`.

### Register for an event

```http
POST /api/events/{id}/register/
```

Authentication is required.

A user cannot:

- register twice;
- register for their own event;
- register when the event is full;
- register after the event has started.

Registration uses a database transaction and row-level locking to prevent concurrent registration from bypassing event capacity or update/delete restrictions.

### Unregister from an event

```http
DELETE /api/events/{id}/unregister/
```

Authentication is required.

A user can unregister only if they are currently registered for the event.

A successful unregistration returns HTTP `204 No Content`.

## Filtering, Search and Ordering

### Filtering

Filter by location:

```http
GET /api/events/?location=Kyiv
```

Filter by organizer username:

```http
GET /api/events/?organizer__username=alex
```

### Search

Search by title, location, or organizer username:

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
GET /api/events/?ordering=-max_members
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
00:01 Europe/Kyiv
```

The Django project timezone and Celery timezone are configured as `Europe/Kyiv`.

It marks events whose `start_date` has passed as archived.

Archived events are no longer returned by the public event queryset.

## Business Logic and Concurrency

The main event lifecycle is:

```text
Create event
     |
     v
No registered participants
     |
     +----> Organizer can update/delete
     |
     +----> Users can register
                    |
                    v
          Registered participants
                    |
                    +----> Update/Delete blocked
                    |
                    v
             Event start time
                    |
                    v
                 Archived
```

Registration, update, and delete operations use database transactions with row-level locking (`select_for_update`) to prevent concurrent operations from bypassing the event's business rules.

Unregistration intentionally does not use row-level locking because it does not participate in the critical registration/capacity/update/delete consistency path.

## Django Admin

Django Admin is available at:

```text
http://localhost:8000/admin/
```

The project registers Users and Events.

Event Admin supports filtering by archived status, start date, and location, searching by title, location, and organizer username, and ordering by start date.

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
├── .env.example
└── manage.py
```

## Running with Docker

### Prerequisites

- Docker
- Docker Compose

### Environment variables

Create a `.env` file in the project root.

Use `.env.example` as a template.

Example:

```env
SECRET_KEY=change-me
POSTGRES_DB=event_management
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://redis:6379/0

DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
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
http://localhost:8000/api/
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

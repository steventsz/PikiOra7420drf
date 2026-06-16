# Piki Ora Medical Centre API

This repository contains the Django REST Framework backend for the Piki Ora Medical Centre appointment booking system. It provides the API used by the separate React frontend application.

The project was refactored from a Django server-rendered clinic appointment system into a backend API that supports doctors, appointment slots, patient bookings, token-based authentication, and staff administration through API endpoints.

## Related Links

- Backend repository: [https://github.com/steventsz/PikiOra7420drf](https://github.com/steventsz/PikiOra7420drf)
- Frontend repository: [https://github.com/steventsz/pikiora7420react](https://github.com/steventsz/pikiora7420react)
- Backend deployment: [https://piki-ora7420drf.vercel.app/](https://piki-ora7420drf.vercel.app/)
- Frontend deployment: [https://pikiora7420react.vercel.app/](https://pikiora7420react.vercel.app/)

## Technology Stack

- Python
- Django
- Django REST Framework
- DRF Token Authentication
- SQLite for local development
- PostgreSQL support for deployed environments
- django-cors-headers for frontend API access
- Vercel deployment

## Main Features

- User registration and login
- Token-based API authentication
- Current user profile endpoint
- Doctor listing and management
- Appointment slot listing and management
- Patient appointment booking
- Appointment cancellation and status updates
- Double-booking prevention on the backend
- Role-based permissions for patients and staff users
- Admin/staff API access for managing doctors, slots, appointments, and users

## Backend Scope

This repository is only the backend API project. The React frontend is developed in a separate repository:

[https://github.com/steventsz/pikiora7420react](https://github.com/steventsz/pikiora7420react)

The Django Admin site may exist for development convenience, but the submitted administrator dashboard is intended to be implemented in the React frontend rather than Django Admin.

## API Overview

All main API endpoints are available under the `/api/` prefix.

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/login/` | Log in and receive an authentication token |
| `GET` | `/api/auth/me/` | Get the currently authenticated user |

### Doctors

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/doctors/` | List doctors |
| `POST` | `/api/doctors/` | Create a doctor, staff only |
| `GET` | `/api/doctors/{id}/` | Retrieve a doctor |
| `PUT` | `/api/doctors/{id}/` | Replace a doctor, staff only |
| `PATCH` | `/api/doctors/{id}/` | Update a doctor, staff only |
| `DELETE` | `/api/doctors/{id}/` | Delete a doctor, staff only |

### Appointment Slots

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/slots/` | List appointment slots |
| `POST` | `/api/slots/` | Create a slot, staff only |
| `GET` | `/api/slots/{id}/` | Retrieve a slot |
| `PUT` | `/api/slots/{id}/` | Replace a slot, staff only |
| `PATCH` | `/api/slots/{id}/` | Update a slot, staff only |
| `DELETE` | `/api/slots/{id}/` | Delete a slot, staff only |

Supported slot filters include:

```text
/api/slots/?doctor=1
/api/slots/?date=2026-06-17
/api/slots/?is_available=true
```

### Appointments

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/appointments/` | List appointments for the current patient, or all appointments for staff |
| `POST` | `/api/appointments/` | Book an appointment |
| `GET` | `/api/appointments/{id}/` | Retrieve an appointment |
| `PATCH` | `/api/appointments/{id}/` | Update appointment status or notes |
| `DELETE` | `/api/appointments/{id}/` | Delete an appointment |

Supported appointment filters include:

```text
/api/appointments/?status=booked
/api/appointments/?doctor=1
/api/appointments/?date=2026-06-17
/api/appointments/?slot=1
```

### Users

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/users/` | List users, staff only |
| `GET` | `/api/users/{id}/` | Retrieve a user, staff only |
| `PATCH` | `/api/users/{id}/` | Update user information, staff only |
| `DELETE` | `/api/users/{id}/` | Deactivate a user, staff only |

## Authentication

The API uses DRF token authentication. After logging in, include the returned token in authenticated requests:

```text
Authorization: Token <your-token>
```

Example login request:

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

## Default Admin Account

The deployed demo environment includes a default administrator account:

```text
username: admin
password: admin
```

This account is provided for demonstration and marking purposes only.

## Permissions Summary

- Anonymous users can view public doctor and appointment slot information.
- Authenticated patients can book appointments and manage their own appointments.
- Staff users can manage doctors, slots, appointments, and users.
- Patients cannot view or manage appointments that belong to other users.
- Staff users can view and manage all appointments.

## Booking Rules

- A user must be authenticated before booking an appointment.
- A slot can only have one active booked appointment.
- Cancelled appointments do not continue blocking the slot.
- Backend validation prevents double booking.
- Patients cannot create appointments for other users.
- Staff users can create appointments on behalf of patients.
- Existing appointments cannot be moved to another slot; the user should cancel and create a new appointment instead.

## Local Development

Clone the backend repository:

```bash
git clone https://github.com/steventsz/PikiOra7420drf.git
cd PikiOra7420drf
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

The local API will usually be available at:

```text
http://127.0.0.1:8000/api/
```

## Database Configuration

For local development, the project falls back to SQLite.

For deployed or PostgreSQL-backed environments, the project can use the following environment variables:

```text
PGHOST
PGUSER
PGDATABASE
PGPASSWORD
PGPORT
PGSSLMODE
```

If the required PostgreSQL variables are present, Django will use PostgreSQL. Otherwise, it will use the local SQLite database.

## Frontend Integration

The React frontend is deployed separately and consumes this backend API.

Frontend deployment:

[https://pikiora7420react.vercel.app/](https://pikiora7420react.vercel.app/)

Backend deployment:

[https://piki-ora7420drf.vercel.app/](https://piki-ora7420drf.vercel.app/)

CORS is enabled so the React frontend can make API requests to the Django REST Framework backend.

## Postman Collection

A Postman collection is included in this repository:

```text
postman_collection.json
```

It can be imported into Postman to inspect and try the available API endpoints.

## Project Structure

```text
PikiOra7420drf/
├── clinic/
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── viewsets.py
│   ├── urls.py
│   └── views.py
├── pikiora7420drf/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── vercel.json
├── postman_collection.json
└── README.md
```

## Notes

- This repository focuses on the backend API only.
- The administrator dashboard for the assignment is provided by the React frontend project.
- The API is designed to be consumed by a separate frontend client.
- The default admin credentials are for demonstration use in the deployed assignment environment.

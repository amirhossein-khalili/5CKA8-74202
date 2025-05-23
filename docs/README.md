# About This Project

This repository implements a **Restaurant Booking System** via a RESTful API. It is structured into three main domains:

1. **User Account**

   - **Signup** (`POST /api/accounts/signup/`): Register with username/password.
   - **Signin** (`POST /api/accounts/signin/`): Obtain JWT access & refresh tokens.
   - Authentication is enforced on booking/cancellation endpoints.

2. **Restaurant Management**

   - **Tables**: Ten tables (N = 10) configurable with M seats each (between 4 and 10).
   - Database models track table capacity and availability in time slots.

3. **Reservation**

   - **Booking** (`POST /api/reservations/book/`): Specify party size; system selects cheapest available table(s) according to:

     - **Pricing**: Seat costs X per seat; full-table booking costs (M–1) × X.
     - **Rules**: Parties cannot book an odd number of seats unless equal to full table capacity (e.g., a party of 3 gets 4 seats).

   - **Cancellation** (`POST /api/reservations/cancel/`): Cancel by reservation ID if owned by the authenticated user.

---

## Technical Stack

- **Framework**: Django + Django REST Framework
- **Database**: PostgreSQL via Django ORM
- **Auth**: JWT (Simple JWT)
- **API Spec**: OpenAPI (Swagger) auto-generated under `docs/swagger/`
- **Containerization**: Docker & Docker Compose
- **Testing**: Django TestCase (unit & integration)

---

## Project Structure

```
├── accounts/          # Signup, signin serializers, views, services, tests
├── restaurant/        # Table model, availability logic, seed command, tests
├── reservations/      # Booking/cancellation logic, pricing policy, table selection strategy, tests
├── config/            # Django settings, URL routing, WSGI/ASGI entrypoints
├── docs/              # Architecture diagrams (PlantUML), Swagger config, Postman collection
├── Dockerfile         # App image definition
├── docker-compose.yml # Service orchestration (web, db)
├── Makefile           # Convenience targets: build, up, postgres, seed, logs, shell
├── example.env        # Environment variable template
├── manage.py          # Django CLI entrypoint
└── requirements.txt   # Python dependencies
```

### Key Modules

- **accounts.services.AuthenticationFacadeService**: Coordinates sign-up/sign-in workflows, integrates with JWTService.
- **restaurant.services.table_selection.DefaultTableSelectionStrategy**: Finds cheapest available table given party size and timeslot.
- **restaurant.services.price_policy.DefaultPricingPolicy**: Computes booking cost using seat- and table-based rules.
- **reservations.services.facade.ReservationFacadeService**: Orchestrates booking & cancellation operations, interacts with repositories and policies.

Together, these components ensure a clean separation of concerns and make adding new pricing or selection strategies straightforward.

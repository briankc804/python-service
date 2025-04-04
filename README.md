# python-service

# E-commerce API
A RESTful API for managing customers, orders, and products.

## Setup
1. Clone: `git clone <repo-url>`
2. Install: `pip install -r requirements.txt`
3. Migrate: `python manage.py migrate`
4. Run: `python manage.py runserver`

## Endpoints
- GET/POST `/api/customers/`
- GET/POST `/api/orders/`
- GET `/admin/`

## Deployment
- Dockerized and deployed to render via GitHub Actions.

# Nova Cart Arcade

Nova Cart Arcade is a Django eCommerce project with two roles:

- Buyers can browse products, manage a cart, check out, and leave reviews.
- Vendors can create stores, publish products, and monitor store activity.

The app includes both HTML views and a small authenticated REST API for store,
product, and review data.

## Feature Summary

- Buyer and vendor signup with role-based dashboards.
- Store and product management for vendors.
- Session-based cart and checkout flow for buyers.
- Invoice emails sent after checkout.
- Review verification that turns on once a buyer has purchased the product.
- Password reset flow using Django's built-in auth views.

## Project Map

Use this table when you need to find the logic for a bug quickly.

| Area | Main files | Notes |
| --- | --- | --- |
| Settings and configuration | `nova_cart_arcade/settings.py` | Database setup, email backend, auth redirects, REST framework config. |
| Data model | `storefront/models.py` | Stores, products, orders, order items, reviews, and user roles. |
| Shared business logic | `storefront/services.py` | Cart helpers, checkout order creation, invoice email generation, review verification updates, and Twitter announcement helpers. |
| HTML forms | `storefront/forms.py` | Signup, store, product, review, and checkout forms. |
| Browser views | `storefront/views.py` | Dashboards, product/store CRUD, cart, checkout, and review submission. |
| API endpoints | `storefront/api_views.py` and `storefront/api_serializers.py` | Authenticated endpoints for creating stores/products and reading vendor/product data. |
| Permissions and role checks | `storefront/mixins.py` and `storefront/services.py` | Buyer/vendor gatekeeping for class-based views and helper functions. |
| Templates | `storefront/templates/` | UI for auth, catalog pages, dashboards, checkout, and order detail pages. |
| Styling and assets | `storefront/static/storefront/` | Theme CSS plus SVG assets used throughout the storefront. |
| Tests | `storefront/tests.py` | End-to-end regression coverage for signup, cart, checkout, password reset, review verification, and API behavior. |

## Workflow Guide

If you need to trace a specific behavior, start here:

- Signup and account rules: `storefront/forms.py` and `storefront/views.py`
- Cart and checkout bugs: `storefront/services.py` and `storefront/views.py`
- Review verification bugs: `storefront/views.py` and `storefront/services.py`
- Vendor CRUD bugs: `storefront/views.py`, `storefront/api_views.py`, and `storefront/api_serializers.py`
- Dashboard totals or summaries: `storefront/views.py`
- Password reset behavior: `nova_cart_arcade/urls.py` plus `storefront/templates/registration/`

## Setup

The app is configured for MariaDB during normal usage.

Set environment variables before running the server:

```powershell
$env:DJANGO_SECRET_KEY = "replace-this-with-a-secret-key"
$env:DJANGO_DEBUG = "1"
$env:NOVA_CART_DB_ENGINE = "mariadb"
$env:NOVA_CART_DB_NAME = "nova_cart_arcade"
$env:NOVA_CART_DB_USER = "root"
$env:NOVA_CART_DB_PASSWORD = "change-me"
$env:NOVA_CART_DB_HOST = "127.0.0.1"
$env:NOVA_CART_DB_PORT = "3306"
```

Install dependencies, apply migrations, and start the server:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Testing

Automated tests switch to SQLite automatically, so the suite can run without a
MariaDB service.

```bash
python manage.py test
```

## Supporting Notes

Additional planning and support documents live in these files:

- `api_quick_guide.md`
- `testing_notes.md`
- `research_answers.md`
- `Planning/`

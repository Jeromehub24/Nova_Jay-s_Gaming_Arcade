# Nova Cart Arcade

A Django eCommerce app for buyers and vendors.

## Main Features

- Vendors can create stores and manage products.
- Buyers can browse products, manage a cart, place orders, and leave reviews.
- Reviews are marked as verified when the buyer has already ordered the
  product.

## Database Setup

The project is configured for MariaDB during normal app usage.

Environment variables:

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

Install dependencies and run migrations:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Automated tests use SQLite automatically so they can run without a MariaDB
service.

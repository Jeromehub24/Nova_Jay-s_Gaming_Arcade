# Nova Cart Arcade

Nova Cart Arcade is a Django eCommerce project for gaming products. Buyers can
browse products, manage a cart, place orders, and leave reviews. Vendors can
create stores, publish products, and monitor storefront activity. The project
also includes an authenticated REST API and Sphinx-generated documentation.

## Features

- Buyer and vendor signup with role-based dashboards
- Store and product management for vendors
- Session-based cart and checkout flow
- Invoice emails after checkout
- Verified reviews once a buyer has purchased a product
- Password reset flow using Django auth views
- REST API for stores, products, and reviews
- Sphinx documentation generated from code docstrings

## Fresh Setup

These steps start from a machine that does not already have the project.

### 1. Clone the repository

```powershell
git clone https://github.com/Jeromehub24/Nova_Jay-s_Gaming_Arcade.git
cd Nova_Jay-s_Gaming_Arcade
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `pip install -r requirements.txt` fails while building `mysqlclient` on
Windows, install Microsoft C++ Build Tools and the MariaDB/MySQL Connector C,
then run the install command again.

### 3. Create the local `.env` file

Copy the example file and then update the values for your machine:

```powershell
Copy-Item .env.example .env
```

The project now loads `.env` automatically through `python-dotenv`, so you do
not need to create Windows environment variables by hand.

Important values to review in `.env`:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `NOVA_CART_DB_*`
- `DEFAULT_FROM_EMAIL`
- `EMAIL_*`

### 4. Install MySQL and create the database

This project uses MariaDB/MySQL during normal development. To make the
`mysql -u root -p` command work, install:

- MySQL Server 8.x or MariaDB Server
- MySQL Command Line Client
- A `PATH` entry that includes the MySQL `bin` directory if the command is not recognized

Example Windows path to add to `PATH` if needed:

```text
C:\Program Files\MySQL\MySQL Server 8.0\bin
```

Once MySQL is installed, create the database before running migrations:

```sql
mysql -u root -p
CREATE DATABASE nova_cart_arcade CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

If you use a different database name, update `NOVA_CART_DB_NAME` in `.env` to
match it.

### 5. Run migrations and start the server

```powershell
python manage.py migrate
python manage.py runserver
```

The development site will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Email Configuration

By default, `.env.example` uses Django's console email backend so invoice and
password reset emails are printed to the terminal during development.

To use a real SMTP server, update these `.env` values:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=you@example.com
SERVER_EMAIL=you@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=you@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
```

## Documentation

Sphinx is included in `requirements.txt`, and the docs read the project
docstrings directly from the codebase.

Build the HTML documentation from the repository root:

```powershell
.\docs\make.bat html
```

Open the generated start page:

```text
docs\_build\html\index.html
```

## Docker

The repository now includes a `Dockerfile` and `.dockerignore`.

Make sure you are in the project root before building the image:

```powershell
cd Nova_Jay-s_Gaming_Arcade
docker build -t nova-cart-arcade .
```

Run the container with the local `.env` file:

```powershell
docker run --env-file .env -p 8000:8000 nova-cart-arcade
```

If the container must connect to a MySQL server running on your Windows host,
set `NOVA_CART_DB_HOST=host.docker.internal` in `.env` before starting it.

If you want a self-contained container demo without MySQL, set
`NOVA_CART_DB_ENGINE=sqlite` in `.env` before running the container.

## Testing

Automated tests switch to SQLite automatically, so they can run without a
MariaDB service.

```powershell
python manage.py test
```

## Project Map

| Area | Main files | Notes |
| --- | --- | --- |
| Settings and configuration | `nova_cart_arcade/settings.py` | Loads `.env`, database setup, email settings, auth redirects, and REST framework config |
| Data model | `storefront/models.py` | Stores, products, orders, order items, reviews, and user roles |
| Shared business logic | `storefront/services.py` | Cart helpers, checkout flow, invoice emails, review verification updates, and social announcements |
| HTML forms | `storefront/forms.py` | Signup, store, product, review, and checkout forms |
| Browser views | `storefront/views.py` | Dashboards, catalog browsing, CRUD screens, cart, checkout, and reviews |
| API endpoints | `storefront/api_views.py` and `storefront/api_serializers.py` | Authenticated store, product, and review endpoints |
| Documentation | `docs/` | Sphinx configuration and generated module pages |
| Tests | `storefront/tests.py` | Regression coverage for auth, cart, checkout, reviews, and API behavior |

## Supporting Notes

- `api_quick_guide.md`
- `testing_notes.md`
- `research_answers.md`
- `Planning/`

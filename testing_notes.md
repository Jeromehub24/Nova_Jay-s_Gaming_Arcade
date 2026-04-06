# Testing Notes

## Automated checks I ran
- `python manage.py check`
- `python manage.py test storefront`

## What the automated tests cover
- Sign up creates the correct buyer or vendor role.
- Buyers can add products to the cart.
- Checkout creates an order and sends an invoice email.
- Platform helper links point to the expected console pages.
- Web store creation calls the tweet announcement helper.
- Vendors can create stores through the API.
- Vendors can create products through the API.
- Buyers can read vendor stores and store products through the API.
- Vendors can read product reviews through the API.

## Manual checks I would do before final submission
- Create one vendor and one buyer account in the browser.
- Create a store and product from the vendor dashboard.
- Log in as a buyer and complete a checkout.
- Reset a password using the reset flow.
- Test the API with Postman using one GET and one POST request.

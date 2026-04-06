# Access And Security Notes

## Access control
- Guests can view the public pages, but they cannot buy, review, or manage stores.
- Buyers can use the cart, checkout, and review features.
- Vendors can manage only their own stores and products.
- Vendors should not be able to edit another vendor's content.
- Buyers should not be able to access vendor create and edit pages.

## Authentication choices
- Django authentication handles login, logout, and password reset.
- Password reset uses Django tokens and expiry settings.
- API routes require an authenticated user.
- API write routes also check that the user is a vendor.

## Data protection
- The cart is stored in session so it stays linked to the current user session.
- Checkout reduces inventory only after stock is checked first.
- Reviews are marked verified only when the buyer has bought the product before.
- API product creation checks that the vendor owns the store in the URL.

## Third-party API notes
- Twitter/X credentials are read from environment variables instead of hardcoding secrets.
- If the credentials are not set, the app writes the tweet payload to `tweet_events.log`.
- This keeps the code safe for local testing while still showing the integration path.

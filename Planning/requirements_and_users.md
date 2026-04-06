# Jay's Gaming Planning Notes

## Main users

### Vendor
- Can sign up and log in.
- Can create a store.
- Can edit or delete their own store.
- Can add products to their own store.
- Can edit or delete their own products.
- Can use the API to create stores and products.
- Can read reviews through the API.

### Buyer
- Can sign up and log in.
- Can browse stores and products.
- Can add products to a cart.
- Can check out and receive an invoice email.
- Can leave reviews.
- Can use the API to view stores, products, and reviews.

## Main system requirements
- The project needs separate buyer and vendor roles.
- Carts should stay in session while the buyer is browsing.
- Orders should reduce stock when checkout is finished.
- Reviews should show whether they are verified or unverified.
- Password reset should work through email and use expiring tokens.
- The app should protect pages and API routes based on the logged-in user.
- The app should expose a basic REST API for store, product, and review data.
- The app should send a tweet-style update when a store or product is added.

## Main data I need to track
- Users and roles
- Stores
- Products
- Orders
- Order items
- Reviews

## Why this structure makes sense
- A vendor can own more than one store, so `User -> Store` is one-to-many.
- A store can contain more than one product, so `Store -> Product` is one-to-many.
- A buyer can place more than one order.
- An order can contain more than one order item.
- A review belongs to one product and one buyer.

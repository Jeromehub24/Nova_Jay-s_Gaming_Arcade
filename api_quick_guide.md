# API Quick Guide

## Authentication

The API uses normal Django authentication. For local testing, the easiest options are:
- Log in through the browser and then test with the same session.
- Use Basic Auth in Postman with a username and password.

## Endpoints

### Create a store
- `POST /api/stores/`

Example body:

```json
{
  "name": "Arcade Replay",
  "description": "Retro and new releases.",
  "logo_url": "https://example.com/logo.png"
}
```

### View stores for one vendor
- `GET /api/vendors/1/stores/`

### View products in one store
- `GET /api/stores/1/products/`

### Add a product to a store
- `POST /api/stores/1/products/`

Example body:

```json
{
  "name": "Halo Infinite",
  "description": "Shooter with campaign and multiplayer.",
  "platform": "xbox",
  "genre": "shooter",
  "price": "49.99",
  "inventory": 4,
  "image_url": "https://example.com/halo.png",
  "is_active": true
}
```

### View reviews for a product
- `GET /api/products/1/reviews/`

## Twitter/X notes

- If real Twitter/X environment variables are set, the app will try to post updates.
- If they are not set, the app writes the tweet payload into `tweet_events.log`.
- This keeps local testing simple and shows what would have been sent.

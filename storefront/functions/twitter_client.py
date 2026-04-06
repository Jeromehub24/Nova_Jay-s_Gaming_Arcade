import json
from datetime import datetime

import requests
from django.conf import settings
from requests_oauthlib import OAuth1Session


class TweetClient:
    tweet_url = "https://api.twitter.com/2/tweets"

    def credentials_ready(self):
        return all(
            [
                settings.TWITTER_ENABLED,
                settings.TWITTER_API_KEY,
                settings.TWITTER_API_SECRET,
                settings.TWITTER_ACCESS_TOKEN,
                settings.TWITTER_ACCESS_TOKEN_SECRET,
            ]
        )

    def build_session(self):
        return OAuth1Session(
            settings.TWITTER_API_KEY,
            client_secret=settings.TWITTER_API_SECRET,
            resource_owner_key=settings.TWITTER_ACCESS_TOKEN,
            resource_owner_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

    def post_update(self, text):
        payload = {"text": text}

        if not self.credentials_ready():
            return self.write_local_log(payload, status="skipped")

        try:
            response = self.build_session().post(self.tweet_url, json=payload, timeout=15)
            response.raise_for_status()
        except requests.RequestException as exc:
            return self.write_local_log(payload, status="failed", error=str(exc))

        return {"status": "sent", "response": response.json()}

    def post_store_created(self, store):
        lines = [
            "New store added on Jay's Gaming.",
            f"Store: {store.name}",
            f"Description: {store.description}",
        ]
        if store.logo_url:
            lines.append(f"Logo: {store.logo_url}")
        return self.post_update("\n".join(lines))

    def post_product_created(self, product):
        lines = [
            "New product added on Jay's Gaming.",
            f"Store: {product.store.name}",
            f"Product: {product.name}",
            f"Description: {product.description}",
        ]
        if product.image_url:
            lines.append(f"Image: {product.image_url}")
        return self.post_update("\n".join(lines))

    def write_local_log(self, payload, status, error=""):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "payload": payload,
        }
        if error:
            entry["error"] = error

        with open(settings.TWITTER_LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(entry) + "\n")

        return entry

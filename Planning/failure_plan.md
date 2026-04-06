# Failure Plan

## Cases I planned for

### Wrong user type
- If a buyer tries to create a store or product, the app should block the request.
- If a vendor tries to access buyer-only actions like cart checkout, the app should block the request.

### Missing stock
- If a buyer tries to add or buy more than the stock available, the app should stop checkout and show an error.

### Empty cart
- If checkout is attempted with an empty cart, the app should stop and show a message instead of creating a bad order.

### Bad form input
- If a form is invalid, the page should stay on the form and show the errors.

### Review edge cases
- If a buyer has not bought a product, the review is still allowed but marked unverified.
- If a buyer reviews the same product again, the existing review is updated instead of duplicating rows.

### API auth failure
- If the user is not logged in, the API should reject the request.
- If the user is logged in but does not have the correct role, the API should return a permission error.

### Twitter/X setup not ready
- If the API keys are missing, the app should not crash.
- Instead, it writes the tweet payload to a local log file so I can still see what would have been posted.

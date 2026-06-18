# Delegation: billing-agent

## FOCUS

- src/billing/
- tests/billing/

## EXCLUDE

- src/auth/
- docs/

## TASK

Implement Stripe-backed billing in src/billing/. Add checkout, webhook receiver, and invoice listing.

## SUCCESS

- pytest tests/billing/ exits 0 with at least 4 test cases
- src/billing/webhook.py validates Stripe signatures
- ruff check src/billing/ exits 0
- git diff --name-only shows only files under src/billing/ or tests/billing/

## RETURN

Markdown summary: files created, tests added, blockers, next steps.

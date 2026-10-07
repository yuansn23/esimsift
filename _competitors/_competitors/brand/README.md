# _competitors/brand/

Per-brand non-plan data (ratings, reviews, company info). One folder per brand.

## Status (generated 2026-10-04)

- `trustpilot.json` for all 5 brands (nomad / jetpac / gigsky / maya / quibity) is a
  **placeholder**: Trustpilot was deliberately NOT scraped this round (curl -> 403 WAF;
  scraping needs browser automation like the esimdb Playwright approach).
- Schema is fixed; a future scraper only fills `tp_review_url`, `rating`,
  `review_count`, `rating_distribution`, `fetched_at`.
- Jetpac's on-site aggregate rating (4.8 / 3276 reviews, from product JSON-LD) lives in
  `_competitors/plans/jetpac/jetpac_japan_offers.json` under `aggregate_rating` -
  do not duplicate it here until a real Trustpilot fetch happens.

# MarketScope

A product-research dashboard: search trending products across five
marketplaces, watch demand by country on a live world map, and let
influencers connect their accounts to an AI-driven content workflow.

## Run it

```
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000 — it will create `instance/marketscope.db`
(SQLite) and seed it with 260 realistic mock product listings across
25+ countries on first launch.

- **Seller dashboard**: register at `/register`, log in at `/login`.
- **Creator studio**: register at `/influencer/register`, log in at `/influencer/login`.

## What's real vs. mock right now

Everything except the marketplace data itself is fully real and working:

- Real user accounts (sellers + influencers), hashed passwords, sessions
- Real SQLite persistence — searches, connections, and accounts all survive restarts
- Real instant-as-you-type search hitting a live Flask API (no page reload)
- Real live-updating world map (polls `/api/countries` every 6s) and stat tiles
- Real influencer connection form that writes rows to the database and lists/deletes them

**Marketplace data is currently mocked** because Amazon, eBay, AliExpress,
Alibaba, and TikTok Shop all require you to register as an approved
developer/affiliate/seller with them directly — there's no public API key
you can just generate. See `config.py` for exactly what each platform
requires and where to apply.

## Going live with a real marketplace

Each marketplace has its own adapter in `adapters/`. They all implement
the same interface (`adapters/base.py`), so the rest of the app — search,
the dashboard, the world map — never needs to change.

1. Get approved and receive credentials from the platform (see `config.py`
   for the application URL for each one).
2. Set the matching environment variable(s), e.g.:
   ```
   export EBAY_CLIENT_ID=...
   export EBAY_CLIENT_SECRET=...
   ```
3. Restart the app. That adapter's `is_live` flips to `True` automatically
   and `/api/search` starts blending in real results from it. Every adapter
   file has a commented template showing the exact real API call to
   uncomment and fill in.

## Project layout

```
app.py                  Flask routes: auth, dashboard, search/countries/stats APIs
config.py               Env-var driven marketplace credentials
database.py             SQLite schema + mock product seeding
adapters/                One file per marketplace, same interface, mock-or-live
templates/               Login/register (seller + influencer), dashboard, connect form
static/css/style.css     Design system (dark "radar" theme)
static/js/app.js         Live search, stats, trending list
static/js/map.js         Leaflet world map with pulsing demand markers
```

## Notes

- The world map uses Leaflet.js with free CARTO dark basemap tiles (no
  API key required).
- "Live" trend numbers include a small intentional jitter on each poll so
  the map and stats visibly move — in production this would instead be
  driven by real-time marketplace data refreshes.
- This is a development server (`app.run`). For real deployment, run it
  behind gunicorn/uwsgi and switch `DB_PATH` to a persistent volume.

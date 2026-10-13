<<<<<<< HEAD
# LinkSnap — Simple URL Shortener

A polished URL shortener built with **Flask** and **SQLite**. It includes a responsive frontend, JSON API, custom short codes, click tracking, and a redirect route.

## Features

- Generate unique 7-character short codes for long URLs
- Optional custom aliases (4–32 letters/numbers)
- SQLite database created automatically in `data/shortener.db`
- `GET /<short_code>` redirect route with click tracking
- JSON API for creating, listing, and looking up links
- Responsive frontend with copy-to-clipboard and recent links
- Automated tests for core API behavior

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> in your browser.

## API

### Create a short URL

```bash
curl -X POST http://127.0.0.1:5000/api/shorten \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.example.com/a/very/long/path"}'
```

Optional custom code:

```json
{"url":"https://example.com", "custom_code":"home"}
```

### List recent URLs

`GET /api/urls`

### Get one URL

`GET /api/urls/<short_code>`

## Configuration

- `PORT` — server port, default `5000`
- `DATABASE_PATH` — optional SQLite database path
- `FLASK_DEBUG=1` — enable Flask debug mode for local development

## Run tests

```bash
pytest -q
```

## Production notes

For production, run behind a WSGI server such as Gunicorn, use a persistent database volume, add rate limiting, and configure trusted proxy/host settings.
=======
# URL-Shortener
>>>>>>> def50db93a0c7b17a9d95ac2d9006d60fee23c2a

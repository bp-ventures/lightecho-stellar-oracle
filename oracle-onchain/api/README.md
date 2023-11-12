Create `.env`:

```
GUNICORN_BIND=localhost:8000
GUNICORN_WORKERS=1
GUNICORN_TIMEOUT=30
```

Create `local_settings.py`:

```
from werkzeug.security import generate_password_hash

CONTRACTS = {
  "XLM": "<XLM-based contract id>",
  "USD": "<USD-based contract id>",
}

# HTTP Basic authorized users
API_USERS = {
    "john": generate_password_hash("hello"),
    "susan": generate_password_hash("bye")
}
```

Install dependencies:

```
poetry install
```

Run server:

```
poetry run flask --app server run --reload
# or
poetry run gunicorn -w 4 server:app
```

# Using the API

## Authentication

Some endpoints require HTTP Basic authentication.  
The list authorized of users and passwords is defined by the above `API_USERS` setting.  
See endpoints below for more detailed instructions and examples.

## Endpoints

### Add prices to a deployed contract

```
curl -X POST "http://localhost:5000/soroban/add-price/" \
  -H "Authorization: Basic a2V5OnZhbHVl" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "source": 2,
    "symbol": "XLMUSDC",
    "asset_type": "other",
    "price": "1.2"
  }'
```

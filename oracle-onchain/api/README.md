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

# HTTP Basic read-only authorized users
READONLY_API_USERS = {
    "publicuser1": generate_password_hash("password1"),
    "publicuser2": generate_password_hash("password2")
}
```

Install dependencies:

```
poetry install
```

Install `ttm` task manager:
```
pip install -U ttm
```

Run server:

```
ttm run --name server ./server.sh
```

Add scripts to cron:
```bash
crontab -e

# add the following to the bottom of file (REPLACE /path/to with correct dir)
0 0 * * 1 /path/to/lightecho-stellar-oracle/oracle-onchain/api/db_delete_old_data.sh
```

To see log file:
```
tail ./data/server.log
```

For status/start/stop/logs the server:
```
ttm ls -a
ttm stop server
ttm start server
ttm logs server
```

To run in development mode:
```
poetry run flask --app server run --reload
```

# Using the API

## Authentication

Some endpoints require HTTP Basic authentication.  
The list authorized of users and passwords is defined by the above `API_USERS` setting.  
See endpoints below for more detailed instructions and examples.

## Endpoints

### Add prices to a deployed contract

```
curl -X POST "http://localhost:5000/db/add-prices/" \
  -H "Authorization: Basic a2V5OnZhbHVl" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "source": 2,
    "symbol": "XLMUSDC",
    "asset_type": "other",
    "price": "1.2"
  }'
```

### Get latest prices

```
curl -X POST "http://localhost:5000/db/get-prices/" \
  -H "Authorization: Basic a2V5OnZhbHVl" \
  -H "Content-Type: application/json" \
  --data-raw '{
    "source": 2,
    "symbol": "XLMUSDC",
    "asset_type": "other",
    "price": "1.2"
  }'
```

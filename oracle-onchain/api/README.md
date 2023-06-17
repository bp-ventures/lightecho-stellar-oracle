Create `local_settings.py`:

```
from werkzeug.security import generate_password_hash

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

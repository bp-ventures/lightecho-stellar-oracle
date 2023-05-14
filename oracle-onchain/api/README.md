```
poetry install

poetry run flask --app server run --reload
# or
poetry run gunicorn -w 4 server:app
```

# Server-side stuff for the World Riichi Tournaments app

I'm currently developing on Python 3.13

## running a dev server locally
`flask --app app.py run`

I run the main public instance on gunicorn:
`gunicorn  --config gunicorn.py myapp.app:application`

### installing
`pip install -r requirements.txt`

### Seating algorithm

See [seating/README](seating/README.md) for details.

# Server-side stuff for the World Riichi Tournaments app

Currently being developed, and running, on Python 3.13. It probably works on Python 3.10-3.12, but that's not tested.

## running a dev server locally
`flask --app app.py run`

I run the main public instance on gunicorn:
`gunicorn  --config gunicorn.py myapp.app:application`

### installing
`pip install -r requirements.txt`

# File structure
### ./
- `app.py` - Main Flask application setup and configuration
- `config.py` - Config for firebase, google sheets, and server config
- `models.py` - SQLAlchemy database specification
- `oauth_setup.py` - OAuth2 and login configuration
- `root.py` - Website root pages and basic routes
- `write_sheet.py` - Google Sheets integration and management

### ./accounts/
- `accounts/accounts.py` - User account management and authentication

### ./create/   
- `create/tournament_setup.py` - Tournament creation

### ./forms/
- `forms/tournament_forms.py` - Forms for tournament management
- `forms/userform.py` - Forms for user management

### ./operations/
- `operations/api.py` - API endpoint for the app to retrieve summary data of historic past tournaments
- `operations/archive.py` - Archive a finished tournament, and store its summary data; the intention here is that because historic tournaments will only increase in number, they're best taken off the google cloud (to keep requests down), so we store those on our own server.
- `operations/queries.py` - Database queries that return lists fo tournaments
- `operations/transforms.py` - Summarise tournaments

### ./run/
- `run/admin.py` - Admin panel
- `run/cloud_edit.py` - edit the tournament metadata that's stored in the google cloud
- `run/export.py` - Tournament results export for wordpress (untested)
- `run/run.py` - Tournament running and management
- `run/substitutes.py` - handle player substitution, and reducing the number of tables, mid-tournament
- `run/user_management.py` - User role and access management

### ./seating/
Contains the individual seating files, as well as the software that is used offline to generate them. e.g. `seats_5.py` contains the seating plans for all 5-hanchan tournaments, 16-172 players (=4-43 tables). The top of each seating file contains summary statistics for each arrangement.

See [seating/README](seating/README.md) for details.

### ./static/
css and js files for public and management pages, as well as customisation for individual tournaments

#### ./static/js/seating/
javascript for generating near-optimal mid-tournament seating rearrangements

### ./templates/
jinja2 templates for the website - both the public pages, and the management pages

### ./utils/
- `utils/timezones.py` - return a list of the timezones for a given country


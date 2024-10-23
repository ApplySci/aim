import pycountry
import pytz
from oauth_setup import logging


def get_timezones_for_country(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        country_code = country.alpha_2
        country_timezones = pytz.country_timezones.get(country_code, [])
        logging.info(f"Timezones for {country_name}: {country_timezones}")
        return country_timezones
    except (IndexError, KeyError):
        logging.error(f"Could not find timezones for country: {country_name}")
        return []

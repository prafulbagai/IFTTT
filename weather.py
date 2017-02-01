from datetime import datetime

import requests
import json
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c26_smartbulb.settings')

django.setup()

from c26_smartbulb.local_settings import WEATHER_URL
from modules.recipes.models import UserRecipesMapping
from utils import read_json_file
from send_gcm import send_gcm_data


def weather_cron():
    users = UserRecipesMapping.objects.filter(recipe__unique_name='weather')
    if not users:
        return {}

    gcm_data = dict()
    for user in users:
        recipe_config = json.loads(user.recipe_config)
        lat = recipe_config['lat']
        long = recipe_config['long']
        response = requests.get(WEATHER_URL % (lat, long)).json()
        weather_icon_id = response['response'].get('weather_icon')

        add_to_gcm = False
        gcm_status = user.gcm_status

        weather_type = recipe_config['weather_type']
        possible_weather_icons = read_json_file('weather_list.json')[weather_type]

        # If weather_icon in possible weather_type_values
        # and gcm has not been send, then send gcm
        if weather_icon_id in possible_weather_icons and gcm_status == 'False':
            user.gcm_status = 'True'
            user.save()
            add_to_gcm = True

        # If weather_icon not in possible_weather_values and gcm has been send
        # before, then update gcm status to False because once the forecast has
        # been again changed to normal tempaerature, we need to send gcm again
        # whenever it rains.
        if weather_icon_id not in possible_weather_icons and gcm_status == 'True':
            user.gcm_status = 'False'
            user.save()

        if add_to_gcm:
            if user in gcm_data:
                gcm_data[user.user]['data'].append(str(user.id))
            else:
                gcm_data[user.user] = {'data': [str(user.id)],
                                       'description': 'Weather is ' + str(weather_type),
                                       'datetime': str(datetime.now())}
    return gcm_data


def main():
    gcm_data = weather_cron()
    print gcm_data, datetime.now()
    if gcm_data:
        send_gcm_data(gcm_data)


if __name__ == '__main__':
    main()

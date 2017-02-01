from datetime import datetime, timedelta
import json
import os
import sys
import django
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'c26_smartbulb.settings')

django.setup()

from c26_smartbulb.local_settings import YOUTUBE_URL
from modules.recipes.models import UserRecipesMapping
from send_gcm import send_gcm_data
from utils import read_json_file


# Youtube Cron
def youtube_cron():
    users = UserRecipesMapping.objects.filter(recipe__unique_name='youtube_channel')
    if not users:
        return {}
    # Mapping all the channels with the list of users subscribe to it.
    # For eg:- {Channel1:[User1,User2,User3], Channel2:[User2]}
    user_channel_mapping = dict()
    for user in users:
        channel = json.loads(user.recipe_config)['channel_name']
        if channel in user_channel_mapping:
            user_channel_mapping[channel].append((user.user, user.id))
        else:
            user_channel_mapping[channel] = [(user.user, user.id)]

    # Getting the list of videos uploaded of
    # unique channels obtained from above.
    channels = user_channel_mapping.keys()
    channel_id_mapping = read_json_file('channel_list.json')
    channel_videos = dict()
    published_after = int(((datetime.now() + timedelta(hours=5.5) - timedelta(hours=2)) - datetime(1970, 1, 1)).total_seconds()) * 1000
    for channel in channels:
        channel_status = False
        channel_id = channel_id_mapping[channel]
        response = requests.get(YOUTUBE_URL % (channel_id,))
        try:
            response = response.json()
            if response['status'] == 200:
                videos = response['response']
                channel_status = any(video['published_at'] > published_after for video in videos)
        except:
            pass

        channel_videos[channel] = channel_status

    # Finding all those users to whom GCM will be send.
    gcm_data = dict()
    for channel, users in user_channel_mapping.items():
        channel_state = channel_videos[channel]
        if channel_state:
            for user, user_recipe_id in users:
                if user in gcm_data:
                    gcm_data[user]['data'].append(user_recipe_id)
                else:
                    gcm_data[user] = {'data': [str(user_recipe_id)],
                                      'description': 'A new video has been uploaded'}
    return gcm_data


def main():
    gcm_data = youtube_cron()
    print gcm_data, datetime.now()
    if gcm_data:
        send_gcm_data(gcm_data)


if __name__ == '__main__':
    main()

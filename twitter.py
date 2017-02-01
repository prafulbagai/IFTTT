import requests
import tweepy
from datetime import datetime as dt


class Twitter:
    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self._api = tweepy.API(auth)

    def get_user_tweets(self, query, since_id=''):
        """
        query: id/user_id/screen_name of that user
                eg.  mdmehrab, @mdmehrab
        since_id: get the tweets whose id is greater than since_id

        return (top 20 tweets if successful):
            if successful than return dict
            else  return empty dict
        """
        try:
            if since_id:
                r = self._api.user_timeline(query, since_id)
            else:
                r = self._api.user_timeline(query)
        except tweepy.error.TweepError:
            return {}
        results = []
        since_id = r.since_id
        for tweet in r:
            if hasattr(tweet, 'retweeted_status'):
                author = tweet.retweeted_status.author
                real_author = author.screen_name
                real_author_dp_url = author.profile_image_url
            else:
                author = tweet.author
                real_author = author.screen_name
                real_author_dp_url = author.profile_image_url

            results.append({
                'tweet_id': tweet.id,
                'user_dp_url': tweet.author.profile_image_url,
                'text': tweet.text,
                'retweet_count': tweet.retweet_count,
                'is_retweeted': tweet.retweeted,
                'real_author': '@' + real_author,
                'real_author_dp_url': real_author_dp_url
            })
        return {'since_id': since_id,
                'results': results}

    def is_user(self, query):
        """
        query: id/user_id/screen_name of that user
              eg.  mdmehrab, @mdmehrab

        return:
            return dict contain is_user key either true or false
            if true than it also contain id, name, etc
        """
        try:
            r = self._api.get_user(query)
        except tweepy.error.TweepError:
            return {'is_user': False}
        return {'is_user': True,
                'screen_name': r.screen_name,
                'id': r.id,
                'name': r.name,
                'dp_url': r.profile_image_url,
                }

    @classmethod
    def make_request(cls, url, params={}):
        r = requests.get(url, params=params)
        print r.url
        if r.ok:
            return r.json()
        return None

    # u can use OR, AND, NOT operator to concat query
    @classmethod
    def search_topic(cls, query, from_time=dt.now(),
                     api_key='', count=1000, source='twitter'):
        """
        query: eg.   #mdmehrab, mdmehrab AND cube26
        from_time:eg. a datetime object
        apikey,begintime,format,source

        """
        frrole_url = 'http://api.frrole.com/v2/topic-details'
        if not (query and api_key):
            return None

        ''' convert from_time to DD-MM-YYYYTHH:MM:SS '''
        from_time = from_time.strftime('%d-%m-%YT%H:%M:%S')
        params = {'apikey': api_key, 'query': query,
                  'begintime': from_time, 'format': 'json',
                  'source': source, 'count': count}
        data = cls.make_request(frrole_url, params=params)
        results = []
        if data['results'].get('count', 0) > 0:
            for tweet in data['results'].get('tweets', []):
                results.append({
                    'text': tweet.get('text', ''),
                    'username': tweet.get('username', ''),
                    'user_image': tweet.get('user_image', ''),
                    'timestamp': tweet.get('timestamp', ''),
                    'tweet_id': tweet.get('tweet_id', '0'),
                    'retweet_count': tweet.get('retweet_count', 0),
                    'reach': tweet.get('reach', 0)
                })
        return sorted(results, key=lambda tweet: (tweet['tweet_id']),
                      reverse=True)


# tweets[{},{}] : text,username,user_image,timestamp,tweet_id,

# API.user_timeline(id/user_id/screen_name, since_id, count, page)
# consumer_key = 'gShjyajZIeBL4dXJoaVtg1xe9'
# consumer_secret = '0KA5LoHqnLp30jsi63Q7ISYRXdhquYZ5q1cg6DPxix2Nuxd7no'
# access_token ='362336298-SEAFLWKkdjHd1qy29ocjkph9eCEnk5sWW05wB7rl'
# access_token_secret = 'wEu1lbvVEMuxYdYfHpOsJe1fXjcKTCz5KDmZ1h1pkxPFu'
# apikey = '9iOirk8N0jjoup8WzXaF5337de796b7dd'

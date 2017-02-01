import requests


class Cricket(object):
    def __init__(self):
        self.url = 'https://query.yahooapis.com/v1/public/yql'
        self.format = 'json'
        self.diagnostics = "true"

    def _build_param(self, query=None):
        params = {
            'q': query,
            'format': self.format,
            'diagnostics': self.diagnostics,
            'env': "store://0TxIGQMQbObzvU4Apia0V0",
            'callback': ''
        }
        return params

    def get_ongoing_matches(self):
        query = "select mid,series.series_name,mn,place.stadium,mt,place.date" + \
                " from cricket.scorecard.live.summary"
        response = requests.get(self.url, params=self._build_param(query),
                                verify=False)
        if not response.ok:
            return []

        results = []
        matches = response.json()["query"]["results"].get("Scorecard")
        for match in matches:
            results.append({
                "matchid": match["mid"],
                "seriesname": match["series"]["series_name"],
                "matchno": match["mn"],
                "venue": match["Place"]["stadium"],
                "startdate": match["Place"]["date"]
            })
        return results

    def get_upcoming_matches(self):
        query = "select * from cricket.upcoming_matches"
        response = requests.get(self.url, params=self._build_param(query),
                                verify=False)
        if not response.ok:
            return []

        results = []
        matches = response.json()["query"]["results"].get("Match")
        for match in matches:
            results.append({
                "matchid": match.get("matchid"),
                "seriesname": match.get("series_name"),
                "matchno": match.get("MatchNo"),
                "venue": (match.get("Venue").get("content")
                          if match.get("Venue") else ''),
                "startdate": match.get("date_match_start")
            })
        return results

    def get_lastball_info(self, matchid):
        query = "select * from  cricket.commentary where match_id={0}"
        query = query.format(matchid)
        response = requests.get(self.url, params=self._build_param(query),
                                verify=False)
        if not response.ok:
            return {}

        overs = response.json()["query"]["results"].get("Over")
        # If there is only 1 over bowled, we get a dict, else a list of dict,
        # hence diffrentiating between a list or a dict.
        last_over = overs if isinstance(overs, dict) else overs[0]
        over_num = last_over.get('num')
        last_ball = (last_over["Ball"]
                     if isinstance(last_over.get("Ball"), dict)
                     else last_over.get("Ball")[0])
        ball_type = last_ball['type']
        # If the response is of type 'commentary' or 'ball'
        if ball_type == 'nonball':
            return {}

        ball = last_ball["n"]
        run = last_ball["r"]
        wkt = True if last_ball["wF"] == "1" else False

        return {
            "over_num": over_num,
            "ball": ball,
            "run": run,
            "wicket": wkt
        }

c = Cricket()
print c.get_ongoing_matches()

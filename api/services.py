import json, requests


def get_market_rate(part):
    response = requests.post('https://mosapi.sinewave.co.in/stocks/', json={'tickers': part})
    string = response.json()
    json_res = json.loads(string)
    if len(json_res) > 0:
        data = json_res[0]
        return data
    else:
        return None

from flask import Flask, jsonify
import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

app = Flask(__name__)


def get_price(code='USD'):
    try:
        url = "https://data-asg.goldprice.org/dbXRates/{}".format(code)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if response.status_code >= 400 and response.status_code < 500:
            return error_message, response.status_code  # Client-side error
        elif response.status_code >= 500:
            return error_message, response.status_code  # Server-side error
        else:
            return "Unknown error occurred.", 500 # Default error response

    try:
        json_data = json.loads(response.content)
        Gold_OZ_Price = json_data['items'][0]['xauPrice']
        Gold_OZ_PrevClose = json_data['items'][0]['xauClose']
        Silver_OZ_Price = json_data['items'][0]['xagPrice']
        Silver_OZ_PrevClose = json_data['items'][0]['xagClose']

        return jsonify(
            {
                'date': json_data['date'],
                'ts': json_data['ts'],
                'code': code,
                'gold': {
                    'price': round(Gold_OZ_Price, 2),
                    'close': round(Gold_OZ_PrevClose, 2)
                },
                'silver': {
                    'price': round(Silver_OZ_Price, 2),
                    'close': round(Silver_OZ_PrevClose, 2)
                }
            })
    except Exception:
        return "Failed on getting live price", 500


@app.route('/', methods=['GET'])
@app.route('/<code>', methods=['GET'])
def get_live_price(code=None):
    if code:
        response = get_price(code)
    else:
        response = get_price()
    if response:
        return response
    else:
        return "Error: Failed to retrieve webpage or response is not successful.", 404


@app.errorhandler(404)
def page_not_found(error):
    return "Page not found. The requested URL was not found on the server.", 404


if __name__ == '__main__':
    app.run()




from flask import Flask, jsonify, Response
import requests
import json
import time

MINUTE = .5
currencies = [
    "USD", "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", "AZN",
    "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", "BRL", "BSD",
    "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", "CNY", "COP", "CRC",
    "CUC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", "EGP", "ERN", "ETB",
    "EUR", "FJD", "FKP", "GBP", "GEL", "GGP", "GHS", "GIP", "GMD", "GNF", "GTQ",
    "GYD", "HKD", "HNL", "HRK", "HTG", "HUF", "IDR", "ILS", "IMP", "INR", "IQD",
    "IRR", "ISK", "JEP", "JMD", "JOD", "JPY", "KES", "KGS", "KHR", "KMF", "KPW",
    "KRW", "KWD", "KYD", "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD",
    "MDL", "MGA", "MKD", "MMK", "MNT", "MOP", "MRO", "MUR", "MVR", "MWK", "MXN",
    "MYR", "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN",
    "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", "SAR",
    "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLL", "SOS", "SRD", "STD", "SVC",
    "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", "TRY", "TTD", "TWD", "TZS",
    "UAH", "UGX", "USD", "UYU", "UZS", "VEF", "VND", "VUV", "WST", "XAF", "XCD",
    "XOF", "XPF", "YER", "ZAR", "ZMW"
]

currency_dict = {currency: True for currency in currencies}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

app = Flask(__name__)

gdata = {}


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
        gdata[code] = json.loads(response.content)
        return make_data(code, gdata[code])
    except Exception:
        return "Failed on getting live price", 500


def make_data(code, json_data):
    Gold_OZ_Price = json_data['items'][0]['xauPrice']
    Gold_OZ_PrevClose = json_data['items'][0]['xauClose']
    Silver_OZ_Price = json_data['items'][0]['xagPrice']
    Silver_OZ_PrevClose = json_data['items'][0]['xagClose']

    Gold_Gram_Price = Gold_OZ_Price / 31.1035
    Gold_Gram_PrevClose = Gold_OZ_PrevClose / 31.1035

    Gold_KG_Price = Gold_Gram_Price * 1000
    Gold_KG_PrevClose = Gold_Gram_PrevClose * 1000

    Silver_KG_Price = Silver_OZ_Price * 32.15
    Silver_KG_PrevClose = Silver_OZ_PrevClose * 32.15


    return jsonify(
        {
            'date': json_data['date'],
            'ts': json_data['ts'],
            'code': code,
            'gold': {
                "oz": {
                    'price': round(Gold_OZ_Price, 2),
                    'close': round(Gold_OZ_PrevClose, 2)
                },
                "gram": {
                    'price': round(Gold_Gram_Price, 2),
                    'close': round(Gold_Gram_PrevClose, 2)
                },
                "kg": {
                    'price': round(Gold_KG_Price, 2),
                    'close': round(Gold_KG_PrevClose, 2)
                }
            },
            'silver': {
                "oz": {
                    'price': round(Silver_OZ_Price, 2),
                    'close': round(Silver_OZ_PrevClose, 2)
                },
                "kg": {
                    'price': round(Silver_KG_Price, 2),
                    'close': round(Silver_KG_PrevClose, 2)
                }
            }
        })


def get_cached_data(code='USD'):
    if code in gdata:
        return gdata[code]
    return None


@app.route('/', methods=['GET'])
@app.route('/<code>', methods=['GET'])
def get_live_price(code=None):
    response = None
    current_time = int(time.time() * 1000)
    if code is None:
        code = 'USD'

    if code not in currency_dict:
        return "Error: currency code not supported.", 404

    data = get_cached_data(code)
    if data:
        diff_time = current_time - data['ts']
        if diff_time < (60000 * MINUTE):  # convert to min
            print("On Cache")
            response = make_data(code, gdata[code])

    if response is None:
        print("On Internet")
        response = get_price(code)

    # for key, value in gdata.items():
    #    print(key, ':', value)
    if response:
        return response

    return "Error: Failed to retrieve webpage or response is not successful.", 404


@app.route('/favicon.ico')
def favicon():
    return Response(status=204)


@app.errorhandler(404)
def page_not_found(error):
    return "Page not found. The requested URL was not found on the server.", 404


if __name__ == '__main__':
    app.run()

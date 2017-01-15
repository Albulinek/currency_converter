import sys
import argparse
import urllib.request, json
import symbols
import ast
import doctest


def currency_converter(args):
    """Return currency exchange rate"""
    args_ = parse_args(args)
    if args_.amount is not None and args_.amount > 0:
        amount = args_.amount
    elif args_.amount is None:
        print('ERROR: You forgot to set the amount of currency. Course will be evaluated for 1 unit of currency')
        amount = 1
    else:
        print('ERROR: You set wrong amount of currency')
        return None

    if args_.input_currency is not None:
        try:
            input_currency = symbols.currency_symbols_conversion(args_.input_currency)
        except symbols.CurrencyNotFoundError as e:
            print(e)
            return None
        except symbols.DuplicateCurrencyError as e:
            print(e)
            return None
    else:
        return print('ERROR: You forgot to set the converted currency')

    if args_.output_currency is not None:
        try:
            output_currency = symbols.currency_symbols_conversion(args_.output_currency)
        except symbols.CurrencyNotFoundError as e:
            print(e)
            return None
        except symbols.DuplicateCurrencyError as e:
            print(str(e))
            return None
    else:
        output_currency = None

    # We are going to use free converter api at http://free.currencyconverterapi.com/ and http://fixer.io/
    if output_currency is not None:
        url = 'http://free.currencyconverterapi.com/api/v3/convert?q=' + input_currency + '_' + output_currency + '&compact=ultra'
        return convert_with_out(url, input_currency, output_currency, amount)
    else:
        url = 'http://api.fixer.io/latest?base=' + input_currency
        return convert_without_out(url, input_currency, amount)


def parse_args(args):
    parser = argparse.ArgumentParser(description='Convert currency exchange rate')
    parser.add_argument('--amount', nargs=None, type=float, help='Amount currency for exchange')
    parser.add_argument('--input_currency', nargs=None, type=str,
                        help='Input currency (3 letter name or currency symbol)')
    parser.add_argument('--output_currency', nargs=None, type=str,
                        help='Output currency (3 letter name or currency symbol)')
    return parser.parse_args(args)


def convert_with_out(url, input_currency, output_currency, amount):
    try:
        r = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print('ERROR: Currency data for ' + input_currency + ' are not available\n' + str(e))
        return None
    except urllib.error.URLError as e:
        print('ERROR: Cant establish connection to server\n' + str(e))
        return None
    response = r.read().decode('utf-8')
    resp_dict = ast.literal_eval(response)
    rate = resp_dict[input_currency + '_' + output_currency]
    data = {'input': {'amount': amount, 'currency': input_currency}, 'output': {}}
    data['output'][output_currency] = round(float(rate) * amount, 2)
    json_data = json.dumps(data, sort_keys=True)
    return json_data


def convert_without_out(url, input_currency, amount):
    try:
        r = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print('ERROR: Currency data for ' + input_currency + ' are not available\n' + str(e))
        return None
    except urllib.error.URLError as e:
        print('ERROR: Can\'t establish connection to server\n' + str(e))
        return None
    resp_dict = ast.literal_eval(r.read().decode('utf-8'))
    rate = resp_dict['rates']
    data = {'input': {'amount': amount, 'currency': input_currency}, 'output': {}}
    for i in rate:
        data['output'][i] = round(float(rate[i]) * amount, 2)
    json_data = json.dumps(data, sort_keys=True)
    return json_data


if __name__ == '__main__':
    data = currency_converter(sys.argv[1:])
    print(data)

import requests
import json


def main(headers, params):
    session = requests.Session()

    session.post('https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/session/start',
                 headers=headers)

    response = session.get('https://api.pdok.nl/bzk/locatieserver/search/v3_1/suggest', params=params, headers=headers)
    json_file = json.loads(response.text)

    # An address_id is needed for the next request which provides the nummeraanduiding_id, address_ids are paired with addresses in this case 'De Boelelaan 1105'
    address_id = json_file['response']['docs'][0]['id']

    response_with_nummeraanduiding_id = session.get(
        f'https://api.pdok.nl/bzk/locatieserver/search/v3_1/lookup?fl=*&id={address_id}',
        headers=headers,
    )

    # print(response_with_nummeraanduiding_id.text)

    # A 'nummeraanduiding id' is needed to retrieve the woz values
    nummeraanduiding_id = json.loads(response_with_nummeraanduiding_id.text)['response']['docs'][0][
        'nummeraanduiding_id']
    identifier = json.loads(response_with_nummeraanduiding_id.text)['response']['docs'][0]['identificatie'].split('-')[
        0]

    response_with_woz_values = session.get(
        f'https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{nummeraanduiding_id}',
        headers=headers,
    )

    woz_waarde_json = json.loads(response_with_woz_values.text)
    # print(response_with_woz_values.text)

    try:
        woz_values_over_years = woz_waarde_json['wozWaarden']
        print(f"woz-waarde for {address} are {woz_values_over_years}")
    except KeyError:
        woz_values_over_years = None
        print(f"There is no woz-waarde available: {woz_values_over_years}")
        if identifier != nummeraanduiding_id:
            # Sometimes a 'building' has multiple identifiers such as 0363200000078860-0363010000841495, since it takes multiple positions on the map
            print('Trying the identifier')
            response = session.get(
                f'https://www.wozwaardeloket.nl/wozwaardeloket-api/v1/wozwaarde/nummeraanduiding/{identifier}',
                headers=headers,
            )
            print(response.text)
            # Not sure whether it is actually possible.


if __name__ == '__main__':
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Origin': 'https://www.wozwaardeloket.nl',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    sample_address = 'De Boelelaan 1105, 1081 HV Amsterdam'
    number_of_years = 10

    params = {
        'q': sample_address,
        'rows': number_of_years,
    }
    main(headers, params)

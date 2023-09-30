import re
import requests
import json
import pathlib
from datetime import datetime
from bs4 import BeautifulSoup

from .. import output, request, units


class ColesScraper:

    def __init__(self, store_id, quick=False):
        self.quick = quick
        self.store_id = store_id

        self.session = request.get_base_session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'Origin': 'https://www.coles.com.au',
            'Referer': 'https://www.coles.com.au',
        }
        self.start()

    def start(self):
        # Need to get the subscription key
        response = self.session.get('https://www.coles.com.au')
        response.raise_for_status()
        html = BeautifulSoup(response.text, features="html.parser")
        next_data_script = html.find("script", id="__NEXT_DATA__")
        next_data_json = json.loads(next_data_script.string)
        self.api_key = next_data_json['runtimeConfig']['BFF_API_SUBSCRIPTION_KEY']
        self.session.headers['ocp-apim-subscription-key'] = self.api_key

    def get_category(self, cat_slug):
        params = {
            'slug': cat_slug,
            'page': 1,
        }
        product_count = 0
        while True:
            print(f'Page {params["page"]}')
            response = self.session.get(f'https://www.coles.com.au/_next/data/20230922.01_v3.52.0/en/browse/{cat_slug}.json', params=params)
            try:
                response.raise_for_status()
            except requests.HTTPError:
                print(response.text)
                raise
            response_data = response.json()
            search_results = response_data['pageProps']['searchResults']
            for result in search_results['results']:
                yield result

            # Next page calculation
            total_products = search_results['noOfResults']
            product_count += len(search_results['results'])
            if product_count >= total_products:
                # We're done
                break

            # Temporary speedup
            if self.quick:
                break

            # Not done, go to next page
            params['page'] += 1

    def get_categories(self):
        response = self.session.get(f'https://www.coles.com.au/api/bff/products/categories?storeId={self.store_id}')
        response.raise_for_status()
        category_data = response.json()
        categories = category_data['catalogGroupView']
        return categories

def get_canonical(item, today):
    if item['_type'] == 'SINGLE_TILE' and item.get('adId'):
        # Ad tile, not a product
        return None

    if item['pricing'] is None:
        # No pricing information, can't process
        return None

    quantity, unit = get_quantity_and_unit(item)

    result = {
        'id': item['id'],
        'name': item['name'],
        'description': item['description'],
        'price': item['pricing']['now'],
        'priceHistory': [{
            'date': today,
            'price': item['pricing']['now'],
        }],
        'isWeighted': item['pricing']['unit'].get('isWeighted', False),
        'unit': unit,
        'quantity': quantity,
        # 'organic': 
    }
    result = units.convert_unit(result)
    return result


def get_quantity_and_unit(item):
    # Try to get unit information from pricing data first
    unit_data = item['pricing']['unit']
    quantity = unit_data['quantity']
    if 'ofMeasureUnits' in unit_data:
        unit = unit_data['ofMeasureUnits']
    else:
        size = item['size']
        if not size:
            # Maybe the description can be parsed as size
            size = item['description']
        parsed_quantity, unit = parse_str_unit(size)
        # A quantity of 0 or 1 indicates that the information is elsewhere
        if parsed_quantity != quantity and quantity > 1:
            raise RuntimeError(f"Quantity '{quantity} does not matched parsed quantity '{parsed_quantity}")
        # If quantity is 1 and we parsed a different value then that's the right value
        # (e.g. 1 (quantity) packet of 38g (parsed_quantity))
        quantity = parsed_quantity

    return quantity, unit


def parse_str_unit(size):
    # Try coles-special methods before going to the generic function
    size = size.lower()
    matched = re.match(r'^.*can (?P<quantity>[0-9]+)(?P<unit>[a-z]+):pack(?P<count>[0-9]+)', size)
    if matched:
        quantity = float(matched.group('quantity'))
        unit = matched.group('unit')
        count = float(matched.group('count'))
        quantity *= count
        return quantity, unit
    else:
        return units.parse_str_unit(size)


def main(quick):
    coles = ColesScraper(store_id='0584', quick=quick)
    categories = coles.get_categories()
    #categories = load_cache()
    for category_obj in categories:
        cat_slug = category_obj['seoToken']
        
        if cat_slug in ['down-down', 'back-to-school']:
            # Skip for now, expect duplicate products
            continue

        if 'Products' in category_obj:
            # Already cached
            continue

        cat_desc = category_obj['name']
        print(f'Fetching category {cat_slug} ({cat_desc})')
        category = coles.get_category(cat_slug)
        all_category_bundles = list(category)
        category_obj['Products'] = all_category_bundles

        if quick:
            break
        #save_cache(categories)
    output.save_data('coles', categories)
    #print(json.dumps(category, indent=4))


if __name__ == '__main__':
    main()
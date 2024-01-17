from hotprices_au.sites import woolies

def get_item(**kwargs):
    defaults = {
        'Stockcode': '1',
        'Name': 'test',
        'Description': 'test desc',
        'IsInStock': True,
        'Price': None,
        'PackageSize': None,
        'CupPrice': None,
        'CupMeasure': None,
        'WasPrice': None,
    }

    if 'CupMeasure' in kwargs:
        defaults.update({
            'CupPrice': 10,
        })

    if 'PackageSize' in kwargs:
        defaults.update({
            'Price': 10,
            'WasPrice': 10,
        })
    defaults.update(kwargs)

    products = {'Products': [defaults]}
    return products

def test_get_canonical():
    today = '2023-09-29'
    item = get_item(CupMeasure='1KG')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 1000

    item = get_item(CupMeasure='335G')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 335

    item = get_item(PackageSize='10EA')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 10

    item = get_item(PackageSize='Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 1

    item = get_item(PackageSize='2 Pack')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 2

    item = get_item(CupMeasure='Per Kg')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 1000

    item = get_item(CupMeasure='PER KG')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 1000

    item = get_item(CupMeasure='125G Punnet')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 125

    item = get_item(CupMeasure='100G Pack')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 100

    item = get_item(PackageSize='Whole Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 1

    item = get_item(PackageSize='Half Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 0.5

    item = get_item(CupMeasure='1L')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 1000

    item = get_item(CupMeasure='150m')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'cm'
    assert can_item['quantity'] == 15000

    item = get_item(PackageSize='30x375mL Case')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 11250

    item = get_item(PackageSize='375mL x10 Carton')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 3750

    item = get_item(PackageSize='440ml x 24 Case')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 10560

    item = get_item(PackageSize='355ml x6 Pack')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 2130

    item = get_item(PackageSize='4x4x375mL')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 6000

    item = get_item(PackageSize='0.8g')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 0.8

    item = get_item(PackageSize='355ml xCase')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 8520

    item = get_item(PackageSize='800mL Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 800

    item = get_item(PackageSize='', Unit='Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 1

    item = get_item(Stockcode=532887, PackageSize='700Mm', Name='Kahlua White Russian')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 700

    item = get_item(Stockcode=985323, PackageSize='200Nl x4 Pack', Name='Nelson County Bourbon & Cola')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 800

    item = get_item(PackageSize='90 Tablets', Unit='Each')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ea'
    assert can_item['quantity'] == 90

    item = get_item(PackageSize='180g', Unit='Each', CupMeasure='100G')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'g'
    assert can_item['quantity'] == 180

    item = get_item(PackageSize='375ml x 24 Case', Unit='Each', Price=None, IsInStock=False)
    assert item['Products'][0]['WasPrice']
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 9000

    item = get_item(PackageSize='200ml X Pack')
    can_item = woolies.get_canonical(item, today)
    assert can_item['unit'] == 'ml'
    assert can_item['quantity'] == 200


if __name__ == '__main__':
    test_get_canonical()
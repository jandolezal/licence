import csv
import pathlib
from typing import List

import dataclasses

from licenses import parse

from licenses.parse import Licence, VykonLicence, VykonProvozovna, Provozovna


def read_lic_ids(business: str) -> List[str]:
    csv_path = pathlib.Path(f'csvs/holders/{business}/holders.csv')
    with open(csv_path) as csvf:
        reader = csv.DictReader(csvf)
        return [row['id'] for row in reader]


def get_data(business: str, lic_ids: List, url: str, start: int, end: int):

    lic_list = []

    for lic_id in lic_ids[start:end]:
        params = {'lic-id': lic_id}
        parsed_lic = parse.parse_page(business, lic_id, parse.request_soup(url, params=params))
        lic_list.append(parsed_lic)

    return lic_list


def main():

    business_map = {
        'electricity': 'výroba elektřiny',
        'electricity-dist': 'distribuce elektřiny',
        'electricity-trade': 'obchod s elektřinou',
        'heat': 'výroba tepelné energie',
        'heat-dist': 'rozvod tepelné energie',
        'gas': 'výroba plynu',
        'gas-dist': 'distribuce plynu',
        'gas-trade': 'obchod s plynem',
    }

    business = 'electricity'

    lic_ids = read_lic_ids(business)
    URL = 'http://licence.eru.cz/detail.php'

    parsed_licenses = get_data(business_map[business], lic_ids, URL, start=2000, end=2010)

    output_dir = pathlib.Path(f'csvs/licenses/{business}')
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / 'capacity.csv', 'w') as csvf:
        fieldnames = [field.name for field in dataclasses.fields(VykonLicence)]
        writer = csv.DictWriter(csvf, fieldnames=fieldnames)
        writer.writeheader()
        for lic in parsed_licenses:
            for vykon in lic.vykony:
                writer.writerow(dataclasses.asdict(vykon))

if __name__ == '__main__':
    main()

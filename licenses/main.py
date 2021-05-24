#!/usr/bin/env python3

from configparser import Error
import csv
import pathlib
from typing import List
import argparse


from licenses.config import conf
from licenses import parse


def read_lic_ids(business: str) -> List[str]:
    csv_path = pathlib.Path(f'csvs/holders/{business}/holders.csv')
    with open(csv_path) as csvf:
        reader = csv.DictReader(csvf)
        return [row['id'] for row in reader]


def read_lic_count(business: str) -> int:
    csv_path = pathlib.Path(f'csvs/holders/{business}/holders.csv')

    with open(csv_path) as csvf:
        reader = csv.DictReader(csvf)
        return len(list(reader)) - 1  # Subtract header


def get_data(business: str, lic_ids: List, url: str, start: int, end: int):

    count = 0

    lic_list = []

    for lic_id in lic_ids[start:end]:
        params = {'lic-id': lic_id}
        try:
            soup = parse.request_soup(url, params=params)
            parsed_lic = parse.parse_page(business, lic_id, soup)
        except Error as e:
            print(e)
            print(f'Error occured when parsing id {lic_id}')
            print(f'for {business} at index {lic_ids.index(lic_id)}')
            raise SystemExit

        lic_list.append(parsed_lic)

        count += 1
        if count % 500 == 0:
            print(f'Parsed {count} licenses')

    return lic_list


def get_parser():
    parser = argparse.ArgumentParser(
        prog='licenses',
        description='Retrieves data from licences',
    )

    # Options
    parser.add_argument(
        '--dev',
        action='store_true',
        default=False,
        help='use downloaded html file in samples dir (default: False)'
    )

    parser.add_argument(
        '--csv',
        action='store_true',
        default=True,
        help='export parsed data to csv (default: True)'
    )

    parser.add_argument(
        '--business',
        action='store',
        choices=['electricity', 'heat'],
        default='electricity',
        help='select business type (default: electricity)'
    )

    parser.add_argument(
        '--count',
        action='store_true',
        help='return number of licenses(default: False)'
    )

    parser.add_argument(
        '--start',
        default=0,
        type=int,
        help='specify start index for parsing license ids (default: 0)'
    )

    parser.add_argument(
        '--end',
        default=None,
        type=int,
        help='specify end index for parsing license ids (default: None)'
    )

    return parser


def main():

    # Mapping from names used in the directory tree
    business_map = {
        'electricity': 'výroba elektřiny',
        'heat': 'výroba tepelné energie',
    }

    args = vars(get_parser().parse_args())

    business = args['business']

    # Case when exploring number of licenses before requesting data
    if args['count']:
        count = read_lic_count(business)
        print(f'{count} licenses for {business}')
        raise SystemExit

    # Useful when requesting in batches
    start = args['start']
    end = args['end']

    # First read license numbers for particular business
    lic_ids = read_lic_ids(business)
    url = conf.get('licenses', 'url')

    # Use these numbers to request data for this license
    parsed_licenses = get_data(
        business_map[business],
        lic_ids,
        url,
        start=start,
        end=end
        )

    if args['csv']:
        for lic in parsed_licenses:
            lic.export_to_csv(business, facilities=True, capacities=True)


if __name__ == '__main__':
    main()

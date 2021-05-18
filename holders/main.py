#!/usr/bin/env python3

"""Find and extract data about licence holders (držitelé licencí)
from Energy Regulatory Office website for selected business type,
e.g. for electricity or heat production.
"""

import argparse
import dataclasses
import pathlib
import xml.etree.ElementTree as ET
from typing import Optional, List, Union
from dataclasses import dataclass, fields
from datetime import date
import csv
import configparser

import requests
from bs4 import BeautifulSoup

from holders.config import conf


@dataclass
class Holder:
    """
    Represents a holder of a licence (držitel licence).
    id is a licence number (číslo licence)
    """

    id: str
    version: int
    status: str
    ic: str
    nazev: str
    cislo_dom: str
    cislo_or: str
    ulice: str
    obec: str
    obec_cast: str
    psc: str
    okres: str
    kraj: str
    zeme: str
    den_opravneni: date
    den_zahajeni: date
    den_zaniku: date
    den_nabyti: date
    osoba: str


def remove_fluff(x: str) -> Optional[str]:
    if '-----' not in x:
        return x
    return None


def convert_date(x: str) -> Optional[date]:
    if x:
        return date.fromisoformat(x)    
    return None


translation = {
    'cislo_licence': ('id', lambda x: x),
    'version': ('version', lambda x: int(x) if x else None),
    'version_status': ('status', remove_fluff),
    'subjekt_IC': ('ic', remove_fluff),
    'subjekt_nazev': ('nazev', remove_fluff),
    'subjekt_cislo_dom': ('cislo_dom', remove_fluff),
    'subjekt_cislo_or': ('cislo_or', remove_fluff),
    'subjekt_ulice_nazev': ('ulice', remove_fluff),
    'subjekt_obec_cast': ('obec_cast', remove_fluff),
    'subjekt_obec_nazev': ('obec', remove_fluff),
    'subjekt_PSC': ('psc', remove_fluff),
    'subjekt_okres': ('okres', remove_fluff),
    'subjekt_kraj': ('kraj', remove_fluff),
    'subjekt_zeme': ('zeme', remove_fluff),
    'subjekt_den_opravneni': ('den_opravneni', convert_date),
    'subjekt_den_zahajeni': ('den_zahajeni', convert_date),
    'subjekt_den_zaniku': ('den_zaniku', convert_date),
    'subjekt_den_nabyti_pravni_moci': ('den_nabyti', convert_date),
    'odpovedny_zast': ('osoba', lambda x: x if x else None),
}


def request_data(url, **kwargs):
    try:
        r = requests.get(url, **kwargs)
        return r
    except requests.RequestException as e:
        raise SystemExit(e)


def get_xml(url: str, business: str, **kwargs) -> requests.models.Response:
    """Find and return xml from the website for particular business type.

    Args:
        url (str) : Endpoint for licence holders (držitelé licencí) datasets
        business (str) : e.g. 'výroba elektřiny' or 'výroba tepelné energie'
    
    Returns:
        requests.models.Reponse
    """
    r = request_data(url, **kwargs)
    bs = BeautifulSoup(r.content, 'html.parser')
    xml_url = bs.find("a", text=business).attrs['href']
    xml_url = "https://www.eru.cz" + xml_url
    print(f'XML file is at: {xml_url}')

    r = request_data(xml_url, **kwargs)

    return r


def parse_xml(xml: Union[requests.models.Response, pathlib.Path]) -> List[Holder]:
    """Parse xml to a list of Holders.
    """
    if isinstance(xml, pathlib.Path):
        try:
            tree = ET.parse(xml)
            root = tree.getroot()
        except FileNotFoundError:
            print('download xml files to samples directory with --dev option. see config.ini [samples]')
            raise SystemExit
    else:
        root = ET.fromstring(xml.text)
    
    holders = []

    for child in root:
        original = child.attrib

        holder = Holder(
            **{new_key: func(original[orig_key]) for orig_key, (new_key, func) in translation.items()}
        )

        holders.append(holder)

    print(f"Parsed {len(holders)} licence holders")
    return holders


def get_parser():
    parser = argparse.ArgumentParser(
        prog='holders',
        description='Retrieves data about licence holders from Energy Regulatory Office',
    )

    # Options
    parser.add_argument(
        '--dev',
        action='store_true',
        default=False,
        help='use testig xml file from samples directory (default: False)'
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
        choices=[
            'electricity', 'electricity-dist', 'electricity-trade',
            'heat', 'heat-dist', 'gas', 'gas-dist', 'gas-trade',
            ],
        default='electricity',
        help='select business type: e.g. electricity or heat (default: electricity)'
    )    

    parser.add_argument(
        '--output',
        metavar='FILENAME',
        action='store',
        default='holders.csv',
        help='specify csv output filename (default: holders.csv)'
    ) 

    return parser


def main() -> None:

    parser = get_parser()
    args = vars(parser.parse_args())

    business = args['business']

    # Map to strings used on the website to find a correct xml file
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
    
    # Request data from the website or
    # prevent request to the website when developing the app
    # and use sample xml files manually downloaded from the website
    # to directory samples. See config.ini [samples]
    if args['dev']:
        try:
            xml = pathlib.Path('samples') / conf.get('samples', business)
        except configparser.NoOptionError as e:
            print(f'{e}. download sample xml for electricity or heat. see config.ini [samples]')
            raise SystemExit
    else:
        url = conf.get('holders', 'url')
        headers = {'User-Agent': conf.get('headers', 'user_agent')}
        xml = get_xml(url=url, business=business_map[business],
                headers=headers, timeout=3)
    
    # Parse xml data
    holders = parse_xml(xml)
    
    # Save parsed data as csv file in csvs directory
    if args['csv']:
        csv_filename = args['output']

        output_dir = pathlib.Path(f'csvs/holders/{business}')
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / csv_filename, 'w') as csvf:
            fieldnames = [field.name for field in dataclasses.fields(Holder)]
            writer = csv.DictWriter(csvf, fieldnames=fieldnames)
            writer.writeheader()
            for holder in holders:
                writer.writerow(dataclasses.asdict(holder))
    
    # TODO: Save data to database


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

"""Funkce pro parsování stránky s licencí.

Data jsou na stránce v html tabulkách.

Jedna licence má celkové výkony za licenci, jednu a více provozoven,
z nichž ke každé provozovně je pár údajů jako název nebo okres
a opět seznam výkonů.

Některé části mohou náhodně scházet.
HTML není konzistentní, např. <th> a <td>, identifikace <table>
jednou jako id, jindy jako class.
"""

import unicodedata
from dataclasses import dataclass, field, fields, asdict
import pathlib
from typing import List
import csv


import bs4
import requests
from bs4 import BeautifulSoup

from licenses import address
from licenses.config import conf


@dataclass
class VykonProvozovna:

    provozovna_id: int
    lic_id: str
    druh: str
    technologie: str
    mw: float


@dataclass
class VykonLicence:

    lic_id: str
    druh: str
    technologie: str
    mw: float


@dataclass
class Provozovna:

    id: int
    lic_id: str
    nazev: str
    ulice: str
    cp: str
    psc: str
    obec: str
    okres: str
    kraj: str
    pocet_zdroju: int = None
    katastralni_uzemi: str = None
    kod_katastru: str = None
    vymezeni: str = None
    vykony: List[VykonProvozovna] = field(default_factory=list)

    def add_capacity(self, capacity):
        self.vykony.append(capacity)

    def export_to_csv(self, business, output_dir='csvs'):
        # Metadata for the facility
        fac_dir = pathlib.Path(f'{output_dir}/licenses/{business}')

        if (fac_dir / 'facilities.csv').exists():
            header = False
        else:
            header = True

        fac_dir.mkdir(parents=True, exist_ok=True)
        with open(fac_dir / 'facilities.csv', 'a') as csvf:
            fieldnames = [
                field.name for field in fields(Provozovna)
                if not field.default_factory == list
                ]
            writer = csv.DictWriter(csvf, fieldnames=fieldnames)
            if header:
                writer.writeheader()

            export_dict = asdict(self)
            export_dict.pop('vykony')  # Remove list
            writer.writerow(export_dict)

        # Capacities for the facility
        cap_dir = pathlib.Path(f'{output_dir}/licenses/{business}')

        if (cap_dir / 'facilities_capacities.csv').exists():
            header = False
        else:
            header = True

        cap_dir.mkdir(parents=True, exist_ok=True)
        with open(cap_dir / 'facilities_capacities.csv', 'a') as csvf2:
            fieldnames = [
                field.name for field in fields(VykonProvozovna)
                if not field.default_factory == list
                ]
            writer = csv.DictWriter(csvf2, fieldnames=fieldnames)
            if header:
                writer.writeheader()
            for cap in self.vykony:
                export_dict = asdict(cap)
                writer.writerow(export_dict)


@dataclass
class Licence:

    id: str
    predmet: str
    pocet_zdroju: int = None
    provozovny: List[Provozovna] = field(default_factory=list)
    vykony: List[VykonLicence] = field(default_factory=list)

    def add_facility(self, facility):
        self.provozovny.append(facility)

    def add_capacity(self, capacity):
        self.vykony.append(capacity)

    def export_to_csv(self, business, output_dir='csvs'):

        lic_dir = pathlib.Path(f'{output_dir}/licenses/{business}')

        if lic_dir.exists():
            header = False
        else:
            header = True

        lic_dir.mkdir(parents=True, exist_ok=True)

        # Few metadata for license
        with open(lic_dir / 'licenses.csv', 'a') as csvf:
            fieldnames = [
                field.name for field in fields(Licence)
                if not field.default_factory == list
                ]
            writer = csv.DictWriter(csvf, fieldnames=fieldnames)
            if header:
                writer.writeheader()
            export_dict = asdict(self)
            export_dict.pop('vykony')  # Remove lists
            export_dict.pop('provozovny')
            writer.writerow(export_dict)

        # Export facilities
        for prov in self.provozovny:
            prov.export_to_csv(business, output_dir)

        # Capacities only for the license itself
        cap_dir = pathlib.Path(f'{output_dir}/licenses/{business}')
        cap_dir.mkdir(parents=True, exist_ok=True)

        with open(cap_dir / 'capacities.csv', 'a') as csvf:
            fieldnames = [
                field.name for field in fields(VykonLicence)
                if not field.default_factory == list
                ]
            writer = csv.DictWriter(csvf, fieldnames=fieldnames)
            if header:
                writer.writeheader()
            for cap in self.vykony:
                export_dict = asdict(cap)
                writer.writerow(export_dict)


def request_soup(url: str, count: int, params: dict) -> bs4.BeautifulSoup:
    """Request page and retur BeautifulSoup from its text
    """
    headers = {'User-Agent': conf.get('headers', 'user_agent')}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=3)
    except requests.exceptions.RequestException:
        print(f'Request failed handling license # {count}')
        print(f'License URL: {url}')
        raise SystemExit
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')


def parse_capacity(table: bs4.BeautifulSoup) -> dict:
    """Parse table with data about installed capacity.
    """
    d = {}
    for row in table.find_all('tr')[2:]:  # První dva řádky nemají hodnoty
        # k = prepare_key(row.find('th').get_text())
        k = row.find('th').get_text().strip('\n\t')

        # num_columns = len(row.find_all('td'))
        num_columns = len(row.find_all(['th', 'td']))

        if num_columns == 3:
            vykony = row.find_all(['th', 'td'])
            el = vykony[-2].get_text(strip=True).replace(' ', '')
            tep = vykony[-1].get_text(strip=True).replace(' ', '')
            d[(k, 'Elektrický')] = float(el) if el else None
            d[(k, 'Tepelný')] = float(tep) if tep else None
        else:
            # Case when data in the row are not capacities
            # Počet zdrojů, Tok or Říční km
            v = row.find('td')
            d[k] = v.get_text(strip=True)
    return d


def parse_facility_header(tabulka: bs4.element.Tag) -> dict:
    """Parse metadata about facility from html table.
    """
    d = {}

    rows = tabulka.find_all('tr')
    divs = rows[0].find_all('div')
    d['id'] = int(divs[0].get_text(strip=True).strip('Evidenční číslo: '))
    d['nazev'] = divs[1].get_text(strip=True)

    soucasti_adresy = ('psc', 'obec', 'ulice', 'cp', 'okres', 'kraj')
    try:
        adresa = divs[2].get_text(strip=True)
        rozdelena_adresa = address.rozdel_adresu(address.uprav_adresu(adresa))
        for k, v in zip(soucasti_adresy, rozdelena_adresa):
            d[k] = v
    # Adresa schází
    except IndexError:
        d.update({soucast: None for soucast in soucasti_adresy})

    if len(rows) > 2:  # Neschází informace o katastru
        for th, td in zip(rows[1].find_all('th'), rows[2].find_all('td')):
            d[prepare_key(th.get_text(strip=True))] = td.get_text(strip=True)

    return d


def prepare_key(original):
    """Make the variable from the first column more useful.
    """
    normalizovane = unicodedata.normalize('NFD', original)
    nove = normalizovane.encode('ascii', 'ignore').decode('utf-8')
    return nove.strip().lower().replace(' ', '_')


def parse_page(business: str, lic_id: str, bs: bs4.BeautifulSoup) -> Licence:
    """Parse license page.
    """

    lic = Licence(id=lic_id, predmet=business)

    # Rozsah podnikání a technické podmínky
    lic_tez_total_table = (
        bs.find('table', {'class': 'lic-tez-total-table'})
        or
        bs.find('table', {'id': 'lic-tez-total-table'})
        )

    if lic_tez_total_table:  # Zrušené, zaniklé licence nemají výkony
        lic_capacity = parse_capacity(lic_tez_total_table)

        # Zpracuje výkony pro licenci
        for k, v in lic_capacity.items():
            if len(k) == 2 and (isinstance(v, float) and v > 0):
                vykon_lic = VykonLicence(
                    lic_id=lic_id,
                    druh=k[1],
                    technologie=k[0],
                    mw=v
                    )
                lic.add_capacity(vykon_lic)
            if k == 'Počet zdrojů':
                lic.pocet_zdroju = int(v)

    # Seznam jednotlivých provozoven k licenci
    # Údaje o provozovnách
    fac_headers = bs.find_all('table', {'class': 'lic-tez-header-table'})
    # Výkony provozoven
    fac_datas = bs.find_all('table', {'class': 'lic-tez-data-table'})

    for header, data in zip(fac_headers, fac_datas):

        # Zpracování metadat o provozovně
        fac = parse_facility_header(header)

        fac['lic_id'] = lic_id
        facility = Provozovna(**fac)

        # Zpracování výkonů k provozovně
        fac_capacity = parse_capacity(data)

        for k, v in fac_capacity.items():
            if len(k) == 2 and ((isinstance(v, float)) and (v > 0)):
                vykon_fac = VykonProvozovna(
                    provozovna_id=facility.id,
                    lic_id=lic_id,
                    druh=k[1],
                    technologie=k[0],
                    mw=v
                    )
                facility.add_capacity(vykon_fac)
            if k == 'Počet zdrojů':
                facility.pocet_zdroju = int(v)

        lic.add_facility(facility)

    return lic


if __name__ == '__main__':
    plana = pathlib.Path('samples/cenergyplana.html')
    plzen = pathlib.Path('samples/plzen.html')
    oleska = pathlib.Path('samples/oleska.html')

    with open(oleska) as f:
        bs = BeautifulSoup(f, 'html.parser')
    lic = parse_page('110100010', bs)
    print(lic)

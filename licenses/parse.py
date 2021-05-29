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
from pathlib import Path
from typing import List
import csv


import bs4
import requests
from bs4 import BeautifulSoup

from licenses import address
from licenses.config import conf


@dataclass
class Base:

    def to_csv(self, output_dir: Path, filename: str) -> None:
        if (output_dir / filename).exists():
            header = False
        else:
            header = True

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / filename, 'a') as csvf:
            fieldnames = [
                field.name for field in fields(self)
                if not field.default_factory == list
                ]
            writer = csv.DictWriter(
                csvf, fieldnames=fieldnames, extrasaction='ignore',
                )

            if header:
                writer.writeheader()

            writer.writerow(asdict(self))


@dataclass
class VykonProvozovna(Base):

    provozovna_id: int
    lic_id: str
    druh: str
    technologie: str
    mw: float


@dataclass
class VykonLicence(Base):

    lic_id: str
    druh: str
    technologie: str
    mw: float


@dataclass
class Provozovna(Base):

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


@dataclass
class Licence(Base):

    id: str
    predmet: str
    pocet_zdroju: int = None
    provozovny: List[Provozovna] = field(default_factory=list)
    vykony: List[VykonLicence] = field(default_factory=list)

    def add_facility(self, facility):
        self.provozovny.append(facility)

    def add_capacity(self, capacity):
        self.vykony.append(capacity)

    def to_csv(self, output_dir: Path, filename: str = 'licenses.csv') -> None:
        super().to_csv(output_dir, filename)

        for cap in self.vykony:
            cap.to_csv(output_dir, 'capacities.csv')

        for fac in self.provozovny:
            fac.to_csv(output_dir, 'facilities.csv')
            for fac_cap in fac.vykony:
                fac_cap.to_csv(output_dir, 'facilities_capacities.csv')


def request_soup(url: str, count: int, params: dict) -> bs4.BeautifulSoup:
    """Request page and retur BeautifulSoup from its text
    """
    headers = {'User-Agent': conf.get('headers', 'user_agent')}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=3)
    except requests.exceptions.RequestException as e:
        print(f'Request failed handling license # {count}')
        print(f'License id: {params["lic-id"]}')
        print(e)
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
    plana = Path('samples/cenergyplana.html')
    plzen = Path('samples/plzen.html')
    oleska = Path('samples/oleska.html')

    with open(oleska) as f:
        bs = BeautifulSoup(f, 'html.parser')
    lic = parse_page('110100010', bs)
    print(lic)

#!/usr/bin/env python3

"""Funkce pro parsování stránky s licencí. 

Data jsou na stránce v html tabulkách.

Jedna licence má celkové výkony za licenci, jednu a více provozoven,
z nichž ke každé provozovně je, kromě pár údajů jako je název nebo okres, 
je k dispozici opět seznam výkonů.

Některé části mohou náhodně scházet.
"""

import unicodedata
from dataclasses import dataclass, field
import pathlib
from typing import List


import bs4
import requests
from bs4 import BeautifulSoup

from licenses import address


@dataclass
class VykonProvozovna:
    
    provozovna_id: str
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


def parse_capacity(table: bs4.BeautifulSoup) -> dict:
    """Z BeautifulSoup tabulky slovník s výkony.
    tabulka: bs4.element.Tag
    Vrátí: dict
    """
    d = {}
    for row in table.find_all('tr')[2:]:  # První dva řádky nemají hodnoty
        # k = prepare_key(row.find('th').get_text())
        k = row.find('th').get_text().strip('\n\t')
    
        num_columns = len(row.find_all('td'))

        if num_columns == 2:
            vykony = row.find_all('td')
            el = vykony[0].get_text(strip=True).replace(' ', '')
            tep = vykony[1].get_text(strip=True).replace(' ', '')
            d[(k, 'Elektrický')] = float(el)
            d[(k, 'Tepelný')] = float(tep)
        else:
            v = row.find('td')
            d[k] = v.get_text(strip=True)
    return d


def parse_facility_header(tabulka: bs4.BeautifulSoup) -> dict:
    """Z BeautifulSoup tabulky slovník s identifikací provozovny.
    tabulka: bs4.element.Tag
    Vrátí: Provozovna
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
    normalizovane = unicodedata.normalize('NFD', original)
    nove = normalizovane.encode('ascii', 'ignore').decode('utf-8')
    return nove.strip().lower().replace(' ', '_')


def request_soup(url: str, params: dict) -> bs4.BeautifulSoup:
    """BeautifulSoup z celé stránky
    url: str
    params: dict
    Vrátí: bs4.BeautifulSoup
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0'}
    r = requests.get(url, params=params, headers=headers)
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')


def parse_page(business: str, lic_id: str, bs: bs4.BeautifulSoup) -> Licence:
    """Parse license page.
    """

    lic = Licence(id=lic_id, predmet=business)
    
    # Rozsah podnikání a technické podmínky
    lic_tez_total_table = bs.find('table', {'class': 'lic-tez-total-table'})
    if lic_tez_total_table:  # Zrušené, zaniklé licence nemají výkony
        lic_capacity = parse_capacity(lic_tez_total_table)
    
    # Zpracuje výkony pro licenci
    # Tabulka obsahuje nejen výkony (tři sloupce), tak počet zdrojů (dva sloupce)
    # a vodní tok s km (dva sloupce, zatím nezpracováno)
    for k, v in lic_capacity.items():
        if len(k) == 2 and v > 0:
            vykon_lic = VykonLicence(lic_id=lic_id, druh=k[1], technologie=k[0], mw=v)
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
            if len(k) == 2 and v > 0:
                vykon_fac = VykonProvozovna(provozovna_id=facility.id, druh=k[1], technologie=k[0], mw=v)
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

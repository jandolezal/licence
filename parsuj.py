#!/usr/bin/env python

"""Funkce pro parsování stránky s licencí. Data jsou v html tabulkách.
"""

import unicodedata
import requests
from bs4 import BeautifulSoup
import adresy


def parsuj_vykony(tabulka):
    """Z BeautifulSoup tabulky slovník s výkony.
    tabulka: bs4.element.Tag
    Vrátí: dict
    """
    d = {}
    for row in tabulka.find_all('tr')[2:]:  # První dva řádky nemají hodnoty
        k = uklid_klic(row.find('th').get_text())

        num_columns = len(row.find_all('td'))

        if num_columns == 2:
            vykony = row.find_all('td')
            el = vykony[0].get_text(strip=True).replace(' ', '')
            tep = vykony[1].get_text(strip=True).replace(' ', '')
            d[f'{k}_el'] = el
            d[f'{k}_tep'] = tep
        else:
            v = row.find('td')
            d[k] = v.get_text(strip=True)
    return d


def parsuj_drzitele(tabulka):
    """Z BeautifulSoup tabulky slovník s informací o držiteli licence.
    tabulka: bs4.element.Tag
    Vrátí: dict
    """
    d = {}
    for row in tabulka.find_all('tr'):
        try:
            prom = uklid_klic(row.find('th').get_text(strip=True))
            promenne = ['cislo_licence', 'verze_licence']
            if prom in promenne:
                v = row.find('td').get_text(strip=True)
                d[prom] = v
        except AttributeError:
            continue
    return d


def parsuj_provozovnu(tabulka):
    """Z BeautifulSoup tabulky slovník s identifikací provozovny.
    tabulka: bs4.element.Tag
    Vrátí: dict
    """
    d = {}

    rows = tabulka.find_all('tr')
    divs = rows[0].find_all('div')
    d['ev_cislo'] = divs[0].get_text(strip=True).strip('Evidenční číslo: ')
    d['nazev'] = divs[1].get_text(strip=True)

    soucasti_adresy = ('psc', 'obec', 'ulice', 'cp', 'okres', 'kraj')
    try:
        adresa = divs[2].get_text(strip=True)
        rozdelena_adresa = adresy.rozdel_adresu(adresy.uprav_adresu(adresa))
        for k, v in zip(soucasti_adresy, rozdelena_adresa):
            d[k] = v
    # Adresa schází
    except IndexError:
        d.update({soucast: '' for soucast in soucasti_adresy})

    if len(rows) > 2:  # Neschází informace o katastru
        for th, td in zip(rows[1].find_all('th'), rows[2].find_all('td')):
            d[uklid_klic(th.get_text(strip=True))] = td.get_text(strip=True)

    return d


def uklid_klic(puvodni):
    normalizovane = unicodedata.normalize('NFD', puvodni)
    nove = normalizovane.encode('ascii', 'ignore').decode('utf-8')
    return nove.strip().lower().replace(' ', '_')


def uprav_osobu(osoba):
    nova_osoba = []
    for cast in unicodedata.normalize('NFKC', osoba).split(' '):
        nova_osoba.append(cast.strip())
    return ' '.join(nova_osoba)


def priprav_bs(url, params):
    """BeautifulSoup z celé stránky
    url: str
    params: dict
    Vrátí: bs4.BeautifulSoup
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:80.0) Gecko/20100101 Firefox/80.0'}
    r = requests.get(url, params=params, headers=headers)
    r.encoding = 'utf-8'
    return BeautifulSoup(r.text, 'html.parser')


def parsuj_stranku(bs):
    """Z bs vrátí slovník s informací o celé licenci.
    bs: bs4.BeautifulSoup
    Vrátí: dict
    """
    d = {}
    # Informace o držiteli licence
    lic_header_table = bs.find('table', {'id': 'lic-header-table'})
    d.update(parsuj_drzitele(lic_header_table))

    # Rozsah podnikání a technické podmínky
    lic_tez_total_table = bs.find('table', {'class': 'lic-tez-total-table'})
    if lic_tez_total_table:  # Zrušené, zaniklé nemají výkony
        d.update(parsuj_vykony(lic_tez_total_table))

    # Seznam jednotlivých provozoven k licenci
    headers = bs.find_all('table', {'class': 'lic-tez-header-table'})
    datas = bs.find_all('table', {'class': 'lic-tez-data-table'})

    d['provozovny'] = []

    for header, data in zip(headers, datas):
        provozovna = {}

        # Zpracování identifikace provozoven
        provozovna.update(parsuj_provozovnu(header))

        # Výkony k provozovně
        provozovna.update(parsuj_vykony(data))

        d['provozovny'].append(provozovna)

    return d

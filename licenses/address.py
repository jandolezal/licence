#!/usr/bin/env python

"""Upraví adresu a rozdělí ji na jednotlivé části (psč, obec apod.)
"""

import unicodedata
import re


def uprav_adresu(adresa):
    normalizovana = unicodedata.normalize('NFKC', adresa)
    upravena = []
    for cast in normalizovana.split(','):
        upravena.append(cast.strip())
    return upravena


def rozdel_adresu(adresa):
    psc = adresa[0][:6].rstrip().replace(' ', '')
    obec = adresa[0][6:].strip()

    ulice_cp = adresa[1]
    re.search(re.compile('[0-9]+'), ulice_cp)
    match = re.search('[0-9]+/*[0-9]*', ulice_cp)
    if match:
        ulice = ulice_cp[:match.start()-1]
        cp = match.group()
    else:
        ulice = ulice_cp
        cp = None

    okres = adresa[2].replace('okres ', '') if 'okres' in adresa[2] else ''
    try:
        kraj = adresa[3].replace('kraj ', '') if 'kraj' in adresa[3] else ''
    except IndexError:
        kraj = None

    return psc, obec, ulice, cp, okres, kraj

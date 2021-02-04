#!/usr/bin/env python3

"""Funkce pro parsování xml s daty o držitelích licence.
"""

import xml.etree.ElementTree as ET
from datetime import date
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Subjekt


URL_DRZITELE = 'https://www.eru.cz/cs/licence/informace-o-drzitelich'


def najdi_xml(url, druh):
    """Najde url xml souboru s daty o držitelích licencí.

    url (str): 'https://www.eru.cz/cs/licence/informace-o-drzitelich'
    druh (str): 'výroba elektřiny' nebo 'výroba tepelné energie'
    Vrátí: str
    """
    r = requests.get(url, timeout=7)
    bs = BeautifulSoup(r.content, 'html.parser')
    xml_url = bs.find("a", text=druh).attrs['href']
    xml_url = "https://www.eru.cz" + xml_url
    print(f'Máme url xml souboru: {xml_url}')
    return xml_url


def data_z_xml(xml_url, druh):
    """Vrátí list s daty o subjektech (slovníky).

    xml: url xml souboru (string)
    Vrátí: list
    """
    r = requests.get(xml_url, timeout=10)
    r.encoding = 'cp1250'
    root = ET.fromstring(r.text)
    subjekty = []
    for child in root:
        subjekt = child.attrib
        subjekt = {k.lower(): v for k, v in subjekt.items()}
        subjekty.append(subjekt)
    print(f"Máme data o {len(subjekty)} subjektech")
    return subjekty


def uprav_subjekty(subjekty, druh):
    """Upraví data o subjektech.
    Vrátí: None
    """
    for subjekt in subjekty:
        for klic in list(subjekt.keys()):
            if '----' in subjekt.get(klic):
                subjekt[klic] = ''
            if '_den_' in klic:
                try:
                    subjekt[klic] = date.fromisoformat(subjekt.get(klic))
                except ValueError:
                    subjekt[klic] = None
            if 'o_s_' in klic:
                subjekt.pop(klic, 'None')
        subjekt['predmet'] = druh


def parsuj_drzitele(url, druh):
    """Získá data o držitelích licence pro druh.
    URL: str
    druh: str
    Vrátí: list (obsahující slovníky)
    """
    xml_url = najdi_xml(url, druh)
    subjekty = data_z_xml(xml_url, druh)
    uprav_subjekty(subjekty, druh)
    return subjekty


if __name__ == '__main__':
    subjekty = parsuj_drzitele(URL_DRZITELE, 'výroba elektřiny')
    engine = create_engine('sqlite:///licence.db')

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    for subjekt in subjekty:
        session.add(Subjekt(**subjekt))

    session.commit()

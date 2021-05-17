import datetime
import pathlib
import pytest
from holders.config import conf


from holders import main

test_subject = main.Holder(
    id='110100009', version=18, status='Aktivní verze', ic='70889953',
    nazev='Povodí Vltavy, státní podnik', cislo_dom='3178', cislo_or='8', ulice='Holečkova',
    obec='Praha', obec_cast='Smíchov', psc='150 00', okres='Hlavní město Praha', 
    kraj='Hlavní město Praha', zeme='CZ',den_opravneni=datetime.date(2001, 7, 1),
    den_zahajeni=datetime.date(2001, 7, 1), den_zaniku=datetime.date(2026, 7, 16),
    den_nabyti=datetime.date(2021, 1, 11), osoba='Yvona Křáková'
    )


def test_parse_electricity_xml_from_file():
    xml = pathlib.Path('samples') / conf.get('samples', 'electricity')
    result = main.parse_xml(xml)
    assert result[0] == test_subject


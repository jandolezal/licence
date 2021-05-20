import pathlib
import pytest

from bs4 import BeautifulSoup

from licenses import parse
from licenses.parse import Licence, Provozovna, VykonProvozovna, VykonLicence


def test_plzen():
    plzen_path = pathlib.Path('samples/plzen.html')
    with open(plzen_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100054', bs)
    
    plzen = Licence(id='110100054', predmet='výroba elektřiny', pocet_zdroju=3, 
    provozovny=[
        Provozovna(id=1, lic_id='110100054', nazev='ELÚ 3', 
        ulice='Tylova', cp=None, psc='31600', obec='Plzeň', okres='Plzeň-město', kraj='Plzeňský',
        pocet_zdroju=3, katastralni_uzemi=None, kod_katastru=None, vymezeni=None,
        vykony=[
            VykonProvozovna(provozovna_id=1, druh='Elektrický', technologie='Celkový', mw=90.0),
            VykonProvozovna(provozovna_id=1, druh='Tepelný', technologie='Celkový', mw=430.1),
            VykonProvozovna(provozovna_id=1, druh='Elektrický', technologie='Parní', mw=90.0),
            VykonProvozovna(provozovna_id=1, druh='Tepelný', technologie='Parní', mw=430.1)])
            ],
    vykony=[
        VykonLicence(lic_id='110100054', druh='Elektrický', technologie='Celkový', mw=90.0),
        VykonLicence(lic_id='110100054', druh='Tepelný', technologie='Celkový', mw=430.1),
        VykonLicence(lic_id='110100054', druh='Elektrický', technologie='Parní', mw=90.0),
        VykonLicence(lic_id='110100054', druh='Tepelný', technologie='Parní', mw=430.1)]
        )

    assert plzen == result
    assert result.provozovny[0].vykony[0].technologie == 'Celkový'
    assert result.provozovny[0].vykony[0].druh == 'Elektrický'
    assert result.provozovny[0].vykony[0].mw == 90.0

    assert result.provozovny[0].vykony[3].technologie == 'Parní'
    assert result.provozovny[0].vykony[3].mw == 430.1

def test_oleska():
    oleska_path = pathlib.Path('samples/oleska.html')
    with open(oleska_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100054', bs)
    
    assert result.id == '110100054'
    assert len(result.provozovny) == 1
    assert result.pocet_zdroju == 2

    assert result.provozovny[0].vykony[0].technologie == 'Celkový'
    assert result.provozovny[0].vykony[0].druh == 'Elektrický'
    assert result.provozovny[0].vykony[0].mw == 0.013

    assert result.provozovny[0].vykony[1].technologie == 'Vodní'
    assert result.provozovny[0].vykony[1].mw == 0.013

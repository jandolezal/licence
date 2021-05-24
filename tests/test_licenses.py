import pathlib

from bs4 import BeautifulSoup

from licenses import parse


def test_plzen():
    plzen_path = pathlib.Path('samples/plzen.html')
    with open(plzen_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100054', bs)

    assert result.provozovny[0].vykony[0].technologie == 'Celkový'
    assert result.provozovny[0].vykony[0].druh == 'Elektrický'
    assert result.provozovny[0].vykony[0].mw == 90.0

    assert result.provozovny[0].vykony[3].technologie == 'Parní'
    assert result.provozovny[0].vykony[3].mw == 430.1


def test_oleska():
    oleska_path = pathlib.Path('samples/oleska.html')
    with open(oleska_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100010', bs)

    assert result.id == '110100010'
    assert len(result.provozovny) == 1
    assert result.pocet_zdroju == 2
    assert result.vykony[0].mw == 0.013
    assert 'Tepelný' not in [vykon.druh for vykon in result.vykony]

    assert result.provozovny[0].kod_katastru == '670936'

    assert result.provozovny[0].vykony[0].technologie == 'Celkový'
    assert result.provozovny[0].vykony[0].druh == 'Elektrický'
    assert result.provozovny[0].vykony[0].mw == 0.013

    assert result.provozovny[0].vykony[1].technologie == 'Vodní'
    assert result.provozovny[0].vykony[1].mw == 0.013

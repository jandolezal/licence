import pathlib
import os
from unittest.mock import patch

from bs4 import BeautifulSoup

from licenses import parse
from licenses.main import read_lic_ids, read_lic_count


@patch('pathlib.Path')
def test_read_lic_ids(mock_path):
    sample_path = os.path.abspath('samples/sample_holders.csv')
    mock_path.return_value = sample_path

    ids_list = read_lic_ids('electricity')

    assert ids_list[0] == '110100009'
    assert ids_list[-1] == '110100032'


@patch('pathlib.Path')
def test_read_lic_count(mock_path):
    sample_path = os.path.abspath('samples/sample_holders.csv')
    mock_path.return_value = sample_path

    ids_count = read_lic_count('electricity')

    assert ids_count == 10


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

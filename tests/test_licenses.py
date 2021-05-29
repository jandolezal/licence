import pathlib
import os
import csv
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


def test_cez():
    cez_path = pathlib.Path('samples/cez.html')
    with open(cez_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100146', bs)

    assert result.id == '110100146'
    assert result.pocet_zdroju == 72

    assert result.vykony[0].lic_id == '110100146'
    assert result.vykony[0].druh == 'Elektrický'
    assert result.vykony[0].technologie == 'Celkový'
    assert result.vykony[0].mw == 9716.003

    assert result.provozovny[0].vykony[0].technologie == 'Celkový'
    assert result.provozovny[0].vykony[0].druh == 'Elektrický'
    assert result.provozovny[0].vykony[0].mw == 7.3

    assert result.provozovny[0].vykony[3].technologie == 'Parní'
    assert result.provozovny[0].vykony[3].mw == 49.8
    assert result.provozovny[0].pocet_zdroju == 2

    assert result.provozovny[-1].pocet_zdroju == 1
    assert result.provozovny[-1].nazev == 'Elektrárna Ledvice IV B6'
    assert result.provozovny[-1].vykony[-1].technologie == 'Parní'
    assert result.provozovny[-1].vykony[-1].mw == 1288.130


def test_plzen_export_to_csv():
    oleska_path = pathlib.Path('samples/plzen.html')
    with open(oleska_path) as f:
        bs = BeautifulSoup(f, 'html.parser')
        result = parse.parse_page('výroba elektřiny', '110100054', bs)

    # Export csvs within tests directory
    output_dir = pathlib.Path('tests/licenses/electricity/')
    result.to_csv(output_dir, 'licenses.csv')

    output_dir_list = list(output_dir.iterdir())
    sub_path = 'tests/licenses/electricity'

    assert pathlib.Path(f'{sub_path}/licenses.csv') in output_dir_list
    assert pathlib.Path(f'{sub_path}/capacities.csv') in output_dir_list
    assert pathlib.Path(f'{sub_path}/facilities.csv') in output_dir_list
    assert pathlib.Path(f'{sub_path}/facilities_capacities.csv') in output_dir_list

    with open(f'{sub_path}/facilities.csv') as csvf:
        reader = csv.DictReader(csvf)
        data = [row for row in reader]
        assert len(data) == 1
        assert data[0]['id'] == '1'
        assert data[0]['lic_id'] == '110100054'
        assert data[0]['nazev'] == 'ELÚ 3'

    with open(f'{sub_path}/licenses.csv') as csvf:
        reader = csv.DictReader(csvf)
        data = [row for row in reader]
        assert len(data) == 1
        assert data[0]['id'] == '110100054'
        assert data[0]['pocet_zdroju'] == '3'

    with open(f'{sub_path}/capacities.csv') as csvf:
        reader = csv.DictReader(csvf)
        data = [row for row in reader]
        assert len(data) == 4
        assert data[0]['mw'] == '90.0'
        assert data[0]['druh'] == 'Elektrický'
        assert data[1]['mw'] == '430.1'
        assert data[1]['druh'] == 'Tepelný'
        assert data[2]['technologie'] == 'Parní'

    # Cleanup
    for csvfile in [
        'capacities.csv', 'facilities.csv', 'facilities_capacities.csv',
        'licenses.csv'
            ]:
        pathlib.Path(f'{sub_path}/{csvfile}').unlink()
    pathlib.Path(f'{sub_path}').rmdir()
    pathlib.Path('tests/licenses').rmdir()

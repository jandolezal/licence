import unittest
from collections import namedtuple
from scrapuj import URL, params
import parsuj
import adresy


Firma = namedtuple('Firma', [
    'cislo_licence', 'provozovny_pocet', 'celkovy_el',
    'celkovy_tep', 'prov_nazev', 'prov_ulice', 'prov_cp',
    'prov_okres', 'prov_kod_katastru',
    ])

cez = Firma(
    '110100146', 29, '10436.003', '5369.050',
    'Teplárna Trmice', 'Edisonova', '453', 'Ústí nad Labem', '774979',
    )

knezice = Firma(
    '110604965', 1, '0.330', '0.405', 'Bioplynová stanice',
    'Kněžice', '205', 'Nymburk', '666921',
    )

jmena = [
    'Zdeněk\xa0\n\t\tWirth', 'Yvona\xa0\n\t\tKřáková',
    'Ing.\xa0\n\t\tJaroslav\xa0\n\t\tHába', 'František\xa0\n\t\tPéli',
    'Petr\xa0\n\t\tBartoš', 'Roman\xa0\n\t\tČech',
    'Miroslav\xa0\n\t\tHrubý', 'Zdeněk\xa0\n\t\tWinter',
    ]

cvicne_adresy = [
    '582 32\xa0Lipnice nad Sázavou,\xa0\n\t\t\t\t\t\t\t\t\tLipnice nad Sázavou,\xa0\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\tokres Havlíčkův Brod,\xa0\n\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\tkraj Vysočina',
    '268 01\xa0Hořovice,\xa0\n\t\t\t\t\t\t\t\t\tKomenského\xa01245/7,\xa0\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\tokres Beroun,\xa0\n\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\tkraj Středočeský',
    '339 01\xa0Klatovy,\xa0\n\t\t\t\t\t\t\t\t\tJateční\xa0660,\xa0\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t\tokres Klatovy,\xa0\n\t\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\tkraj Plzeňský',
    ]


class ParserTestCez(unittest.TestCase):
    bs = None

    @classmethod
    def setUpClass(cls):
        params.update({'lic-id': cez.cislo_licence})
        cls.bs = parsuj.priprav_bs(URL, params=params)

    def test_cez_cislo_licence(self):
        result = parsuj.parsuj_stranku(self.bs)['cislo_licence']
        self.assertEqual(result, cez.cislo_licence)

    def test_cez_pocet_provozoven(self):
        result = len(parsuj.parsuj_stranku(self.bs)['provozovny'])
        self.assertEqual(result, cez.provozovny_pocet)

    def test_cez_celkovy_elektricky(self):
        result = parsuj.parsuj_stranku(self.bs)['celkovy_el']
        self.assertEqual(result, cez.celkovy_el)

    def test_cez_celkovy_tepelny(self):
        result = parsuj.parsuj_stranku(self.bs)['celkovy_tep']
        self.assertEqual(result, cez.celkovy_tep)

    def test_cez_trmice_nazev(self):
        result = parsuj.parsuj_stranku(self.bs)['provozovny'][26]['nazev']
        self.assertEqual(result, cez.prov_nazev)

    def test_cez_trmice_ulice(self):
        result = parsuj.parsuj_stranku(self.bs)['provozovny'][26]['ulice']
        self.assertEqual(result, cez.prov_ulice)

    def test_cez_trmice_cp(self):
        result = parsuj.parsuj_stranku(self.bs)['provozovny'][26]['cp']
        self.assertEqual(result, cez.prov_cp)

    def test_cez_trmice_okres(self):
        result = parsuj.parsuj_stranku(self.bs)['provozovny'][26]['okres']
        self.assertEqual(result, cez.prov_okres)

    def test_cez_trmice_kod_katastru(self):
        stranka = parsuj.parsuj_stranku(self.bs)
        result = stranka['provozovny'][26]['kod_katastru']
        self.assertEqual(result, cez.prov_kod_katastru)


class ParserTestKnezice(unittest.TestCase):
    bs = None

    @classmethod
    def setUpClass(cls):
        params.update({'lic-id': knezice.cislo_licence})
        cls.bs = parsuj.priprav_bs(URL, params=params)

    def test_cez_cislo_licence(self):
        result = parsuj.parsuj_stranku(self.bs)['cislo_licence']
        self.assertEqual(result, knezice.cislo_licence)

    def test_cez_pocet_provozoven(self):
        result = len(parsuj.parsuj_stranku(self.bs)['provozovny'])
        self.assertEqual(result, knezice.provozovny_pocet)

    def test_cez_celkovy_elektricky(self):
        result = parsuj.parsuj_stranku(self.bs)['celkovy_el']
        self.assertEqual(result, knezice.celkovy_el)

    def test_cez_celkovy_tepelny(self):
        result = parsuj.parsuj_stranku(self.bs)['celkovy_tep']
        self.assertEqual(result, knezice.celkovy_tep)


class AdresaTest(unittest.TestCase):

    def test_rozdel_obec_1(self):
        result = adresy.rozdel_adresu(adresy.uprav_adresu(cvicne_adresy[0]))
        rozdelene = '58232', 'Lipnice nad Sázavou', 'Lipnice nad Sázavou', '', 'Havlíčkův Brod', 'Vysočina'
        self.assertEqual(result, rozdelene)

    def test_rozdel_obec_2(self):
        result = adresy.rozdel_adresu(adresy.uprav_adresu(cvicne_adresy[1]))
        rozdelene = '26801', 'Hořovice', 'Komenského', '1245/7', 'Beroun', 'Středočeský'
        self.assertEqual(result, rozdelene)

    def test_rozdel_obec_3(self):
        result = adresy.rozdel_adresu(adresy.uprav_adresu(cvicne_adresy[2]))
        rozdelene = '33901', 'Klatovy', 'Jateční', '660', 'Klatovy', 'Plzeňský'
        self.assertEqual(result, rozdelene)


if __name__ == '__main__':
    unittest.main()

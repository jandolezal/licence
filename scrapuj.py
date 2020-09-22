#!/usr/bin/env python

"""Scrapuje udělené licence na výrobu elektřiny z webu ERÚ licence.eru.cz/
"""

import csv
import json
import parsuj

URL = 'http://licence.eru.cz/detail.php'
params = dict(SelAdProcStatusId='Udělená licence', GroupId='31')

if __name__ == '__main__':
    with open('licence.csv', 'r') as csvf:
        reader = csv.DictReader(csvf)
        licence = [row['cislo_licence'] for row in reader]

    data = []

    for lic in licence:
        params.update({'lic-id': lic})
        data_z_licence = parsuj.parsuj_stranku(parsuj.priprav_bs(URL, params))
        data.append(data_z_licence)

    with open('elektrina.json', 'w') as f:
        json.dump(data, f)

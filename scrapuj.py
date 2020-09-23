#!/usr/bin/env python

"""Scrapuje udělené licence na výrobu elektřiny z webu ERÚ licence.eru.cz/
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Subjekt, Provozovna
import parsuj


def scrapuj(url, params, db, start, end):
    engine = create_engine(db)
    Session = sessionmaker(bind=engine)
    session = Session()

    licence = []

    for instance in session.query(Subjekt).order_by(Subjekt.id):
        licence.append(instance.cislo_licence)

    for lic in licence[start:end]:
        params.update({'lic-id': lic})

        data_z_licence = parsuj.parsuj_stranku(parsuj.priprav_bs(URL, params))

        # Update dat o subjektech (základ byl v xml na jiné stránce)
        data_subjektu = {k: v for k, v in data_z_licence.items() if k not in ['cislo_licence', 'provozovny']}
        session.query(Subjekt).filter(Subjekt.cislo_licence == lic).update(data_subjektu)

        # Přidání provozoven do tabulky
        id = session.query(Subjekt).filter(Subjekt.cislo_licence == lic).first().id
        provozovny = data_z_licence['provozovny']

        for provoz in provozovny:
            provoz.update({'subjekt_id': id})
            session.add(Provozovna(**provoz))

    session.commit()


URL = 'http://licence.eru.cz/detail.php'
params = dict(SelAdProcStatusId='Udělená licence', GroupId='31')

if __name__ == '__main__':
    scrapuj(URL, params, db='sqlite:///licence.db', start=29_000, end=29_126)

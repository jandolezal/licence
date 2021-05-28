#!/usr/bin/env python3

"""Scrapuje udělené licence na výrobu elektřiny z webu ERÚ licence.eru.cz/
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from old.models import Subjekt, Provozovna
from old import parsuj


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


if __name__ == '__main__':
    URL = 'http://licence.eru.cz/detail.php'
    PARAMS = dict(SelAdProcStatusId='Udělená licence', GroupId='31')
    scrapuj(URL, PARAMS, db='sqlite:///licence.db', start=27_000, end=29_306)

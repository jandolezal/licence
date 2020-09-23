from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String, Date


Base = declarative_base()


class Subjekt(Base):
    __tablename__ = 'subjekty'

    id = Column(Integer, primary_key=True)
    cislo_licence = Column(Integer, index=True)
    version = Column(Integer, index=True)
    version_status = Column(String(64))
    subjekt_ic = Column(String(9), index=True)
    subjekt_nazev = Column(String(128))
    subjekt_cislo_dom = Column(String(10))
    subjekt_cislo_or = Column(String(10))
    subjekt_ulice_nazev = Column(String(64))
    subjekt_obec_cast = Column(String(64))
    subjekt_obec_nazev = Column(String(64))
    subjekt_psc = Column(String(6))
    subjekt_okres = Column(String(64))
    subjekt_kraj = Column(String(64))
    subjekt_zeme = Column(String(64))
    subjekt_den_opravneni = Column(Date)
    subjekt_den_zahajeni = Column(Date)
    subjekt_den_zaniku = Column(Date)
    subjekt_den_nabyti_pravni_moci = Column(Date)
    predmet = Column(String(64))
    odpovedny_zastupce = Column(String(64))
    pocet_zdroju = Column(Integer)
    celkovy_el = Column(Float)
    celkovy_tep = Column(Float)
    horkovodni_el = Column(Float)
    horkovodni_tep = Column(Float)
    teplovodni_el = Column(Float)
    teplovodni_tep = Column(Float)
    parni_el = Column(Float)
    parni_tep = Column(Float)
    kvet_el = Column(Float)
    kvet_tep = Column(Float)
    kogenerace_el = Column(Float)
    kogenerace_tep = Column(Float)
    plynovy_el = Column(Float)
    plynovy_tep = Column(Float)
    jaderny_el = Column(Float)
    jaderny_tep = Column(Float)
    precerpavaci_el = Column(Float)
    precerpavaci_tep = Column(Float)
    paroplynova_el = Column(Float)
    paroplynova_tep = Column(Float)
    slunecni_el = Column(Float)
    slunecni_tep = Column(Float)
    vetrny_el = Column(Float)
    vetrny_tep = Column(Float)
    vodni_el = Column(Float)
    vodni_tep = Column(Float)
    ostatni_el = Column(Float)
    ostatni_tep = Column(Float)

    def __repr__(self):
        return f'<Subjekt: {self.cislo_licence}, {self.subjekt_nazev}>'

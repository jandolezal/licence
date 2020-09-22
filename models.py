from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date


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

    def __repr__(self):
        return f'<Subjekt: {self.cislo_licence}, {self.subjekt_nazev}>'

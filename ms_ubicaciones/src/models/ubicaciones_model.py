from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PaisModel(Base):
    """usr_app.countries: catalogo mundial de paises."""

    __tablename__ = "countries"
    __table_args__ = {"schema": "usr_app"}

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class DepartamentoModel(Base):
    """usr_app.departments: solo hay departamentos de Colombia cargados."""

    __tablename__ = "departments"
    __table_args__ = {"schema": "usr_app"}

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("usr_app.countries.id"))
    name = Column(String)
    code = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class MunicipioModel(Base):
    """usr_app.municipalities: municipios colgados de un departamento."""

    __tablename__ = "municipalities"
    __table_args__ = {"schema": "usr_app"}

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("usr_app.departments.id"))
    name = Column(String)
    code = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

# encoding: utf-8

import datetime
import logging

from sqlalchemy import Column, ForeignKey, func, String, distinct, text
from sqlalchemy.orm import relationship
from sqlalchemy import orm

import ckan.model.package as _package
from ckanext.rdkit_visuals.models.molecule_tab import Molecules
from sqlalchemy import types as _types
from ckan.model import Session
from ckan.model import meta
from .base import Base

#__all__ =[u"MolecularRelationData", "molecule_rel_data_table"]

class MolecularRelationData(Base):

    __tablename__ = "molecule_rel_data"
    __table_args__ = {'schema': 'public'}

    """
    Table which contains molecule and package relationship.
    
    molecules_id from molecules data table are stored here. 
    Which internally, relates to the packages and their ids. 
    
    These two are combined in this table, for simpler access. 
    
    """
    id = Column(u'id', _types.Integer, primary_key=True, autoincrement=True, nullable=False)
    molecules_id = Column(u'molecules_id', _types.Integer, ForeignKey(u'molecules.id'), nullable=False)
    package_id = Column(u'package_id', _types.UnicodeText, ForeignKey(_package.Package.id), nullable=False)

    @classmethod
    def create(cls, molecules_id, package_id):
        """
        Create a new MoleculeRelData entry and store it in the database.

        :param molecules_id: The ID of the molecule
        :param package_id: The ID of the package
        :param session: The SQLAlchemy session for database interaction
        :return: The created MoleculeRelData instance
        """
        new_entry = cls(molecules_id=molecules_id, package_id=package_id)
        Session.add(new_entry)
        Session.commit()
        return new_entry

    @classmethod
    def get_package_list_inchi_key(cls, page_size, current_page):
        """
        Get the list of InChIKeys and their associated packages IDs.

        :param page_size: The number of records per page
        :param current_page: The current page number
        :return: InChIKeys and their associated packages IDs  (inchi_key, package_ids)
        """
        offset_value = (current_page - 1) * page_size

        subquery = Session.query(
            cls.molecules_id,
            func.string_agg(cls.package_id.cast(_types.String), ', ').label('package_ids')
        ).group_by(cls.molecules_id).subquery()

        query = Session.query(
            Molecules.inchi_key,
            subquery.c.package_ids
        ).join(
            Molecules,
            Molecules.id == subquery.c.molecules_id
        ).limit(page_size).offset(offset_value)

        return query.all()

    @classmethod
    def get_count_rows(cls):
        """
        Get the number of rows/molecules with datasets in molecule_rel_data table.
        :return: Number of rows to display "n Molecules Found"
        """
        subquery = Session.query(
            cls.molecules_id,
            cls.package_id
        ).distinct(cls.molecules_id).subquery()

        count = Session.query(func.count()).select_from(subquery).scalar()
        return count

    @classmethod
    def get_mol_formula_by_package_id(cls, package_id):
        """

        :param package_id:
        :return:
        """

        molecules_sub_query = Session.query(
            cls.molecules_id
        ).filter(cls.package_id == package_id).subquery()

        mol_formula = Session.query(Molecules.mol_formula).filter(Molecules.id.in_(molecules_sub_query)).all()

        return mol_formula

    @classmethod
    def get_exact_mass_by_package_id(cls, package_id):
        """

        :param package_id:
        :return:
        """
        molecules_sub_query = Session.query(
            cls.molecules_id
        ).filter(cls.package_id == package_id).subquery()

        exact_mass = Session.query(Molecules.exact_mass).filter(Molecules.id.in_(molecules_sub_query)).all()
        return exact_mass

    @classmethod
    def get_molecule_data_by_package_id(cls, package_id):
        """
        :param package_id:
        :return: A list of molecules data for given molecule id via molecule_rel_data and package_id
        """

        molecules_sub_query = Session.query(
            cls.molecules_id
        ).filter(cls.package_id == package_id).subquery()

        inchi = Session.query(Molecules.inchi).filter(Molecules.id.in_(molecules_sub_query)).all()
        iupac_name = Session.query(Molecules.iupac_name).filter(Molecules.id.in_(molecules_sub_query)).all()
        molecule_name = Session.query(Molecules.molecule_name).filter(Molecules.id.in_(molecules_sub_query)).all()

        return inchi,iupac_name, molecule_name




# relationship to build between molecules and packages
package = relationship(_package.Package, secondary= MolecularRelationData, back_populates="molecular_relation_data", cascade="all, delete")

# encoding: utf-8

from sqlalchemy import Column, ForeignKey, func, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy import orm

from ckan.model import meta, Package, domain_object
from sqlalchemy import types as _types
from ckan.model import Session
from ckan.model import meta
from .base import Base


class Molecules(Base):
    __tablename__ = 'molecules'

    """
    Molecules is an essential table for storing the molecular information in a database using RDKit visuals while
    harvesting the metadata through CKAN harvesters.
    
    """

    id = Column(_types.Integer, primary_key=True, autoincrement=True)
    inchi = Column(_types.String)
    canonical_smiles = Column(_types.String)
    inchi_key = Column(_types.String)
    exact_mass = Column(Float)
    mol_formula = Column(_types.String)
    iupac_name = Column(_types.String)
    alternate_names = Column(_types.String)
    molecule_name = Column(_types.String)

    # Relationship with the Package model
    # package = relationship('Package')

    # Additional methods can be added here as needed

    @classmethod
    def create(cls, inchi, canonical_smiles, inchi_key, exact_mass, mol_formula,iupac_name, alternate_names, molecule_name):
        """
        Create a new Molecule entry and store it in the database.

        :param package_id: The ID of the package
        :param inchi: InChI string for the molecule
        :param smiles: SMILES string for the molecule
        :param inchi_key: InChI key for the molecule
        :param exact_mass: The exact mass of the molecule
        :param mol_formula: The molecular formula of the molecule
        :param session: The SQLAlchemy session for database interaction
        :return: The created Molecule instance
        """
        new_molecule = cls(
            inchi=inchi.strip(),
            canonical_smiles=canonical_smiles,
            inchi_key=inchi_key,
            exact_mass=exact_mass,
            mol_formula=mol_formula,
            iupac_name = iupac_name,
            alternate_names = alternate_names,
            molecule_name = molecule_name
        )
        Session.add(new_molecule)
        Session.commit()
        return new_molecule

    @classmethod
    def _get_inchi_from_db(cls, inchi_key):
        """

        :param inchi_key:
        :return: the id of the molecule
        """

        molecule_id_result = Session.query(Molecules.id).filter(Molecules.inchi_key == inchi_key).all()

        return molecule_id_result

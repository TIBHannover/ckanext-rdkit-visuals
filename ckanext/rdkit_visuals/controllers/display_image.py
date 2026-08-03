import base64
import io
import logging
import os

import ckan.plugins.toolkit as toolkit
from ckan.model import Session
from PIL import Image
from sqlalchemy import text

from ckanext.related_resources.models.related_resources import (
    RelatedResources as related_resources,
)
from ckanext.rdkit_visuals.models.molecule_rel import (
    MolecularRelationData as molecule_rel,
)

log = logging.getLogger(__name__)


class RdkitVisualsController(object):

    @staticmethod
    def display_image(package_name):
        """
        Return the molecule image as base64 PNG.

        The image is loaded from:
            /var/lib/ckan/default/storage/images/<inchi_key>.png
        """

        try:
            package = toolkit.get_action("package_show")(
                {},
                {"name_or_id": package_name}
            )

            inchi_key = package.get("inchi_key")

            if not inchi_key:
                log.warning(
                    "RDKit visuals: package %s has no inchi_key",
                    package_name
                )
                return ""

            if str(inchi_key).startswith("data"):
                log.warning(
                    "RDKit visuals: package %s has invalid image key: %s",
                    package_name,
                    inchi_key
                )
                return ""

            image_path = os.path.join(
                "/var/lib/ckan/default/storage/images",
                str(inchi_key) + ".png"
            )

            if not os.path.exists(image_path):
                log.warning(
                    "RDKit visuals: image file not found for package %s: %s",
                    package_name,
                    image_path
                )
                return ""

            with open(image_path, "rb") as image_file:
                image = Image.open(io.BytesIO(image_file.read()))

            output = io.BytesIO()
            image.save(output, "PNG")
            output.seek(0)

            return base64.b64encode(output.getvalue()).decode("ascii")

        except Exception:
            log.exception(
                "RDKit visuals: failed to render image for package %s",
                package_name
            )
            return ""

    @staticmethod
    def molecule_data(package_name):
        molecule_formula = []

        package = toolkit.get_action("package_show")(
            {},
            {"name_or_id": package_name}
        )
        package_id = package["id"]

        molecule_formula_list = molecule_rel.get_mol_formula_by_package_id(
            package_id
        )

        try:
            for value in molecule_formula_list:
                molecule_formula = "['']".join(value)
        except TypeError:
            pass

        return molecule_formula

    @staticmethod
    def alternames(inchi_key=None, package_id=None, package_name=None):
        """Return alternate molecule names for an InChIKey.

        ``package_id`` and ``package_name`` are retained for callers that do
        not yet have the InChIKey.  They are resolved through ``package_show``
        before querying the molecule tables.
        """
        package_reference = package_id or package_name
        if not inchi_key and package_reference:
            try:
                package = toolkit.get_action("package_show")(
                    {}, {"name_or_id": package_reference}
                )
                inchi_key = package.get("inchi_key")
            except Exception:
                log.exception(
                    "RDKit visuals: failed to resolve InChIKey for package %s",
                    package_reference,
                )
                return []

        if not inchi_key:
            return []

        query = text("""
            SELECT names.name
            FROM (
                SELECT DISTINCT mn.name
                FROM rdk.molecules AS molecule
                JOIN rdk.molecule_names AS mn
                  ON mn.molecule_id = molecule.molecule_id
                WHERE molecule.inchi_key = :inchi_key
                  AND mn.name IS NOT NULL
                  AND btrim(mn.name) <> ''
            ) AS names
            ORDER BY lower(names.name), names.name
        """)

        try:
            rows = Session.execute(query, {"inchi_key": inchi_key})
            return [row[0] for row in rows]
        except Exception:
            log.exception(
                "RDKit visuals: failed to load alternate names for InChIKey %s",
                inchi_key,
            )
            return []

    @staticmethod
    def related_resources(package_name):
        rel_values = []

        package = toolkit.get_action("package_show")(
            {},
            {"name_or_id": package_name}
        )
        package_id = package["id"]

        try:
            rel_values = related_resources.get_relation_values_by_package_id(
                package_id
            )
        except Exception:
            pass

        if any(None in elem for elem in rel_values):
            return None

        return rel_values

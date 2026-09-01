from unittest import mock

from sqlalchemy.sql.elements import TextClause

from ckanext.rdkit_visuals.controllers.display_image import (
    RdkitVisualsController,
)


def test_alternate_names_returns_query_results_as_strings():
    rows = [
        ("FUSARENON X",),
        ("Fusarenone X",),
        ("Fusarenon-X",),
    ]

    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        return_value=rows,
    ):
        result = RdkitVisualsController.alternames("INCHI-KEY")

    assert result == [
        "FUSARENON X",
        "Fusarenone X",
        "Fusarenon-X",
    ]
    assert all(isinstance(name, str) for name in result)


def test_alternate_names_query_filters_deduplicates_and_orders_names():
    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        return_value=[],
    ) as execute:
        result = RdkitVisualsController.alternames("INCHI-KEY")

    query, parameters = execute.call_args[0]
    normalized_sql = " ".join(str(query).split())

    assert result == []
    assert isinstance(query, TextClause)
    assert "SELECT DISTINCT mn.name" in normalized_sql
    assert "mn.name IS NOT NULL" in normalized_sql
    assert "btrim(mn.name) <> ''" in normalized_sql
    assert "ORDER BY lower(names.name), names.name" in normalized_sql
    assert "molecule.inchi_key = :inchi_key" in normalized_sql
    assert "mn.molecule_id = molecule.id" in normalized_sql
    assert parameters == {"inchi_key": "INCHI-KEY"}
    assert "INCHI-KEY" not in str(query)


def test_alternate_names_helper_returns_empty_list_without_relation():
    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        return_value=[],
    ):
        assert RdkitVisualsController.alternames("INCHI-KEY") == []


def test_alternate_names_database_failure_is_logged_and_returns_empty_list():
    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        side_effect=RuntimeError("database unavailable"),
    ), mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.log.exception"
    ) as log_exception:
        result = RdkitVisualsController.alternames("INCHI-KEY")

    assert result == []
    log_exception.assert_called_once()


def test_alternate_names_accepts_legacy_package_name_keyword():
    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.toolkit.get_action",
        return_value=lambda context, data: {"inchi_key": "INCHI-KEY"},
    ), mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        return_value=[("Name",)],
    ) as execute:
        result = RdkitVisualsController.alternames(
            package_name="package-id"
        )
    
    assert result == ["Name"]
    assert execute.call_args[0][1] == {"inchi_key": "INCHI-KEY"}


def test_alternate_names_accepts_package_id_keyword():
    with mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.toolkit.get_action",
        return_value=lambda context, data: {"inchi_key": "INCHI-KEY"},
    ) as get_action, mock.patch(
        "ckanext.rdkit_visuals.controllers.display_image.Session.execute",
        return_value=[("Name",)],
    ) as execute:
        result = RdkitVisualsController.alternames(package_id="package-id")

    assert result == ["Name"]
    get_action.assert_called_once_with("package_show")
    assert execute.call_args[0][1] == {"inchi_key": "INCHI-KEY"}

from pathlib import Path

import yaml

from app.main import app

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def test_openapi_document_matches_fastapi_routes_and_version():
    document_path = Path(__file__).resolve().parents[2] / "openapi.yaml"
    document = yaml.safe_load(document_path.read_text(encoding="utf-8"))
    runtime_document = app.openapi()
    documented_paths = set(document["paths"])
    runtime_paths = set(runtime_document["paths"])

    assert runtime_paths == documented_paths
    assert document["info"]["version"] == app.version
    assert runtime_document["info"]["version"] == app.version
    for path, operations in runtime_document["paths"].items():
        runtime_methods = {method for method in operations if method in HTTP_METHODS}
        documented_methods = {
            method for method in document["paths"][path] if method in HTTP_METHODS
        }
        assert runtime_methods == documented_methods, path


def test_openapi_telemetry_range_matches_tmp117_contract():
    document_path = Path(__file__).resolve().parents[2] / "openapi.yaml"
    document = yaml.safe_load(document_path.read_text(encoding="utf-8"))
    temperature = document["components"]["schemas"]["TelemetrySample"]["properties"]["temperature_deci_c"]
    assert temperature["minimum"] == -550
    assert temperature["maximum"] == 1500

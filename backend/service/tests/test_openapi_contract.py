from pathlib import Path

import yaml

from app.main import app


def test_openapi_document_matches_runtime_routes_and_version():
    document_path = Path(__file__).resolve().parents[2] / "openapi.yaml"
    document = yaml.safe_load(document_path.read_text(encoding="utf-8"))
    documented_paths = set(document["paths"])
    runtime_routes = [
        route for route in app.routes
        if getattr(route, "path", "").startswith(("/api/v1/", "/health/"))
    ]
    runtime_paths = {route.path for route in runtime_routes}

    assert runtime_paths == documented_paths
    assert document["info"]["version"] == app.version
    for route in runtime_routes:
        methods = {method.lower() for method in (route.methods or set())}
        assert methods <= set(document["paths"][route.path])


def test_openapi_telemetry_range_matches_tmp117_contract():
    document_path = Path(__file__).resolve().parents[2] / "openapi.yaml"
    document = yaml.safe_load(document_path.read_text(encoding="utf-8"))
    temperature = document["components"]["schemas"]["TelemetrySample"]["properties"]["temperature_deci_c"]
    assert temperature["minimum"] == -550
    assert temperature["maximum"] == 1500

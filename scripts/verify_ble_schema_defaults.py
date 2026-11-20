#!/usr/bin/env python3
"""Validate the initial BLE values against the published read-only schemas."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

SOURCE = Path("firmware/esp-idf/main/ble_service.c")


def extract_initial_json(name: str) -> dict:
    source = SOURCE.read_text(encoding="utf-8")
    match = re.search(
        rf'static char {name}\[(\d+)\] = ("(?:\\\\.|[^"\\\\])*");',
        source,
    )
    if match is None:
        raise SystemExit(f"{name}: initial JSON declaration not found")
    capacity = int(match.group(1))
    payload = json.loads(ast.literal_eval(match.group(2)))
    if len(match.group(2)) - 2 >= capacity:
        raise SystemExit(f"{name}: default JSON exceeds its C buffer")
    return payload


telemetry = extract_initial_json("telemetry_json")
assert set(telemetry) == {"v", "n", "bv", "vv", "ba", "av", "tc", "tv", "e", "s", "vc", "pe"}
assert telemetry == {
    "v": 1, "n": 0, "bv": None, "vv": False, "ba": None, "av": False,
    "tc": None, "tv": False, "e": 0, "s": 0, "vc": 0, "pe": False,
}

diagnostics = extract_initial_json("diagnostics_json")
assert set(diagnostics) == {"v", "rr", "nv", "sn", "mo", "rf", "cg"}
assert diagnostics == {"v": 1, "rr": 0, "nv": 0, "sn": 0, "mo": 0, "rf": 3, "cg": 0}

source = SOURCE.read_text(encoding="utf-8")
assert ".flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY" in source
assert ".flags = BLE_GATT_CHR_F_READ," in source
assert "BLE_GATT_CHR_F_WRITE" not in source
print("BLE telemetry and diagnostics defaults match read-only schema v1")

#!/usr/bin/env python3
"""Validate BLE wire defaults, read-only permissions and published v1 contracts."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

SOURCE = Path("firmware/esp-idf/main/ble_service.c")
DOC = Path("protocol/BLE_PROTOCOL.md")


def extract_initial_json(name: str) -> dict:
    line = next((item for item in SOURCE.read_text(encoding="utf-8").splitlines()
                 if item.startswith(f"static char {name}[")), None)
    if line is None:
        raise SystemExit(f"{name}: initial JSON declaration not found")
    capacity = int(line.split("[", 1)[1].split("]", 1)[0])
    encoded = line.split("= ", 1)[1].rstrip(";")
    payload = json.loads(ast.literal_eval(encoded))
    if len(encoded) - 2 >= capacity:
        raise SystemExit(f"{name}: default JSON exceeds its C buffer")
    return payload


telemetry = extract_initial_json("telemetry_json")
telemetry_keys = {"v", "n", "bv", "vv", "ba", "av", "tc", "tv", "e", "s", "vc", "pe"}
assert set(telemetry) == telemetry_keys
assert telemetry == {
    "v": 1, "n": 0, "bv": None, "vv": False, "ba": None, "av": False,
    "tc": None, "tv": False, "e": 0, "s": 0, "vc": 0, "pe": False,
}

diagnostics = extract_initial_json("diagnostics_json")
diagnostics_keys = {"v", "rr", "nv", "sn", "mo", "rf", "cg"}
assert set(diagnostics) == diagnostics_keys
assert diagnostics == {"v": 1, "rr": 0, "nv": 0, "sn": 0, "mo": 0, "rf": 19, "cg": 0}

source = SOURCE.read_text(encoding="utf-8")
assert ".flags = BLE_GATT_CHR_F_READ | BLE_GATT_CHR_F_NOTIFY" in source
assert ".flags = BLE_GATT_CHR_F_READ," in source
assert "BLE_GATT_CHR_F_WRITE" not in source

doc = DOC.read_text(encoding="utf-8")
for mapping in (
    "bv | battery voltage", "vv | voltage validity",
    "ba | battery current", "av | current validity",
    "tc | temperature", "tv | temperature validity",
    "e | engine state", "s | controller state",
    "vc | system voltage class", "pe | protection enabled",
    "rr | reset reason", "nv | NVS state",
    "sn | sensor state", "mo | mode;",
    "rf | reason bitmask", "cg | stored config generation",
):
    assert mapping in doc, f"BLE contract documentation missing: {mapping}"
for key in telemetry_keys | diagnostics_keys:
    assert key in doc, f"BLE contract documentation missing key: {key}"

for name in ("service_uuid", "telemetry_uuid", "diagnostics_uuid"):
    match = re.search(rf"{name} =\s*BLE_UUID128_INIT\(([^)]*)\)", source, re.S)
    assert match is not None, f"BLE UUID missing in source: {name}"
    values = re.findall(r"0x[0-9a-fA-F]{2}", match.group(1))
    assert len(values) == 16, f"Invalid UUID byte count: {name}"
    wire_uuid = " ".join(value[2:].upper() for value in values)
    assert wire_uuid in doc, f"UUID not documented: {name}"

assert "not encrypted or authenticated" in doc
assert "READ/NOTIFY only" in doc
print("BLE telemetry/diagnostics defaults, UUIDs, read-only permissions and contract documentation validated")

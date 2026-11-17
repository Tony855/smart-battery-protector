#!/usr/bin/env python3
"""Validate the SBP ESP32-C6 4 MiB partition map and optional app image size."""

from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path

FLASH_SIZE = 4 * 1024 * 1024
EXPECTED = {
    "nvs": ("data", "nvs", 0x9000, 0x6000),
    "otadata": ("data", "ota", 0xF000, 0x2000),
    "nvs_keys": ("data", "nvs_keys", 0x11000, 0x1000),
    "phy_init": ("data", "phy", 0x12000, 0x1000),
    "ota_0": ("app", "ota_0", 0x20000, 0x1D0000),
    "ota_1": ("app", "ota_1", 0x1F0000, 0x1D0000),
    "storage": ("data", "spiffs", 0x3C0000, 0x40000),
}

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def parse_int(value: str, field: str, line: int) -> int:
    try:
        return int(value.strip(), 0)
    except ValueError:
        fail(f"line {line}: invalid {field}: {value!r}")
        raise AssertionError("unreachable")

def load_partitions(path: Path) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        for line_no, raw in enumerate(handle, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            columns = next(csv.reader([raw], skipinitialspace=True))
            if len(columns) < 5 or len(columns) > 6:
                fail(f"line {line_no}: expected 5 or 6 CSV columns")
            name, kind, subtype, offset_text, size_text = (item.strip() for item in columns[:5])
            flags = columns[5].strip() if len(columns) == 6 else ""
            if name in rows:
                fail(f"line {line_no}: duplicate partition label {name}")
            rows[name] = {
                "type": kind, "subtype": subtype,
                "offset": parse_int(offset_text, "offset", line_no),
                "size": parse_int(size_text, "size", line_no),
                "flags": {flag.strip() for flag in flags.split(",") if flag.strip()},
                "line": line_no,
            }
    return rows

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-csv", type=Path, default=Path("firmware/esp-idf/partitions.csv"))
    parser.add_argument("--app-bin", type=Path)
    args = parser.parse_args()
    rows = load_partitions(args.partition_csv)
    if set(rows) != set(EXPECTED):
        fail("partition labels differ: "
             f"missing={sorted(set(EXPECTED) - set(rows))}, "
             f"unexpected={sorted(set(rows) - set(EXPECTED))}")
    intervals: list[tuple[int, int, str]] = []
    for name, expected in EXPECTED.items():
        row = rows[name]
        actual = (row["type"], row["subtype"], row["offset"], row["size"])
        if actual != expected:
            fail(f"{name}: expected {expected}, got {actual}")
        offset, size = int(row["offset"]), int(row["size"])
        if offset % 0x1000 or size % 0x1000:
            fail(f"{name}: offset and size must be 4 KiB aligned")
        end = offset + size
        if end > FLASH_SIZE:
            fail(f"{name}: extends beyond 4 MiB flash")
        intervals.append((offset, end, name))
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if previous[1] > current[0]:
            fail(f"partitions overlap: {previous[2]} and {current[2]}")
    for name in ("ota_0", "ota_1"):
        if int(rows[name]["offset"]) % 0x10000 or int(rows[name]["size"]) % 0x10000:
            fail(f"{name}: OTA app partitions must be 64 KiB aligned")
    if rows["ota_0"]["size"] != rows["ota_1"]["size"]:
        fail("OTA slots must have equal capacity")
    if "encrypted" not in rows["nvs_keys"]["flags"]:
        fail("nvs_keys must be marked encrypted for the future flash-encryption profile")
    if "factory" in rows:
        fail("factory app partition is prohibited by the planned anti-rollback profile")
    if args.app_bin:
        if not args.app_bin.is_file():
            fail(f"application binary not found: {args.app_bin}")
        image_size = args.app_bin.stat().st_size
        slot_size = int(rows["ota_0"]["size"])
        if image_size > slot_size:
            fail(f"application image {image_size} bytes exceeds OTA slot {slot_size} bytes")
        print(f"Application image: {image_size} / {slot_size} bytes ({100 * image_size / slot_size:.1f}%)")
    print("Partition layout valid: ESP32-C6 4 MiB, two equal OTA slots, no overlaps.")
    print("OTA slot capacity: {} bytes each.".format(int(rows["ota_0"]["size"])))

if __name__ == "__main__":
    main()

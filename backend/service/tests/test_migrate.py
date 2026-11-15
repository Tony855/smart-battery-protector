from pathlib import Path

import pytest

from app.migrate import checksum, migration_files, split_sql_statements


def test_split_sql_ignores_full_line_comments_and_blank_statements():
    source = """
    -- first statement
    CREATE TABLE a (id INT);
    
    -- second statement
    CREATE TABLE b (id INT);
    """
    assert split_sql_statements(source) == [
        "CREATE TABLE a (id INT)",
        "CREATE TABLE b (id INT)",
    ]


def test_checksum_is_stable_and_sensitive_to_content():
    assert checksum("SELECT 1;") == checksum("SELECT 1;")
    assert checksum("SELECT 1;") != checksum("SELECT 2;")


def test_migration_files_are_sorted_and_ignore_other_files(tmp_path: Path):
    (tmp_path / "002_second.sql").write_text("SELECT 2;", encoding="utf-8")
    (tmp_path / "001_first.sql").write_text("SELECT 1;", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a migration", encoding="utf-8")
    assert [p.name for p in migration_files(tmp_path)] == [
        "001_first.sql",
        "002_second.sql",
    ]

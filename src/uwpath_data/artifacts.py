from __future__ import annotations

import hashlib
import json
import os
import tempfile
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from uwpath_data.models import Catalog


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json_bytes(value)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(payload)
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, path)


class RawSnapshotWriter:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def __call__(self, relative_path: str, value: Any) -> None:
        target = (self.root / relative_path).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError(f"Raw snapshot path escapes its root: {relative_path}")
        write_json(target, value)


def validate_catalog(value: dict[str, Any]) -> None:
    packaged_schema = resources.files("uwpath_data").joinpath("schema/catalog-v1.schema.json")
    if packaged_schema.is_file():
        schema = json.loads(packaged_schema.read_text())
    else:
        repository_schema = Path(__file__).parents[2] / "schema/catalog-v1.schema.json"
        schema = json.loads(repository_schema.read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def publish_catalog(catalog: Catalog, output_root: Path) -> dict[str, Any]:
    target = output_root / catalog.calendar.academic_year
    catalog_data = catalog.to_dict()
    validate_catalog(catalog_data)
    courses_data = catalog_data["courses"]
    programs_data = catalog_data["programs"]
    write_json(target / "catalog.json", catalog_data)
    write_json(target / "courses.json", courses_data)
    write_json(target / "programs.json", programs_data)

    files = {}
    for name, value in (
        ("catalog.json", catalog_data),
        ("courses.json", courses_data),
        ("programs.json", programs_data),
    ):
        payload = canonical_json_bytes(value)
        files[name] = {
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    manifest = {
        "schema_version": catalog.schema_version,
        "academic_year": catalog.calendar.academic_year,
        "generated_at": catalog.generated_at,
        "source": catalog.calendar.source,
        "source_id": catalog.calendar.source_id,
        "quality": catalog_data["quality"],
        "files": files,
    }
    write_json(target / "manifest.json", manifest)
    return manifest

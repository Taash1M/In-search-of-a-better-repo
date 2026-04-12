"""Load metadata from YAML files into Pydantic models."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from pbi_semantic_mcp.metadata.models import (
    ColumnMeta,
    DAXExample,
    DatasetMeta,
    MeasureMeta,
    RelationshipMeta,
    TableMeta,
)
from pbi_semantic_mcp.metadata.registry import MetadataRegistry

logger = logging.getLogger(__name__)


class MetadataLoader:
    """Load all metadata YAML files from the data directory."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def load(self) -> MetadataRegistry:
        """Load all datasets, glossary, and DAX examples into a registry."""
        registry = MetadataRegistry()

        # Load dataset inventory
        datasets_file = self._data_dir / "datasets.yaml"
        if datasets_file.exists():
            datasets = self._load_datasets(datasets_file)
            for ds in datasets:
                registry.add_dataset(ds)

        # Load per-stream metadata
        streams_dir = self._data_dir / "streams"
        if streams_dir.exists():
            for yaml_file in sorted(streams_dir.glob("*.yaml")):
                ds = self._load_stream_file(yaml_file)
                if ds:
                    registry.add_dataset(ds)

        # Load shared DAX examples
        examples_file = self._data_dir / "dax_examples.yaml"
        if examples_file.exists():
            examples = self._load_dax_examples(examples_file)
            registry.shared_dax_examples = examples

        # Load glossary
        glossary_file = self._data_dir / "glossary.yaml"
        if glossary_file.exists():
            registry.glossary = self._load_glossary(glossary_file)

        logger.info(
            "Loaded %d datasets, %d shared examples, %d glossary terms",
            len(registry.datasets),
            len(registry.shared_dax_examples),
            len(registry.glossary),
        )
        return registry

    def _load_datasets(self, path: Path) -> list[DatasetMeta]:
        """Load the dataset inventory file."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data or "datasets" not in data:
            return []

        results = []
        for entry in data["datasets"]:
            ds = DatasetMeta(
                id=entry.get("id", ""),
                name=entry.get("name", ""),
                description=entry.get("description", ""),
                workspace=entry.get("workspace", "prod"),
                stream=entry.get("stream", ""),
                refresh_schedule=entry.get("refresh_schedule", ""),
                owner=entry.get("owner", ""),
            )
            results.append(ds)
        return results

    def _load_stream_file(self, path: Path) -> DatasetMeta | None:
        """Load a per-stream YAML file with full table/column/measure metadata."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data:
            return None

        tables = []
        for tbl in data.get("tables", []):
            columns = [
                ColumnMeta(**col) for col in tbl.get("columns", [])
            ]
            measures = [
                MeasureMeta(**m) for m in tbl.get("measures", [])
            ]
            tables.append(TableMeta(
                name=tbl["name"],
                description=tbl.get("description", ""),
                columns=columns,
                measures=measures,
                row_count_estimate=tbl.get("row_count_estimate"),
                source_type=tbl.get("source_type", ""),
                refresh_schedule=tbl.get("refresh_schedule", ""),
            ))

        relationships = [
            RelationshipMeta(**r) for r in data.get("relationships", [])
        ]

        dax_examples = [
            DAXExample(**ex) for ex in data.get("dax_examples", [])
        ]

        return DatasetMeta(
            id=data.get("id", ""),
            name=data.get("name", path.stem),
            description=data.get("description", ""),
            workspace=data.get("workspace", "prod"),
            tables=tables,
            relationships=relationships,
            dax_examples=dax_examples,
            stream=data.get("stream", path.stem),
            refresh_schedule=data.get("refresh_schedule", ""),
            owner=data.get("owner", ""),
        )

    def _load_dax_examples(self, path: Path) -> list[DAXExample]:
        """Load shared DAX examples."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data or "examples" not in data:
            return []
        return [DAXExample(**ex) for ex in data["examples"]]

    def _load_glossary(self, path: Path) -> dict[str, str]:
        """Load business glossary (term → definition)."""
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not data or "terms" not in data:
            return {}
        return {t["term"]: t["definition"] for t in data["terms"] if "term" in t}

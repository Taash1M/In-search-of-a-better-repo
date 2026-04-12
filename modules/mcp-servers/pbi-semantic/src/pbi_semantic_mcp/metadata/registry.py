"""In-memory metadata registry with lookup and fuzzy search."""

from __future__ import annotations

from pbi_semantic_mcp.metadata.models import (
    ColumnMeta,
    DAXExample,
    DatasetMeta,
    MeasureMeta,
    TableMeta,
)


class MetadataRegistry:
    """Central registry for all PBI dataset metadata. Loaded once at startup."""

    def __init__(self) -> None:
        self._datasets: dict[str, DatasetMeta] = {}  # keyed by lowercase name
        self._datasets_by_id: dict[str, DatasetMeta] = {}
        self.shared_dax_examples: list[DAXExample] = []
        self.glossary: dict[str, str] = {}

    @property
    def datasets(self) -> list[DatasetMeta]:
        return list(self._datasets.values())

    def add_dataset(self, ds: DatasetMeta) -> None:
        """Add or update a dataset in the registry."""
        key = ds.name.lower()
        if key in self._datasets:
            # Merge: new metadata enriches existing
            existing = self._datasets[key]
            if ds.tables:
                existing.tables = ds.tables
            if ds.relationships:
                existing.relationships = ds.relationships
            if ds.dax_examples:
                existing.dax_examples = ds.dax_examples
            if ds.description and not existing.description:
                existing.description = ds.description
        else:
            self._datasets[key] = ds
        if ds.id:
            self._datasets_by_id[ds.id] = ds

    def get_dataset(self, name_or_id: str) -> DatasetMeta | None:
        """Look up a dataset by name (case-insensitive) or ID."""
        ds = self._datasets.get(name_or_id.lower())
        if ds:
            return ds
        return self._datasets_by_id.get(name_or_id)

    def get_table(self, dataset_name: str, table_name: str) -> TableMeta | None:
        """Look up a specific table within a dataset."""
        ds = self.get_dataset(dataset_name)
        if not ds:
            return None
        return ds.get_table(table_name)

    def search_datasets(self, query: str) -> list[DatasetMeta]:
        """Fuzzy search datasets by name, description, or stream."""
        q = query.lower()
        results = []
        for ds in self._datasets.values():
            score = 0
            if q in ds.name.lower():
                score += 3
            if q in ds.description.lower():
                score += 2
            if q in ds.stream.lower():
                score += 2
            if score > 0:
                results.append((score, ds))
        results.sort(key=lambda x: x[0], reverse=True)
        return [ds for _, ds in results]

    def search_fields(self, query: str, max_results: int = 20) -> list[dict]:
        """Search across all datasets for columns/measures matching a query.

        Returns list of dicts with dataset, table, column/measure name, type, description.
        """
        q = query.lower()
        hits: list[tuple[int, dict]] = []

        for ds in self._datasets.values():
            for table in ds.tables:
                for col in table.columns:
                    score = self._field_score(q, col.name, col.description, col.business_definition)
                    if score > 0:
                        hits.append((score, {
                            "dataset": ds.name,
                            "table": table.name,
                            "field": col.name,
                            "type": "column",
                            "data_type": col.data_type,
                            "description": col.description or col.business_definition,
                        }))
                for measure in table.measures:
                    score = self._field_score(q, measure.name, measure.description, "")
                    if score > 0:
                        hits.append((score, {
                            "dataset": ds.name,
                            "table": table.name,
                            "field": measure.name,
                            "type": "measure",
                            "data_type": "MEASURE",
                            "description": measure.description,
                        }))

        hits.sort(key=lambda x: x[0], reverse=True)
        return [h for _, h in hits[:max_results]]

    def get_dax_examples(self, dataset_name: str | None = None, category: str | None = None) -> list[DAXExample]:
        """Get DAX examples, optionally filtered by dataset or category."""
        examples: list[DAXExample] = list(self.shared_dax_examples)

        if dataset_name:
            ds = self.get_dataset(dataset_name)
            if ds:
                examples.extend(ds.dax_examples)
        else:
            for ds in self._datasets.values():
                examples.extend(ds.dax_examples)

        if category:
            cat = category.lower()
            examples = [ex for ex in examples if cat in ex.category.lower()]

        return examples

    @staticmethod
    def _field_score(query: str, name: str, description: str, business_def: str) -> int:
        """Score a field match (higher = better)."""
        score = 0
        name_lower = name.lower()
        if query == name_lower:
            score += 5  # exact match
        elif query in name_lower:
            score += 3
        if description and query in description.lower():
            score += 2
        if business_def and query in business_def.lower():
            score += 1
        return score

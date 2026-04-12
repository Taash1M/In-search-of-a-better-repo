"""Tests for metadata loading and registry operations."""

from pathlib import Path

from pbi_semantic_mcp.metadata.loader import MetadataLoader


def test_loader_finds_datasets(data_dir: Path):
    loader = MetadataLoader(data_dir)
    registry = loader.load()
    assert len(registry.datasets) > 0


def test_so_backlog_loaded(registry):
    ds = registry.get_dataset("SO Backlog")
    assert ds is not None
    assert ds.stream == "so_backlog"
    assert len(ds.tables) >= 6  # Fact + 5 dims


def test_so_backlog_has_measures(registry):
    ds = registry.get_dataset("SO Backlog")
    measures = ds.all_measures
    assert len(measures) >= 3
    names = [m.name for m in measures]
    assert "Total Backlog Value" in names


def test_so_backlog_relationships(registry):
    ds = registry.get_dataset("SO Backlog")
    assert len(ds.relationships) >= 5


def test_search_datasets(registry):
    results = registry.search_datasets("backlog")
    assert len(results) >= 1
    assert results[0].name == "SO Backlog"


def test_search_fields(registry):
    results = registry.search_fields("customer")
    assert len(results) > 0
    # Should find CustomerName, CustomerID, etc.
    field_names = [r["field"] for r in results]
    assert any("Customer" in f for f in field_names)


def test_glossary_loaded(registry):
    assert len(registry.glossary) > 0
    assert "SO Backlog" in registry.glossary


def test_dax_examples_loaded(registry):
    examples = registry.get_dax_examples()
    assert len(examples) > 0


def test_dax_examples_filter_by_category(registry):
    agg_examples = registry.get_dax_examples(category="aggregation")
    assert len(agg_examples) >= 1
    for ex in agg_examples:
        assert "aggregation" in ex.category.lower()

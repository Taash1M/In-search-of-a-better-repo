"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from pbi_semantic_mcp.config import Settings
from pbi_semantic_mcp.metadata.loader import MetadataLoader


@pytest.fixture
def settings() -> Settings:
    """Test settings with no real credentials."""
    return Settings(
        azure_tenant_id="test-tenant",
        azure_client_id="test-client",
        azure_client_secret="test-secret",
        pbi_default_workspace="dev",
    )


@pytest.fixture
def data_dir() -> Path:
    """Path to the package's data directory."""
    return Path(__file__).parent.parent / "src" / "pbi_semantic_mcp" / "data"


@pytest.fixture
def registry(data_dir: Path):
    """Loaded metadata registry from bootstrap YAML."""
    loader = MetadataLoader(data_dir)
    return loader.load()

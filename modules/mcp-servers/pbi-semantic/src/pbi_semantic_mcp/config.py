"""Configuration via Pydantic Settings — loads from .env or environment variables."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """MCP server settings. All values can be overridden via environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Azure AD Service Principal ────────────────────────────────────
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # ── Power BI Workspace IDs ────────────────────────────────────────
    pbi_workspace_prod: str = "a59d3713-6f5a-470e-833e-15bbf60e8c97"
    pbi_workspace_dev: str = "6fec84af-8245-4738-b317-f29326432ae3"
    pbi_workspace_qa: str = "7f77ddaf-78e7-471c-b104-9000eb5fd761"
    pbi_default_workspace: str = Field(default="prod", pattern=r"^(prod|dev|qa)$")

    # ── DAX Guardrails ────────────────────────────────────────────────
    dax_max_rows: int = 10_000
    dax_timeout_seconds: int = 120
    rate_limit_per_minute: int = 30

    # ── Transport ─────────────────────────────────────────────────────
    mcp_transport: str = Field(default="stdio", pattern=r"^(stdio|sse|streamable-http)$")
    mcp_port: int = 8080

    # ── Metadata ──────────────────────────────────────────────────────
    metadata_dir: str = ""  # Override to point at custom YAML dir

    @property
    def workspace_ids(self) -> dict[str, str]:
        """Map environment names to workspace IDs."""
        return {
            "prod": self.pbi_workspace_prod,
            "dev": self.pbi_workspace_dev,
            "qa": self.pbi_workspace_qa,
        }

    @property
    def default_workspace_id(self) -> str:
        """Resolve the active workspace ID."""
        return self.workspace_ids[self.pbi_default_workspace]

    @property
    def has_credentials(self) -> bool:
        """Check if Azure AD credentials are configured."""
        return bool(self.azure_tenant_id and self.azure_client_id and self.azure_client_secret)


def get_settings(**overrides: str) -> Settings:
    """Create a Settings instance, optionally overriding values."""
    return Settings(**overrides)

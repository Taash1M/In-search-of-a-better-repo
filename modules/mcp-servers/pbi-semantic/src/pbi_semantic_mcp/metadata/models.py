"""Pydantic models for PBI semantic model metadata."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ColumnMeta(BaseModel):
    """Metadata for a single column in a PBI table."""

    name: str
    data_type: str = ""  # STRING, INTEGER, DECIMAL, DATE, BOOLEAN, etc.
    description: str = ""
    is_key: bool = False  # PK or FK
    fk_table: str = ""  # Referenced table if FK
    fk_column: str = ""  # Referenced column if FK
    sample_values: list[str] = Field(default_factory=list)
    source_column: str = ""  # Original source column name
    business_definition: str = ""  # Extended business context


class MeasureMeta(BaseModel):
    """Metadata for a DAX measure."""

    name: str
    expression: str = ""  # DAX formula
    description: str = ""
    format_string: str = ""  # e.g., "$#,##0", "0.0%"
    folder: str = ""  # Display folder in PBI


class RelationshipMeta(BaseModel):
    """Metadata for a model relationship."""

    from_table: str
    from_column: str
    to_table: str
    to_column: str
    cardinality: str = "many-to-one"  # many-to-one, one-to-one, many-to-many
    cross_filter: str = "single"  # single, both
    is_active: bool = True


class TableMeta(BaseModel):
    """Metadata for a single table in a PBI dataset."""

    name: str
    description: str = ""
    columns: list[ColumnMeta] = Field(default_factory=list)
    measures: list[MeasureMeta] = Field(default_factory=list)
    row_count_estimate: int | None = None
    source_type: str = ""  # Gold view, DirectQuery, Import, etc.
    refresh_schedule: str = ""


class DAXExample(BaseModel):
    """A curated DAX query example."""

    question: str
    query: str
    explanation: str = ""
    category: str = ""  # e.g., "aggregation", "time-intelligence", "filtering"


class DatasetMeta(BaseModel):
    """Metadata for a complete PBI dataset/semantic model."""

    id: str  # PBI dataset ID
    name: str
    description: str = ""
    workspace: str = "prod"
    tables: list[TableMeta] = Field(default_factory=list)
    relationships: list[RelationshipMeta] = Field(default_factory=list)
    dax_examples: list[DAXExample] = Field(default_factory=list)
    stream: str = ""  # UBI business stream (SO Backlog, Revenue, GL, etc.)
    refresh_schedule: str = ""
    owner: str = ""

    @property
    def table_names(self) -> list[str]:
        return [t.name for t in self.tables]

    @property
    def all_measures(self) -> list[MeasureMeta]:
        return [m for t in self.tables for m in t.measures]

    def get_table(self, name: str) -> TableMeta | None:
        for t in self.tables:
            if t.name.lower() == name.lower():
                return t
        return None

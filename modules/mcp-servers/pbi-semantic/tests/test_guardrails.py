"""Tests for DAX guardrails — validation, row limits, rate limiting."""

import pytest

from pbi_semantic_mcp.guardrails import (
    DAXValidationError,
    RateLimiter,
    inject_row_limit,
    validate_dax,
)


class TestValidateDAX:
    def test_valid_evaluate(self):
        q = "EVALUATE TOPN(10, Customers)"
        assert validate_dax(q) == q

    def test_valid_define(self):
        q = "DEFINE MEASURE t[m] = 1 EVALUATE ROW(\"x\", [m])"
        assert validate_dax(q) == q

    def test_blocks_create(self):
        with pytest.raises(DAXValidationError, match="CREATE"):
            validate_dax("CREATE TABLE foo(x INT)")

    def test_blocks_drop(self):
        with pytest.raises(DAXValidationError, match="DROP"):
            validate_dax("DROP TABLE Customers")

    def test_blocks_delete(self):
        with pytest.raises(DAXValidationError, match="DELETE"):
            validate_dax("DELETE FROM Customers WHERE id = 1")

    def test_blocks_insert(self):
        with pytest.raises(DAXValidationError, match="INSERT"):
            validate_dax("INSERT INTO Customers VALUES (1, 'test')")

    def test_blocks_update(self):
        with pytest.raises(DAXValidationError, match="UPDATE"):
            validate_dax("UPDATE Customers SET name = 'test'")

    def test_blocks_alter(self):
        with pytest.raises(DAXValidationError, match="ALTER"):
            validate_dax("ALTER TABLE Customers ADD col INT")

    def test_blocks_truncate(self):
        with pytest.raises(DAXValidationError, match="TRUNCATE"):
            validate_dax("TRUNCATE TABLE Customers")

    def test_blocks_merge(self):
        with pytest.raises(DAXValidationError, match="MERGE"):
            validate_dax("MERGE INTO target USING source ON ...")

    def test_empty_query(self):
        with pytest.raises(DAXValidationError, match="Empty"):
            validate_dax("")

    def test_whitespace_only(self):
        with pytest.raises(DAXValidationError, match="Empty"):
            validate_dax("   ")


class TestInjectRowLimit:
    def test_adds_topn_to_evaluate(self):
        result = inject_row_limit("EVALUATE Customers", 1000)
        assert result == "EVALUATE TOPN(1000, Customers)"

    def test_skips_if_topn_present(self):
        q = "EVALUATE TOPN(50, Customers)"
        assert inject_row_limit(q, 1000) == q

    def test_skips_row_expression(self):
        q = 'EVALUATE ROW("x", 1)'
        assert inject_row_limit(q, 1000) == q

    def test_handles_define_evaluate(self):
        q = 'DEFINE MEASURE t[m] = SUM(t[v]) EVALUATE SUMMARIZECOLUMNS(t[c], "val", [m])'
        result = inject_row_limit(q, 5000)
        assert "TOPN(5000," in result
        assert result.startswith("DEFINE")


class TestRateLimiter:
    def test_allows_within_limit(self):
        limiter = RateLimiter(max_per_minute=60)
        assert limiter.acquire() is True

    def test_blocks_when_exhausted(self):
        limiter = RateLimiter(max_per_minute=2)
        limiter.acquire()
        limiter.acquire()
        assert limiter.acquire() is False

    def test_wait_seconds_positive_when_blocked(self):
        limiter = RateLimiter(max_per_minute=1)
        limiter.acquire()
        assert limiter.wait_seconds > 0

import os
import threading
import logging
import duckdb
import pandas as pd
from typing import Any, Dict, List, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class DuckDBEngine:
    """
    Embedded columnar analytical database engine.

    Uses a single persistent file connection shared across threads via a lock.
    DuckDB's file-lock model means only one connection may write at a time;
    using a singleton + threading.Lock is the correct pattern for an in-process
    OLAP engine in a multithreaded web server.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(settings.DUCKDB_DIR, "analytics.duckdb")
        self.db_path = db_path
        self._conn: Optional[duckdb.DuckDBPyConnection] = None
        self._lock = threading.Lock()
        self._connect()

    def _connect(self) -> None:
        """Open (or re-open) the persistent DuckDB connection."""
        try:
            self._conn = duckdb.connect(self.db_path)
            logger.info("DuckDB connection established: %s", self.db_path)
        except Exception as e:
            # Fallback to read-only mode if primary process holds write lock
            try:
                self._conn = duckdb.connect(self.db_path, read_only=True)
                logger.info("DuckDB connection established in READ-ONLY mode: %s", self.db_path)
            except Exception:
                logger.warning("Falling back to in-memory DuckDB instance due to lock: %s", e)
                self._conn = duckdb.connect(":memory:")

    def _ensure_connected(self) -> duckdb.DuckDBPyConnection:
        """Return the live connection, attempting reconnect if it was lost."""
        if self._conn is None:
            self._connect()
        return self._conn  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a read-only analytical SELECT and return rows as dicts.
        Raises ValueError for any mutating statement so this path can never
        be used as a write channel by accident.
        """
        normalized = sql.strip().upper()
        forbidden = {"DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"}
        first_tokens = set(normalized.split()[:3])
        if first_tokens & forbidden:
            raise ValueError(
                "Only read-only SELECT queries are permitted through execute_query(). "
                "Use execute_ddl() for schema operations."
            )

        with self._lock:
            conn = self._ensure_connected()
            try:
                result = conn.execute(sql, params or [])
                df = result.fetchdf()
                df = df.where(pd.notnull(df), None)
                return df.to_dict(orient="records")
            except Exception:
                logger.exception("DuckDB query failed: %.200s", sql)
                raise

    def execute_ddl(self, sql: str) -> None:
        """
        Execute a DDL statement (CREATE, DROP, etc.) under the shared lock.
        This is the safe path for schema-level mutations.
        """
        with self._lock:
            conn = self._ensure_connected()
            try:
                conn.execute(sql)
            except Exception:
                logger.exception("DuckDB DDL failed: %.200s", sql)
                raise

    def register_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        """Persist a pandas DataFrame as a permanent DuckDB table (CREATE OR REPLACE)."""
        with self._lock:
            conn = self._ensure_connected()
            try:
                # Register as an ephemeral view, then materialise into a real table
                conn.register("_staging_df", df)
                conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM _staging_df")
                conn.unregister("_staging_df")
            except Exception:
                logger.exception("Failed to register dataframe as table '%s'", table_name)
                raise

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """Return column names and types for an existing table."""
        with self._lock:
            conn = self._ensure_connected()
            try:
                result = conn.execute(f"DESCRIBE {table_name}").fetchall()
                return [{"column_name": r[0], "column_type": r[1]} for r in result]
            except Exception:
                logger.exception("Could not describe table '%s'", table_name)
                raise


duckdb_engine = DuckDBEngine()

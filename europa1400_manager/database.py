from __future__ import annotations

from typing import Type, TypeVar, cast

from europa1400_manager.models import (
    DatabaseElement,
    DatabaseTable,
    GameDistributionTable,
    GameDrmTable,
    GameEditionTable,
    GameExecutableTable,
    GameExecutableToMetadataTable,
    GameLanguageTable,
    GameVersionTable,
)
from europa1400_manager.utils import DatabaseUtils

TTable = TypeVar("TTable", bound=DatabaseTable)
TElement = TypeVar("TElement", bound=DatabaseElement)


class Database:
    """Database class that initializes once and provides access to table elements."""

    def __init__(self) -> None:
        self._tables: dict[Type[DatabaseTable], DatabaseTable] = {}
        self._initialized = False

    async def init(self) -> None:
        """Initialize the database by fetching all tables once."""
        if self._initialized:
            return

        # List of all table types to fetch
        table_types: list[Type[DatabaseTable]] = [
            GameLanguageTable,
            GameEditionTable,
            GameVersionTable,
            GameDistributionTable,
            GameDrmTable,
            GameExecutableTable,
            GameExecutableToMetadataTable,
        ]

        # Fetch all tables
        for table_type in table_types:
            try:
                table: DatabaseTable = await DatabaseUtils.fetch_table(table_type)
                self._tables[table_type] = table
            except Exception as e:
                print(f"Warning: Failed to fetch {table_type.__name__}: {e}")
                self._tables[table_type] = table_type(id="", name="", elements=[])

        self._initialized = True

    def get_table_elements(
        self, table_type: Type[TTable], element_type: Type[TElement]
    ) -> list[TElement]:
        """Get all elements of a specific type from a table."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call init() first.")

        table = self._tables.get(table_type)
        if table is None:
            return []

        return cast(list[TElement], table.elements)

    def get_table_element(
        self, element_id: str, table_type: Type[TTable], element_type: Type[TElement]
    ) -> TElement:
        """Get a specific element by ID from a table."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call init() first.")

        elements = self.get_table_elements(table_type, element_type)
        if not (
            element := next(
                (element for element in elements if element.id == element_id), None
            )
        ):
            raise ValueError(
                f"Element with ID {element_id} not found in table {table_type.__name__}."
            )
        return element

    def get_table(self, table_type: Type[TTable]) -> TTable:
        """Get a specific table by type."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call init() first.")

        return cast(TTable, self._tables[table_type])

    @property
    def is_initialized(self) -> bool:
        """Check if the database has been initialized."""
        return self._initialized

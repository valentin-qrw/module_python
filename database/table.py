from typing import Any, Dict, List, Union, Iterator
from .column import Column
from .row import Row

class Table:
    """
    Represents a table in a mini database.

    Attributes:
        name (str): The name of the table.
        columns (Dict[str, Column]): A dictionary mapping column names to Column objects.
        rows (List[Row]): A list of rows in the table.
        next_id (int): The ID to be assigned to the next inserted row.
    Methods:
        insert(row_data: Dict[str, Any]) -> Row
        get_row(index: int) -> Union[Row, None]
        get_by_id(row_id: int) -> Union[Row, None]
        update(row_id: int, row_data: Dict[str, Any]) -> Union[Row, None]
        delete(row_id: int) -> bool
        count(column_name: str) -> int
        sum(column_name: str) -> float
        avg(column_name: str) -> float
        __len__() -> int
        __iter__() -> Iterator[Row]
        __repr__() -> str
    """

    def __init__(self, name: str, columns: List[Column]):
        self.name = name
        self.columns = {column.name: column for column in columns}
        self.rows = []
        self.next_id = 1

    def insert(self, row_data: Dict[str, Any]) -> Row:
        row_data = row_data.copy()

        provided_id = row_data.get('id')
        if provided_id is not None:
            if not isinstance(provided_id, int):
                raise ValueError("ID must be an integer.")
            if self.get_by_id(provided_id) is not None:
                raise ValueError(f"Row with id {provided_id} already exists.")
            if provided_id >= self.next_id:
                self.next_id = provided_id + 1
        else:
            row_data['id'] = self.next_id
            self.next_id += 1

        for column_name, column in self.columns.items():
            value = row_data.get(column_name)
            if value is not None and not column.data_type.validate(value):
                raise ValueError(f"Invalid value for column {column_name}: {value}")

        row = Row(row_data)
        self.rows.append(row)
        return row

    def get_row(self, index: int) -> Union[Row, None]:
        return self.rows[index] if 0 <= index < len(self.rows) else None

    def get_by_id(self, row_id: int) -> Union[Row, None]:
        for row in self.rows:
            if row.data.get("id") == row_id:
                return row
        return None

    def get_column(self, column_name: str) -> Column:
        if column_name in self.columns:
            return self.columns[column_name]
        raise ValueError(f"Column {column_name} not found.")

    def update(self, row_id: int, row_data: Dict[str, Any]) -> Union[Row, None]:
        row = self.get_by_id(row_id)
        if row is None:
            raise ValueError(f"Row with id {row_id} not found.")

        row_data = row_data.copy()
        if 'id' in row_data:
            del row_data['id']

        for column_name, column in self.columns.items():
            value = row_data.get(column_name)
            if value is not None and not column.data_type.validate(value):
                raise ValueError(f"Invalid value for column {column_name}: {value}")

        row.data.update(row_data)
        return row

    def delete(self, row_id: int) -> bool:
        row = self.get_by_id(row_id)
        if row is None:
            return False
        self.rows.remove(row)
        return True

    def count(self, column_name: str) -> int:
        if column_name not in self.columns:
            raise KeyError(f"Column '{column_name}' does not exist.")
        return sum(1 for row in self.rows if row[column_name] is not None)

    def sum(self, column_name: str) -> float:
        if column_name not in self.columns:
            raise KeyError(f"Column '{column_name}' does not exist.")
        return sum(row[column_name] for row in self.rows if row[column_name] is not None)

    def avg(self, column_name: str) -> float:
        if column_name not in self.columns:
            raise KeyError(f"Column '{column_name}' does not exist.")
        values = [row[column_name] for row in self.rows if row[column_name] is not None]
        return sum(values) / len(values) if values else 0.0

    def __len__(self):
        return len(self.rows)

    def __iter__(self) -> Iterator[Row]:
        return iter(self.rows)

    def __repr__(self):
        return f"Table(name={self.name}, columns={list(self.columns.keys())}, rows={len(self.rows)})"


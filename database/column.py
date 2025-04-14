from typing import Any
from .datatypes import DataType

class Column:
    """
    Represents a column in a database table.
    """

    def __init__(self, name: str, data_type: DataType, nullable: bool = True):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable

    def validate(self, value: Any) -> bool:
        if value is None:
            return self.nullable
        return self.data_type.validate(value)

    def __repr__(self):
        return f"Column(name={self.name}, data_type={repr(self.data_type)}, nullable={self.nullable})"


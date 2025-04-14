from typing import List, Dict
import json
from .table import Table
from .column import Column
from .datatypes import IntegerType, StringType, BooleanType, DateType
from .row import Row


class Database:
    """
    A class representing a simple in-memory database with support for transactions and JSON persistence.
    """

    def __init__(self, name: str):
        self.name = name
        self.tables: Dict[str, Table] = {}
        self.transaction_in_progress = False
        self.initial_state = {}

    @classmethod
    def from_json(cls, filename: str):
        type_mapping = {
            "IntegerType": IntegerType,
            "StringType": StringType,
            "BooleanType": BooleanType,
            "DateType": DateType
        }

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        db = cls(data["name"])
        next_ids = data.get("next_ids", {})

        for table_name in data["tables"]:
            # Відновлення колонок
            columns = []
            for col in data["columns"][table_name]:
                col_type = type_mapping[col["type"]]()
                columns.append(Column(col["name"], col_type))

            table = Table(table_name, columns)
            db.tables[table_name] = table

            for row_data in data["tables"][table_name]:
                row = Row(row_data)
                table.rows.append(row)

            table.next_id = next_ids.get(table_name, 1)

        return db

    def save(self, filename: str):
        data = {
            "name": self.name,
            "tables": {},
            "columns": {},
            "next_ids": {}
        }

        for name, table in self.tables.items():
            data["tables"][name] = [row.data for row in table.rows]
            data["columns"][name] = [
                {"name": col.name, "type": type(col.data_type).__name__}
                for col in table.columns.values()
            ]
            data["next_ids"][name] = table.next_id

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_table(self, name: str, columns: List[Column]) -> Table:
        if name in self.tables:
            raise ValueError(f"Table '{name}' already exists.")
        table = Table(name, columns)
        self.tables[name] = table
        return table

    def drop_table(self, name: str):
        if name not in self.tables:
            raise ValueError(f"Table '{name}' does not exist.")
        del self.tables[name]

    def __enter__(self):
        if self.transaction_in_progress:
            raise ValueError("A transaction is already in progress.")

        self.initial_state = {
            name: (
                list(table.columns.values()),
                table.rows.copy(),
                table.next_id
            )
            for name, table in self.tables.items()
        }
        self.transaction_in_progress = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            for name, (columns, rows, next_id) in self.initial_state.items():
                table = Table(name, columns)
                table.rows = rows
                table.next_id = next_id
                self.tables[name] = table
            print("Transaction aborted.")
        else:
            print("Transaction committed.")
        self.transaction_in_progress = False
        return False

    def commit(self):
        if not self.transaction_in_progress:
            raise ValueError("No transaction in progress.")
        self.transaction_in_progress = False
        print("Transaction committed.")

    def rollback(self):
        if not self.transaction_in_progress:
            raise ValueError("No transaction in progress.")
        for name, (columns, rows, next_id) in self.initial_state.items():
            table = Table(name, columns)
            table.rows = rows
            table.next_id = next_id
            self.tables[name] = table
        self.transaction_in_progress = False
        print("Transaction rolled back.")

    # --- CRUD API ---

    def create(self, model_name: str, data: dict) -> dict:
        if model_name not in self.tables:
            columns = []
            for key, value in data.items():
                if isinstance(value, int):
                    dtype = IntegerType()
                elif isinstance(value, bool):
                    dtype = BooleanType()
                elif isinstance(value, str):
                    dtype = StringType()
                else:
                    dtype = StringType()
                columns.append(Column(key, dtype))
            self.create_table(model_name, columns)
        return self.tables[model_name].insert(data).data

    def get(self, model_name: str, obj_id: int) -> dict | None:
        table = self.tables.get(model_name)
        if not table:
            return None
        row = table.get_by_id(obj_id)
        return row.data if row else None

    def update(self, model_name: str, obj_id: int, data: dict) -> dict | None:
        table = self.tables.get(model_name)
        if not table:
            return None
        row = table.update(obj_id, data)
        return row.data if row else None

    def delete(self, model_name: str, obj_id: int) -> bool:
        table = self.tables.get(model_name)
        if not table:
            return False
        return table.delete(obj_id)

    def get_related_many(self, from_model: str, to_model: str, foreign_key: str, from_id: int) -> List[dict]:
        if to_model not in self.tables:
            return []
        table = self.tables[to_model]
        return [row.data for row in table.rows if row.data.get(foreign_key) == from_id]

    def add_many_to_many_relation(self, relation_table: str, from_id: int, to_id: int,
                                  from_key: str = "from_id", to_key: str = "to_id") -> dict:
        if relation_table not in self.tables:
            self.create_table(relation_table, [
                Column(from_key, IntegerType()),
                Column(to_key, IntegerType())
            ])
        return self.tables[relation_table].insert({
            from_key: from_id,
            to_key: to_id
        }).data

    def get_many_to_many_related(self, relation_table: str, from_key: str, to_key: str,
                                 from_id: int, target_model: str) -> List[dict]:
        if relation_table not in self.tables or target_model not in self.tables:
            return []

        related_ids = [
            row.data[to_key]
            for row in self.tables[relation_table].rows
            if row.data[from_key] == from_id
        ]

        return [
            row.data
            for row in self.tables[target_model].rows
            if row.data.get("id") in related_ids
        ]



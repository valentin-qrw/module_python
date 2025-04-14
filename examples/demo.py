from database.database import Database
from database.column import Column
from database.datatypes import IntegerType, StringType

# Створення бази даних "users_db"
db = Database("users_db")

# Створення таблиці "users"
users = db.create_table("users", [
    Column("id", IntegerType(), nullable=False),
    Column("name", StringType(50), nullable=False),
    Column("email", StringType(100), nullable=False)
])

# Додавання користувачів
users.insert({"id": 1, "name": "Alice", "email": "alice@example.com"})
users.insert({"id": 2, "name": "Bob", "email": "bob@example.com"})
users.insert({"id": 3, "name": "Charlie", "email": "charlie@example.com"})

# Використання транзакцій
users.begin_transaction()
users.insert({"id": 4, "name": "David", "email": "david@example.com"})
# users.rollback()  # Якщо потрібно скасувати транзакцію

# Агрегатні функції
print("Всього користувачів:", users.count())

# Збереження бази у файл
db.save("users_db.json")
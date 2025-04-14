import unittest
from unittest.mock import patch, MagicMock
import json
from database.database import Database
from database.table import Table
from database.column import Column
from database.datatypes import IntegerType, StringType

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Set up a sample database for testing"""
        self.db = Database("TestDB")
        columns = [
            Column("id", IntegerType()),
            Column("name", StringType())
        ]
        self.table = self.db.create_table("users", columns)

    def test_create_table(self):
        """Test table creation"""
        columns = [
            Column("id", IntegerType()),
            Column("name", StringType())
        ]
        table = self.db.create_table("customers", columns)
        self.assertIn("customers", self.db.tables)
        self.assertEqual(len(table.columns), 2)

    def test_create_table_exists(self):
        """Test creating a table that already exists"""
        columns = [
            Column("id", IntegerType()),
            Column("name", StringType())
        ]
        with self.assertRaises(ValueError):
            self.db.create_table("users", columns)

    def test_drop_table(self):
        """Test dropping a table"""
        self.db.drop_table("users")
        self.assertNotIn("users", self.db.tables)

    def test_drop_table_not_exists(self):
        """Test dropping a non-existent table"""
        with self.assertRaises(ValueError):
            self.db.drop_table("nonexistent_table")

    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.dump")
    def test_save(self, mock_json_dump, mock_open):
        """Test saving the database to a JSON file"""
        self.db.save("test_db.json")
        mock_open.assert_called_once_with("test_db.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.load")
    def test_from_json(self, mock_json_load, mock_open):
        """Test loading a database from a JSON file"""
        mock_json_load.return_value = {
            "name": "TestDB",
            "tables": {
                "users": [{"id": 1, "name": "Alice"}]
            },
            "columns": {
                "users": [
                    {"name": "id", "type": "IntegerType"},
                    {"name": "name", "type": "StringType"}
                ]
            }
        }
        db = Database.from_json("test_db.json")
        self.assertEqual(db.name, "TestDB")
        self.assertIn("users", db.tables)
        self.assertEqual(len(db.tables["users"].columns), 2)

    def test_transaction_commit(self):
        """Test committing a transaction"""
        with self.db as db:
            table = db.tables["users"]
            table.insert({"id": 1, "name": "Alice"})
            self.db.commit()
        self.assertEqual(len(self.db.tables["users"].rows), 1)

    def test_transaction_rollback(self):
        """Test rolling back a transaction"""
        with self.db as db:
            table = db.tables["users"]
            table.insert({"id": 1, "name": "Alice"})
            db.rollback()
        self.assertEqual(len(self.db.tables["users"].rows), 0)

    def test_transaction_in_progress(self):
        """Test that an error is raised if a transaction is already in progress"""
        with self.db as db:
            with self.assertRaises(ValueError):
                with self.db as db2:  # Trying to start another transaction
                    pass

    def test_crud_create(self):
        """Test creating a new record with dynamic model creation"""
        data = {"id": 1, "name": "Alice"}
        result = self.db.create("employees", data)
        self.assertEqual(result, data)
        self.assertIn("employees", self.db.tables)
        self.assertEqual(len(self.db.tables["employees"].rows), 1)

    def test_crud_get(self):
        """Test retrieving a record by ID"""
        self.db.create("users", {"id": 1, "name": "Alice"})
        result = self.db.get("users", 1)
        self.assertEqual(result, {"id": 1, "name": "Alice"})


    def test_crud_delete(self):
        """Test deleting a record by ID"""
        self.db.create("users", {"id": 1, "name": "Alice"})
        deleted = self.db.delete("users", 1)
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get("users", 1))


    def test_one_to_many_relationship(self):
        # Створюємо Users
        user = self.db.create("users", {"id": 1, "name": "Alice"})

        # Створюємо Posts, які мають user_id
        post1 = self.db.create("posts", {"id": 1, "title": "Post 1", "user_id": 1})
        post2 = self.db.create("posts", {"id": 2, "title": "Post 2", "user_id": 1})

        # Витягуємо всі пости, що належать користувачу
        posts_table = self.db.tables["posts"]
        related_posts = [row.data for row in posts_table.rows if row.data["user_id"] == 1]

        self.assertEqual(len(related_posts), 2)
        self.assertTrue(all(post["user_id"] == 1 for post in related_posts))

    def test_many_to_many_relationship(self):
        # Створюємо студентів і курси
        student = self.db.create("students", {"id": 1, "name": "Bob"})
        course1 = self.db.create("courses", {"id": 101, "title": "Math"})
        course2 = self.db.create("courses", {"id": 102, "title": "Physics"})

        # Створюємо таблицю зв’язку enrollments
        enrollment1 = self.db.create("enrollments", {"student_id": 1, "course_id": 101})
        enrollment2 = self.db.create("enrollments", {"student_id": 1, "course_id": 102})

        # Витягуємо всі курси, на які записаний студент
        enrollments_table = self.db.tables["enrollments"]
        enrolled_course_ids = [e.data["course_id"] for e in enrollments_table.rows if e.data["student_id"] == 1]

        courses_table = self.db.tables["courses"]
        enrolled_courses = [c.data for c in courses_table.rows if c.data["id"] in enrolled_course_ids]

        self.assertEqual(len(enrolled_courses), 2)
        self.assertSetEqual({course["id"] for course in enrolled_courses}, {101, 102})


if __name__ == "__main__":
    unittest.main()
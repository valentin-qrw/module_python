import unittest
from controllers.database_controller import switch_database
from controllers.user_controller import create_user, get_user, update_user, delete_user
from database.registry import DatabaseRegistry
from database.database import Database
from models.base_model import User
from models.base_model import BaseModelMeta

# Dummy BaseModel for switch_database testing
class DummyModel:
    db = None

    @classmethod
    def use_db(cls, db_name):
        if db_name == "invalid":
            raise ValueError("Invalid database")
        cls.db = db_name


# Dummy User model for user controller testing.
# This simulates a very simple in-memory user store.
class DummyUser:
    _store = {}
    _next_id = 1

    def __init__(self, **data):
        self.data = data.copy()

    def to_dict(self):
        return self.data

    @classmethod
    def reset(cls):
        cls._store = {}
        cls._next_id = 1

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Allows two types of calls:
         - With positional arguments: create(model_name, data)
         - With keyword arguments only: create(name=..., email=...)
        """
        if args:
            # Called as DummyUser.create(model_name, data)
            model_name = args[0]
            data = args[1] if len(args) > 1 else {}
        else:
            # Called with keyword arguments only
            model_name = "User"  # default model name (can be ignored)
            data = kwargs

        user_data = data.copy()
        user_data['id'] = cls._next_id
        cls._next_id += 1
        user = DummyUser(**user_data)
        cls._store[user_data['id']] = user
        # Return the dictionary representation rather than the instance
        return user.to_dict()

    @classmethod
    def get(cls, model_name, user_id):
        user = cls._store.get(user_id)
        if user:
            return user.to_dict()
        return None

    @classmethod
    def update(cls, model_name, user_id, data):
        user = cls._store.get(user_id)
        if not user:
            return None
        user.data.update(data)
        return user.to_dict()

    @classmethod
    def delete(cls, model_name, user_id):
        if user_id in cls._store:
            del cls._store[user_id]
            return True
        return False


class TestDatabaseController(unittest.TestCase):
    def setUp(self):
        default_db = Database("default")
        DatabaseRegistry.register("default", default_db)
        User._db_instance = default_db

        # Ensure DummyModel is registered in the registry before testing switch_database
        BaseModelMeta.registry["DummyModel"] = DummyModel

    def test_switch_database_success(self):
        response = switch_database("DummyModel", "TestDB")
        self.assertEqual(response, {"switched": True, "model": "DummyModel", "db": "TestDB"})
        self.assertEqual(DummyModel.db, "TestDB")

    def test_switch_database_invalid(self):
        """Test that switching to an invalid database returns an error."""
        response = switch_database("DummyModel", "invalid")
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Invalid database")
        self.assertIsNone(DummyModel.db)

    def test_switch_database_model_not_found(self):
        """Test that switching database for a non-existent model returns an error."""
        response = switch_database("NonExistentModel", "TestDB")
        self.assertIn("error", response)
        self.assertEqual(response["error"], "Model 'NonExistentModel' not found")


class TestUserController(unittest.TestCase):
    def setUp(self):
        # Reset the DummyUser store before each test.
        DummyUser.reset()

        User._db_instance = DummyUser

    def test_create_user(self):
        """Test that a new user is created successfully."""
        data = {"name": "Alice", "email": "alice@example.com"}
        user_dict = create_user(data)
        self.assertIn("id", user_dict)
        self.assertEqual(user_dict["name"], "Alice")
        self.assertEqual(user_dict["email"], "alice@example.com")

    def test_get_user_success(self):
        """Test retrieving an existing user."""
        # First, create a user.
        user = DummyUser.create(name="Bob", email="bob@example.com")
        user_dict = get_user(user["id"])
        self.assertEqual(user_dict, user)

    def test_get_user_not_found(self):
        """Test that getting a non-existent user returns an error."""
        response = get_user(999)
        self.assertEqual(response, {"error": "User not found"})

    def test_update_user_success(self):
        """Test that updating an existing user works."""
        user = DummyUser.create(name="Charlie", email="charlie@example.com")
        updated = update_user(user["id"], {"email": "new_charlie@example.com"})
        self.assertEqual(updated["email"], "new_charlie@example.com")
        self.assertEqual(updated["name"], "Charlie")

    def test_update_user_not_found(self):
        """Test that updating a non-existent user returns an error."""
        response = update_user(999, {"email": "ghost@example.com"})
        self.assertEqual(response, {"error": "User not found or update failed"})

    def test_delete_user_success(self):
        """Test that deleting an existing user returns success."""
        user = DummyUser.create(name="Dana", email="dana@example.com")
        response = delete_user(user["id"])
        self.assertEqual(response, {"deleted": True})
        self.assertEqual(get_user(user["id"]), {"error": "User not found"})

    def test_delete_user_not_found(self):
        """Test that deleting a non-existent user returns failure."""
        response = delete_user(999)
        self.assertEqual(response, {"deleted": False})


if __name__ == "__main__":
    unittest.main()
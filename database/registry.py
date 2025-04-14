from database.database import Database

class DatabaseRegistry:
    """Реєстр баз даних."""
    _databases = {}

    @classmethod
    def register(cls, name, db_instance):
        cls._databases[name] = db_instance

    @classmethod
    def get(cls, name):
        return cls._databases.get(name)

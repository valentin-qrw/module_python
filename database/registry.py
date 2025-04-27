class DatabaseRegistry:
    """Глобальний реєстр баз даних."""
    _databases = {}

    @classmethod
    def register(cls, name, db_instance):
        """Реєструє базу даних під заданим ім'ям."""
        cls._databases[name] = db_instance

    @classmethod
    def get(cls, name):
        """Повертає базу даних за ім'ям."""
        return cls._databases.get(name)

    @classmethod
    def list(cls):
        """Повертає список усіх зареєстрованих баз даних."""
        return list(cls._databases.keys())
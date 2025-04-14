from datetime import datetime

class DataType:
    """Base class for defining column data types."""

    def validate(self, value):
        """
        Base validation method (overridden by subclasses).

        Args:
            value (Any): The value to validate.

        Returns:
            bool: Always returns True (subclasses implement actual validation).
        """
        return True

    def __str__(self):
        """Returns the name of the data type."""
        return self.__class__.__name__


class IntegerType(DataType):
    """Represents an integer data type."""

    def validate(self, value):
        """
        Validates if the value is an integer or None.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is an integer or None, otherwise False.
        """
        return isinstance(value, int) or value is None


class StringType(DataType):
    """Represents a string data type with a maximum length."""

    def __init__(self, max_length=255):
        """
        Initializes a StringType instance.

        Args:
            max_length (int, optional): The maximum allowed length for the string. Defaults to 255.
        """
        self.max_length = max_length

    def validate(self, value):
        """
        Validates if the value is a string within the specified length.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is a valid string or None, otherwise False.
        """
        return isinstance(value, str) and len(value) <= self.max_length or value is None


class BooleanType(DataType):
    """Represents a boolean data type."""

    def validate(self, value):
        """
        Validates if the value is a boolean or None.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is a boolean or None, otherwise False.
        """
        return isinstance(value, bool) or value is None


class DateType(DataType):
    """Represents a date data type formatted as 'YYYY-MM-DD'."""

    def validate(self, value):
        """
        Validates if the value is a correctly formatted date string or None.

        Args:
            value (Any): The value to validate.

        Returns:
            bool: True if the value is a valid date string or None, otherwise False.
        """
        if value is None:
            return True
        if isinstance(value, str):
            try:
                datetime.strptime(value, "%Y-%m-%d")
                return True
            except ValueError:
                return False
        return False

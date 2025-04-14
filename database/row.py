class Row:
    """
    Represents a single row in a table.

    Attributes:
        data (dict): A dictionary representing the row data.
        id (int): The unique identifier of the row.
    """

    def __init__(self, data: dict, row_id: int = None):
        """
        Initializes a Row instance.

        Args:
            data (dict): The row's data.
            row_id (int, optional): The unique ID of the row. Defaults to None.
        """
        self.data = data
        if row_id is not None:
            self.data["id"] = row_id

    def update(self, new_data: dict):
        """
        Updates the row with new data.

        Args:
            new_data (dict): Dictionary of fields to update.
        """
        self.data.update(new_data)

    def __getitem__(self, key):
        """
        Allows dictionary-like access to row fields.
        """
        return self.data.get(key)

    def __setitem__(self, key, value):
        """
        Allows dictionary-like setting of row fields.
        """
        self.data[key] = value

    def __repr__(self):
        return f"Row({self.data})"

    def to_dict(self):
        """
        Returns the row as a dictionary.
        """
        return self.data.copy()


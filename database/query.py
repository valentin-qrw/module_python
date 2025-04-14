class SimpleQuery:
    """Provides a simple query system for filtering, selecting, and sorting table data."""

    def __init__(self, table):
        """
        Initializes a SimpleQuery instance.

        Args:
            table (Table): The table to query.
        """
        self.table = table
        self.selected_columns = None
        self.filter_conditions = []
        self.sort_column = None
        self.sort_ascending = True

    def select(self, columns):
        """
        Selects specific columns for the query.

        Args:
            columns (list[str]): List of column names to retrieve.

        Returns:
            SimpleQuery: The query instance for method chaining.
        """
        self.selected_columns = columns
        return self

    def where(self, column, operator, value):
        """
        Filters rows based on a condition.

        Args:
            column (str): The column name to filter on.
            operator (str): The comparison operator ('=', '>', '<').
            value (Any): The value to compare.

        Returns:
            SimpleQuery: The query instance for method chaining.
        """
        self.filter_conditions.append((column, operator, value))
        return self

    def order_by(self, column, ascending=True):
        """
        Sorts the results based on a column.

        Args:
            column (str): The column to sort by.
            ascending (bool, optional): Sort order, True for ascending, False for descending. Defaults to True.

        Returns:
            SimpleQuery: The query instance for method chaining.
        """
        self.sort_column = column
        self.sort_ascending = ascending
        return self

    def execute(self):
        """
        Executes the query and returns the filtered, sorted, and selected results.

        Returns:
            list[dict]: The list of rows matching the query.
        """
        results = list(self.table)

        # Apply filtering
        for column, operator, value in self.filter_conditions:
            if operator == "=":
                results = [row for row in results if row[column] == value]
            elif operator == ">":
                results = [row for row in results if row[column] > value]
            elif operator == "<":
                results = [row for row in results if row[column] < value]

        # Apply sorting
        if self.sort_column:
            results.sort(key=lambda r: r[self.sort_column], reverse=not self.sort_ascending)

        # Apply column selection
        if self.selected_columns:
            results = [{col: row[col] for col in self.selected_columns} for row in results]

        return results


class JoinedTable:
    """Performs an INNER JOIN between two tables based on a matching column."""

    def __init__(self, left_table, right_table, left_column, right_column):
        """
        Initializes a JoinedTable instance.

        Args:
            left_table (Table): The first table to join.
            right_table (Table): The second table to join.
            left_column (str): The column from the left table for joining.
            right_column (str): The column from the right table for joining.

        Raises:
            ValueError: If either column is not found in the corresponding table.
        """
        if left_column not in left_table.columns:
            raise ValueError(f"Column '{left_column}' not found in table '{left_table.name}'!")
        if right_column not in right_table.columns:
            raise ValueError(f"Column '{right_column}' not found in table '{right_table.name}'!")

        self.left_table = left_table
        self.right_table = right_table
        self.left_column = left_column
        self.right_column = right_column
        self.rows = self._inner_join()

    def _inner_join(self):
        """
        Performs an INNER JOIN between two tables based on matching values in the specified columns.

        Returns:
            list[dict]: A list of joined rows.
        """
        joined_rows = []
        right_index = {row[self.right_column]: row for row in self.right_table}

        for left_row in self.left_table:
            left_value = left_row[self.left_column]
            if left_value in right_index:
                right_row = right_index[left_value]
                joined_data = {**left_row.data, **{f"{k}_r": v for k, v in right_row.data.items()}}
                joined_rows.append(joined_data)

        return joined_rows

    def __iter__(self):
        """Allows iteration over the joined rows."""
        return iter(self.rows)

    def __len__(self):
        """Returns the number of joined rows."""
        return len(self.rows)

    def __repr__(self):
        """Returns a string representation of the joined table."""
        return f"JoinedTable({self.left_table.name} ⨝ {self.right_table.name} ON {self.left_column} = {self.right_column})"

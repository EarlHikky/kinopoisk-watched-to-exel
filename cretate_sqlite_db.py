import argparse
import sqlite3
import csv


# Функция для создания таблицы из CSV
def create_table_from_csv(cursor: sqlite3.Cursor, table_name: str, csv_file: str) -> None:
    """
    Creates a table in the SQLite database based on the provided CSV file.

    Args:
        cursor (sqlite3.Cursor): The cursor to execute SQL queries.
        table_name (str): The name of the table to be created.
        csv_file (str): The path to the CSV file containing data to populate the table.

    Returns:
        None
    """
    with open(csv_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{header} TEXT' for header in headers])})")

        for row in reader:
            cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in row])})", row)


def main(csv_file=None):
    if csv_file is None:
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('csv_file', help='path to csv file')
        args = parser.parse_args()
        csv_file = args.csv_file

    table_name = csv_file.split('-')[0].lower()

    conn = sqlite3.connect('kinopoisk.db')
    cursor = conn.cursor()

    create_table_from_csv(cursor, table_name, csv_file)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()

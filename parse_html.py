"""
This module contains functions that parse HTML fragments and save them to an Excel file.
"""

import datetime
import os
import re
import sys

from argparse import ArgumentParser
from pathlib import Path
from typing import Generator

from bs4 import BeautifulSoup
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from tqdm import tqdm


def extract_year_range(string: str) -> str | None:
    """
    Extracts the year or years from a string enclosed in parentheses.

    Args:
        string (str): Input string containing the year or years.

    Returns:
        str: Extracted year or years if found, None otherwise.
    """
    # Match a year in parentheses
    match = re.search(r'\(.*(?P<year>\d{4}).*\)', string)
    if match:
        # Extract and return the year
        year = match.group('year')
        return year
    else:
        # Match years in parentheses
        match = re.search(r'\((?P<years>.*\d{4}[ \-–0-9.]*)\)', string)
        if match:
            # Extract and return the years
            years = match.group('years')
            return years
        else:
            return None


def get_html_fragment(folder_name: str) -> Generator[str, None, None]:
    """
    Generator function that yields HTML fragments from files in the './html' directory.

    Yields:
        file object: HTML fragment file object
    """
    path_folder = Path(f'{folder_name}/html')
    for root, dirs, files in os.walk(path_folder):
        # Sort files based on the integer value of the filename without the '.html' extension
        files.sort(key=lambda x: int(x.replace('.html', '')))
        for file in files:
            with open(f'{os.path.join(root, file)}', 'r') as html_fragment:
                yield html_fragment


def parse_html(html_fragment: str, ws: Worksheet) -> None:
    """
    Parse the HTML fragment and extract film information to store in the worksheet.

    Args:
        html_fragment (str): The HTML fragment to parse.
        ws (Worksheet): The worksheet to store the film information.

    Returns:
        None
    """
    duration_data = ''
    year = ''
    duration = ''
    director = ''

    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_fragment, 'html.parser')

    # Find the list of films
    films_list = soup.find('ul', id='itemList').find_all('li')

    # Iterate over each film in the list
    for film in films_list:
        try:
            # Extract the title of the film
            title = film.find('div', class_='name_rating').text

            # Extract the year and duration information
            year_duration_element_data = film.find('span').text

            if year_duration_element_data:
                try:
                    duration_data = year_duration_element_data.split()[-2]
                    year = extract_year_range(year_duration_element_data)
                except IndexError:
                    pass

            # Determine the duration of the film
            if duration_data.isdigit():
                duration = duration_data

            # Extract the director information
            i_element = film.find('i')
            if i_element is not None:
                director = i_element.find('a').text
            else:
                try:
                    directors = film.find('div', class_='info').find_all('a', class_='lined')
                    director = ', '.join([_.text for _ in directors])
                except AttributeError:
                    pass

            # Append the film information to the worksheet
            ws.append([title, year, duration, director])

        except (IndexError, AttributeError, NameError) as e:
            print(e)
            sys.exit(1)


def count_files_in_folder(folder_name: str) -> int:
    """
    Counts the number of files in a given folder.

    Args:
        folder_name (str): The name of the folder to count the files in.

    Returns:
        int: The number of files in the folder.
    """
    folder_path = Path(f'{folder_name}/html')
    all_items = os.listdir(folder_path)
    only_files = [item for item in all_items if os.path.isfile(os.path.join(folder_path, item))]

    return len(only_files)


def main(folder_name: str = None) -> None:
    """
    Main function to process HTML fragments and save to an xlsx file.

    Args:
        folder_name (str): Name of the folder to save the xlsx file. Default is None.

    Returns:
        None
    """
    # Check if folder_name is provided, otherwise use the default folder name
    if folder_name is None:
        parser = ArgumentParser(description='')
        parser.add_argument('--folder_name', default='Watched', help='Folder Name for save html and xlsx file')
        folder_name = parser.parse_args().folder_name

    # Initialize a new Workbook and select the active worksheet
    wb = Workbook()
    ws: Worksheet = wb.active

    # Append the header row to the worksheet
    ws.append(['Название', 'Год', 'Длительность', 'Режиссёр'])

    # Get the current date
    today = str(datetime.date.today())

    file_count: int = count_files_in_folder(folder_name)

    # Process HTML fragments and parse them into the worksheet
    for html_fragment in tqdm(get_html_fragment(folder_name), total=file_count, desc="Processing HTML fragments",
                              leave=False):
        parse_html(html_fragment, ws)

    # Save the workbook with the specified folder name and current date
    wb.save(f'{folder_name}/{folder_name}-{today}.xlsx')


if __name__ == '__main__':
    main()

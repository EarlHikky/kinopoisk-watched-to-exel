import datetime
import os
import re
import sys

from bs4 import BeautifulSoup
import openpyxl
from tqdm import tqdm

from parse_html import get_html_fragment, extract_year_range, count_files_in_folder


def parse_html(html_fragment, ws):
    soup = BeautifulSoup(html_fragment, 'html.parser')
    films_list = soup.find('div', class_='profileFilmsList').find_all('div', class_='item')

    for film in films_list:
        try:
            film_info = film.find('div', class_='nameRus').text
            if 'сериал' in film_info:
                title = re.sub(r'\((\D*?)\d.*?\)', r'(\1)', film_info).replace(', )', ')')
            else:
                title_element_data = film_info.split()
                title = ' '.join(title_element_data[:-1])

            year = extract_year_range(film_info)

            duration_element_data = film.find('div', class_='rating').find_all('span')
            if len(duration_element_data) > 1:
                duration = duration_element_data[-1].text.strip('()')
            else:
                duration = None

            date_element = film.find('div', class_='date')
            if date_element is not None:
                date = date_element.text
            else:
                date = None

            ws.append([title, year, duration, date])

        except (IndexError, AttributeError, NameError) as e:
            print(e, 'in item:', film, sep='\n')
            sys.exit(1)


def main():
    today = str(datetime.date.today())
    folder_name = 'Watched'
    file_name = f'{folder_name}/{folder_name}-{today}.xlsx'

    if os.path.isfile(file_name):
        os.remove(file_name)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Название', 'Год', 'Длительность', 'Дата добавления'])

    file_count: int = count_files_in_folder(folder_name)

    for html_fragment in tqdm(get_html_fragment(folder_name), total=file_count, desc="Processing HTML fragments",
                              leave=False):
        parse_html(html_fragment, ws)
    wb.save(file_name)


if __name__ == '__main__':
    main()

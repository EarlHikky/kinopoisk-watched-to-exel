import datetime
import os
import re
import sys

from bs4 import BeautifulSoup
import openpyxl
from icecream import ic
from tqdm import tqdm

from parse_html import get_html_fragment, extract_year_range


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
            ic(film)
            ic(e)
            sys.exit(1)


def main():
    today = str(datetime.date.today())
    file_name = f'Watched-{today}.xlsx'

    if os.path.isfile(file_name):
        os.remove(file_name)
    else:
        pass
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Название', 'Год', 'Длительность', 'Дата добавления'])

    for html_fragment in tqdm(get_html_fragment('Watched'), desc="Processing HTML fragments"):
        parse_html(html_fragment, ws)
    wb.save(file_name)


if __name__ == '__main__':
    main()

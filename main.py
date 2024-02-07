from argparse import ArgumentParser

from save_html import main as save_html
from parse_html import main as parse_html
from parse_watched_html import main as parse_watched_html


if __name__ == '__main__':
    parser = ArgumentParser(description='')
    parser.add_argument('--user_id', help='User ID for Kinopoisk')
    parser.add_argument('--folder_id', help='Folder ID for Kinopoisk')
    parser.add_argument('--folder_name', help='Folder Name for save html and xlsx file')

    user_id = parser.parse_args().user_id
    folder_id = parser.parse_args().folder_id
    folder_name = parser.parse_args().folder_name

    save_html(user_id, folder_id, folder_name)

    if folder_name is None:
        parse_watched_html()
    else:
        parse_html(folder_name)


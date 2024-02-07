"""
This module contains a function that retrieves cookies from a JSON file.
It then writes the cookies dictionary to 'cookies.json'.
If 'cookies.txt' is not found, it prints an error message and exits the program.
"""

import re
import argparse
import sys
import json

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from bs4 import BeautifulSoup
from requests import Session, Response
from tqdm import tqdm


def save_html(filename: str, response: Response) -> None:
    """
    Saves the HTML content from the response to a file.

    Args:
        filename (str): The name of the file to save the HTML content to.
        response (Response): The response object containing the HTML content to be saved.

    Returns:
        None
    """
    with open(filename, 'w', encoding='utf8') as output_file:
        output_file.write(response.text)


def get_one_page(session: Session, cookies: dict, url: str, page: int) -> tuple[Response, int]:
    """
    A function that retrieves one page using the provided session, cookies, URL, and page number.

    Args:
        session (Session): The session to use for the GET request.
        cookies (dict): Cookies to be used in the request.
        url (str): The URL of the page to retrieve.
        page (int): The page number being retrieved.

    Returns:
        tuple[Response, int]: A tuple containing the response object and the page number.
    """
    response = session.get(url, cookies=cookies)
    response.raise_for_status()
    check_if_captcha(response)
    return response, page


def check_if_captcha(response) -> None:
    """
    A function that checks if the response is a captcha page.

    Args:
        response: The response object to check for captcha.

    Returns:
        None
    """
    if response.history or 'captcha' in response.url:
        print('Captcha!')
        sys.exit(1)


def make_cookies() -> dict:
    """
    This function reads data from 'cookies.txt' and creates a dictionary of cookies with key-value pairs.
    It then writes the cookies dictionary to 'cookies.json'.
    If 'cookies.txt' is not found, it prints an error message and exits the program.

    Returns:
        dict: A dictionary containing the cookies.
    """
    cookies = dict()
    try:
        with open('cookies.txt', 'r', encoding='utf8') as file:
            for line in file:
                k, v = line.split()[-2:]
                cookies[k] = v.strip('"')

        with open('cookies.json', 'w', encoding='utf8') as output_file:
            json.dump(cookies, output_file)

    except FileNotFoundError:
        print('cookies.txt not found!')
        sys.exit(1)

    return cookies


def get_cookies_from_file() -> dict:
    """
    Retrieves cookies from a JSON file. Returns a dictionary of cookies.

    Returns:
        dict: A dictionary containing the cookies.
    """
    try:
        with open('cookies.json', 'r', encoding='utf8') as cookies:
            return json.load(cookies)
    except FileNotFoundError:
        print('File cookies.json not found! Using cookies.txt ...')
        cookies = make_cookies()
        return cookies


def get_pages_count(session: Session, cookies: dict, url: str) -> int:
    """
    Calculates the number of pages available for the given URL.

    Args:
        session (Session): The session to use for the GET request.
        cookies (dict): Cookies to be used in the request.
        url (str): The base URL to retrieve the page count from.

    Returns:
        int: The number of pages available for the given URL.
    """
    response: Response = session.get(url + '1/', cookies=cookies)
    response.raise_for_status()
    check_if_captcha(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    nav: BeautifulSoup = soup.find('div', class_='navigator')
    pages_url: BeautifulSoup = nav.find('ul', class_='list').find_all('li')[-1].find('a')
    pages_count = int(re.search(r'page[/=](\d{1,3})/?', pages_url['href']).group(1))
    return pages_count


def get_base_url(user_id: str, folder_id: str) -> str:
    """
    Returns the base URL for the given user ID and folder ID.

    Args:
        user_id (str): The user ID for Kinopoisk.
        folder_id (str): The folder ID for Kinopoisk.

    Returns:
        str: The base URL for the given user ID and folder ID.
    """
    match (user_id, folder_id):
        case (user_id, folder_id) if user_id is not None and folder_id is not None:
            base_url = f'https://www.kinopoisk.ru/user/{user_id}/movies/list/type/{folder_id}/sort/name/vector/asc/page/'
        case (None, folder_id) if folder_id is not None:
            base_url = f'https://www.kinopoisk.ru/mykp/folders/{folder_id}/?sort=name'
        case (user_id, None) if user_id is not None:
            base_url = f'https://www.kinopoisk.ru/user/{user_id}/votes/list/ord/name/vs/novote/page/'
        case _:
            sys.exit('User ID or Folder ID not provided')
    return base_url


def make_session() -> Session:
    """
    Creates a session with custom headers.

    Returns:
        Session: The created session.
    """
    session = Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
    })
    return session


def main(user_id=None, folder_id=None, folder_name=None):
    """
    Define the main function that saves HTML from kinopoisk.ru to the html folder.
    It takes user_id, folder_id, and folder_name as input parameters.
    If user_id is not provided, it parses it using the argparse module.
    It creates a session with custom headers, defines the base URL based on user_id and folder_id combinations,
    retrieves necessary information, gets cookies from a file, calculates the number of pages,
    creates a path for the folder, concurrently fetches multiple pages, and saves the HTML for each page.
    Finally, it closes the session.
    """

    # Retrieve necessary information
    cookies: dict = get_cookies_from_file()
    user_id = cookies.get('uid')

    # Parse user_id if not provided
    if user_id is None:
        parser = argparse.ArgumentParser(description='Saves html from kinopoisk.ru to ./html folder')
        parser.add_argument('--user_id', help='User ID for Kinopoisk')
        parser.add_argument('--folder_id', help='Folder ID for Kinopoisk')
        parser.add_argument('--folder_name', help='Folder Name for save html and xlsx file')
        args = parser.parse_args()
        folder_id = args.folder_id
        folder_name = args.folder_name
        user_id = args.user_id

    # Set folder_name if not provided
    if folder_name is None:
        folder_name = 'Watched'

    # Create a session with custom headers
    session: Session = make_session()

    # Define the base URL based on user_id and folder_id combinations
    base_url: str = get_base_url(user_id, folder_id)

    # Calculate the number of pages
    pages_count: int = get_pages_count(url=base_url, session=session, cookies=cookies)

    # Create a path for the folder and a  folder
    folder_path = Path(f'{folder_name}/html')
    folder_path.mkdir(parents=True, exist_ok=True)

    # Concurrently fetch multiple pages
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(get_one_page, session, cookies, f'{base_url}{page}/', page)
            for page in range(1, pages_count + 1)
        ]

        # Display progress using tqdm
        for future in tqdm(as_completed(futures), total=pages_count, desc="Downloading pages", leave=False):
            try:
                response, page = future.result()  # Check if the future completed successfully
                save_html(f'{folder_path}/{page}.html', response)
            except Exception as e:
                print(f"Error fetching page {page}: {e}")

    # Close the session after completion
    session.close()


if __name__ == '__main__':
    main()

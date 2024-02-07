# Kinopoisk Watched to Excel

## Description
**Kinopoisk Watched to Excel** is a tool to export the list of movies you have watched on Kinopoisk to an Excel file. This allows you to easily create and save a comprehensive list of all the movies you've watched in a convenient spreadsheet format.

## Requirements
- Python 3.12
- [Poetry](https://python-poetry.org/) or [pip](https://pip.pypa.io/en/stable/)
- Necessary dependencies listed in `requirements.txt`

## Installation

### Using pip
1. Clone the repository:
    ```sh
    git clone https://github.com/EarlHikky/kinopoisk-watched-to-exel.git
    ```
2. Navigate to the project directory:
    ```sh
    cd kinopoisk-watched-to-exel
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

### Using Poetry
1. Clone the repository:
    ```sh
    git clone https://github.com/EarlHikky/kinopoisk-watched-to-exel.git
    ```
2. Navigate to the project directory:
    ```sh
    cd kinopoisk-watched-to-exel
    ```
3. Install the dependencies:
    ```sh
    poetry install
    ```

## Usage

### Preparing the Environment

Copy cookies to `cookies.txt` format like:
   
 ```plaintext
  key value
   ```

   **OR**  manually save the HTML in `./<Folder_name>/html/`

### Save and Parse

#### Arguments:
1. `--user_id` - Can be obtained from the browser's address bar.
2. `--folder_id` - Can be obtained from the browser's address bar.
3. `--folder_name` - Directory to save HTML and choose the source for parsing.

> If `--folder_name` is not specified, a folder named "Watched" is created by default.
> If `--user_id` is not specified, it will be taken from cookies." 

#### Save from 'Watched' and parse to '.xlsx' (if cookies exist)
```sh
python main.py --user_id 12345
```
A folder named "Watched" will be created to save the HTML, and a file "Watched.xlsx" will be generated. If you specify `--folder_name` during execution, a folder with the specified name will be created.

#### Save from 'Folder' by user id (if the folder is public or cookies exist) and parse to '.xlsx'
```sh
python main.py --user_id 12345 --folder_id 12345
```
A folder named "Watched" will be created to save the HTML, and a file "Watched.xlsx" will be generated if `--folder_name` is not specified during execution.

### Only Save to 'html'

#### Save from 'Watched' (if cookies exist)
```sh
python save_html.py --user_id 12345
```

#### Save from 'Folder' by user id (if the folder is public or cookies exist)
```sh
python save_html.py --user_id 12345 --folder_id 12345
```

### Parse to '.xlsx'

#### Parse if folder is not 'Watched'
```sh
python parse_html.py --folder_name 'Watched'
```

#### Parse if folder is 'Watched' (default)
```sh
python parse_watched_html.py
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.


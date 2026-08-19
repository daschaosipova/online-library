import json
import os
from urllib.parse import quote

import more_itertools
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server

SITE_DIR = "static"
BOOKS_PER_PAGE = 10
BOOKS_PER_ROW = 2

REDIRECT_PAGE = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={SITE_DIR}/index1.html">
    <title>Онлайн-библиотека</title>
  </head>
  <body>
    <p><a href="{SITE_DIR}/index1.html">Перейти к библиотеке</a></p>
  </body>
</html>
"""


def load_library():
    with open("meta_data.json", "r", encoding="utf-8") as meta_data:
        books_json = meta_data.read()
    library = json.loads(books_json)

    for book in library:
        if "img_src" in book and book["img_src"]:
            book["img_src"] = quote(book["img_src"], safe="/:")
        if "book_path" in book and book["book_path"]:
            book["book_path"] = quote(book["book_path"], safe="/:")
    return library


def get_template():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.get_template("template.html")


def render_catalog_pages(template, library):
    pages = list(more_itertools.chunked(library, BOOKS_PER_PAGE))
    total_pages = len(pages)

    for page_num, page_books in enumerate(pages, start=1):
        books_rows = list(more_itertools.chunked(page_books, BOOKS_PER_ROW))

        rendered_page = template.render(
            books=books_rows,
            current_page=page_num,
            total_pages=total_pages,
            has_previous=page_num > 1,
            has_next=page_num < total_pages,
        )

        file_path = os.path.join(SITE_DIR, f"index{page_num}.html")
        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)


def write_redirect_page():
    with open("index.html", "w", encoding="utf8") as file:
        file.write(REDIRECT_PAGE)


def on_reload():
    library = load_library()
    template = get_template()

    os.makedirs(SITE_DIR, exist_ok=True)

    render_catalog_pages(template, library)
    write_redirect_page()

    print("All pages rebuilt successfully")


def main():
    on_reload()

    server = Server()
    server.watch("template.html", on_reload)
    server.watch("meta_data.json", on_reload)
    server.serve(root=SITE_DIR, default_filename="index1.html")


if __name__ == "__main__":
    main()

import argparse
import json
import os
from functools import partial
from urllib.parse import quote

import more_itertools
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server

BOOKS_PER_PAGE = 10
BOOKS_PER_ROW = 2


def parse_args():
    parser = argparse.ArgumentParser(
        description="Собирает статический сайт онлайн-библиотеки"
    )
    parser.add_argument(
        "--meta-path",
        default=os.getenv("LIBRARY_META_PATH", "meta_data.json"),
        help="Путь к файлу с данными о книгах",
    )
    parser.add_argument(
        "--site-dir",
        default=os.getenv("LIBRARY_SITE_DIR", "pages"),
        help="Каталог для сгенерированных страниц",
    )
    return parser.parse_args()


def load_library(meta_path):
    with open(meta_path, "r", encoding="utf-8") as meta_data:
        library = json.load(meta_data)

    for book in library:
        if "img_src" in book and book["img_src"]:
            book["img_src"] = quote(book["img_src"], safe="/:")
        if "book_path" in book and book["book_path"]:
            book["book_path"] = quote(book["book_path"], safe="/:")
    return library


def get_template(template_name):
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env.get_template(template_name)


def render_catalog_pages(template, library, site_dir):
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

        file_path = os.path.join(site_dir, f"index{page_num}.html")
        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)


def write_redirect_page(site_dir):
    template = get_template("redirect.html")
    redirect_page = template.render(target_url=f"{site_dir}/index1.html")
    with open("index.html", "w", encoding="utf8") as file:
        file.write(redirect_page)


def on_reload(meta_path, site_dir):
    library = load_library(meta_path)
    template = get_template("template.html")

    os.makedirs(site_dir, exist_ok=True)

    render_catalog_pages(template, library, site_dir)
    write_redirect_page(site_dir)


def main():
    args = parse_args()
    reload_site = partial(on_reload, args.meta_path, args.site_dir)
    reload_site()

    server = Server()
    server.watch("template.html", reload_site)
    server.watch("redirect.html", reload_site)
    server.watch(args.meta_path, reload_site)
    server.serve(root=".", default_filename=f"{args.site_dir}/index1.html")


if __name__ == "__main__":
    main()

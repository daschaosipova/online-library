import json
import os
import more_itertools
from urllib.parse import quote
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    with open("meta_data.json", "r", encoding="utf-8") as meta_data:
        books_json = meta_data.read()
    library = json.loads(books_json)

    for book in library:
        if "img_src" in book:
            book["img_src"] = quote(book["img_src"])
        if "book_path" in book:
            book["book_path"] = quote(book["book_path"])

    os.makedirs("pages", exist_ok=True)
    
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    books_per_page = 10
    pages = list(more_itertools.chunked(library, books_per_page))
    total_pages = len(pages)

    for page_num, page_books in enumerate(pages, start=1):

        books_rows = list(more_itertools.chunked(page_books, 2))

        rendered_page = template.render(
            books=books_rows,
            current_page=page_num,
            total_pages=total_pages
        )

        file_path = os.path.join("pages", f"index{page_num}.html")
        
        with open(file_path, "w", encoding="utf8") as file:
            file.write(rendered_page)

    print("All pages rebuilt successfully")


def main():
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.watch('meta_data.json', on_reload)
    server.serve(root='pages', default_filename='index1.html')


if __name__ == "__main__":
    main()

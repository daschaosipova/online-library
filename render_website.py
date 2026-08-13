import json

from livereload import Server

from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    with open("meta_data.json", "r", encoding="utf-8") as meta_data:
        books_json = meta_data.read()
    books = json.loads(books_json)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

    rendered_page = template.render(
        books=books,
    )

    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)

    print("Site rebuilt")


def main():
    on_reload()

    server = Server()
    server.watch('template.html', on_reload)
    server.watch('meta_data.json', on_reload)
    server.serve(root='.')


if __name__ == "__main__":
    main()

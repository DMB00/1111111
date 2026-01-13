from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs
import mimetypes


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Обработка GET-запросов"""
        parsed_path = urlparse(self.path)

        # Если запрос к корню - отдаем главную страницу
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            with open('templates/index.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.wfile.write(html_content.encode('utf-8'))

        # Если запрос к контактам - отдаем страницу контактов
        elif parsed_path.path == '/contacts' or parsed_path.path == '/contacts.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            with open('templates/contacts.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.wfile.write(html_content.encode('utf-8'))

        # Если запрос к другим ресурсам (стили, скрипты)
        elif os.path.exists('.' + parsed_path.path):
            self.serve_static_file('.' + parsed_path.path)

        else:
            # Для любых других GET-запросов возвращаем страницу контактов
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            with open('templates/contacts.html', 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        """Обработка POST-запросов (дополнительное задание)"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        # Парсим данные в зависимости от типа контента
        content_type = self.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            data = json.loads(post_data.decode('utf-8'))
        elif 'application/x-www-form-urlencoded' in content_type:
            data = parse_qs(post_data.decode('utf-8'))
            # Преобразуем списки в строки
            data = {k: v[0] if len(v) == 1 else v for k, v in data.items()}
        else:
            data = {'raw_data': post_data.decode('utf-8')}

        # Выводим полученные данные в консоль
        print("\n" + "=" * 50)
        print("Получен POST-запрос:")
        print(f"Путь: {self.path}")
        print(f"Заголовки: {dict(self.headers)}")
        print("Данные от пользователя:")
        for key, value in data.items():
            print(f"  {key}: {value}")
        print("=" * 50 + "\n")

        # Отправляем ответ клиенту
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

        response = {
            'status': 'success',
            'message': 'Данные получены сервером',
            'received_data': data
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def serve_static_file(self, filepath):
        """Обслуживание статических файлов (CSS, JS, изображения)"""
        if os.path.exists(filepath):
            self.send_response(200)

            # Определяем MIME-тип файла
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type:
                self.send_header('Content-type', mime_type)
            else:
                self.send_header('Content-type', 'application/octet-stream')

            self.end_headers()

            with open(filepath, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")


def run_server(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    """Запуск сервера"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Сервер запущен на порту {port}")
    print(f"Откройте в браузере: http://localhost:{port}")
    print(f"Страница контактов: http://localhost:{port}/contacts")
    print("Для остановки сервера нажмите Ctrl+C")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")


if __name__ == '__main__':
    # Создаем необходимые директории
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Проверяем существование HTML-файлов
    if not os.path.exists('templates/index.html'):
        print("Внимание: Файл templates/index.html не найден!")
        print("Создайте HTML-файлы как показано в инструкции.")

    if not os.path.exists('templates/contacts.html'):
        print("Внимание: Файл templates/contacts.html не найден!")
        print("Создайте HTML-файлы как показано в инструкции.")

    # Запускаем сервер
    run_server(port=8000)

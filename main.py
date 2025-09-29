#!/usr/bin/env python3
"""
Главный модуль для демонстрации использования парсера с обходом защиты от ботов
"""

import sys
import time
import os
import sys
from dotenv import load_dotenv

# Добавляем директорию src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Загружаем переменные окружения из .env файла
load_dotenv()

from anti_bot_parser import AntiBotParser


def main():
    # Загружаем URL из .env файла
    url = os.getenv("URL")
    
    if not url:
        print("Ошибка: URL не найден в .env файле")
        sys.exit(1)
    
    # Инициализация парсера
    with AntiBotParser(base_url=url, cookies_file="cookies.json") as parser:
        print("Запуск парсера с обходом защиты от ботов...")

        # Парсинг URL
        html_content = parser.parse(url)

        # Проверка на блокировку по IP
        blocked = False
        data = {}
        if html_content:
            data = parser.extract_data(html_content)
            title = data.get('title', '').lower()
            text_content = data.get('text_content', '').lower()
            if ("доступ ограничен" in title) or ("доступ ограничен" in text_content) or ("проблема с ip" in title) or ("проблема с ip" in text_content):
                print("Обнаружена блокировка по IP! Пробуем сменить User-Agent и повторить попытку...")
                blocked = True

        # Если блокировка обнаружена — пробуем ещё раз с новым User-Agent
        if blocked or not html_content:
            from services.headers import get_custom_headers
            # Принудительно обновляем заголовки
            parser.session_cookies = {}  # Можно также сбросить cookies
            # Повторный парсинг
            html_content = parser.parse(url)
            if html_content:
                data = parser.extract_data(html_content)
                title = data.get('title', '').lower()
                text_content = data.get('text_content', '').lower()
                if ("доступ ограничен" in title) or ("доступ ограничен" in text_content) or ("проблема с ip" in title) or ("проблема с ip" in text_content):
                    print("Повторная попытка не удалась: сайт по-прежнему блокирует доступ.")
                    sys.exit(1)
            else:
                print("Не удалось спарсить контент даже после смены User-Agent.")
                sys.exit(1)

        print("Контент успешно спарсен!")
    # Печать результата в консоль
    print("\n--- Результат парсинга ---")
    print(f"URL: {url}")
    print(f"Заголовок: {data.get('title', 'N/A')}")
    print(f"Предпросмотр текста: {data.get('text_content', 'N/A')[:200]}...")
    print(f"Всего ссылок найдено: {data.get('total_links', 0)}")


    # Сохраняем результат в базу данных и Excel
    data_for_save = dict(data)
    data_for_save['url'] = url
    from save_results import save_to_sqlite, save_to_excel
    save_to_sqlite(data_for_save)
    save_to_excel(data_for_save)

    # Новый процессор: извлечение объектов и сохранение в БД
    from data_processor import process_html_and_save
    process_html_and_save(html_content, base_url=url)

    # Отправка данных в другой модуль (пример)
    parser.send_to_module(str(data), "data_processor")

    # Печатаем полный результат в консоль
    print("\n--- Полный результат ---")
    print(data)


if __name__ == "__main__":
    main()
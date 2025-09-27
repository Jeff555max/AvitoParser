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
        
        if html_content:
            print("Контент успешно спарсен!")
            
            # Извлечение данных
            data = parser.extract_data(html_content)
            
            # Печать результата в консоль
            print("\n--- Результат парсинга ---")
            print(f"URL: {url}")
            print(f"Заголовок: {data.get('title', 'N/A')}")
            print(f"Предпросмотр текста: {data.get('text_content', 'N/A')[:200]}...")
            print(f"Всего ссылок найдено: {data.get('total_links', 0)}")
            
            # Отправка данных в другой модуль (пример)
            parser.send_to_module(str(data), "data_processor")
            
            # Печатаем полный результат в консоль
            print("\n--- Полный результат ---")
            print(data)
        else:
            print("Не удалось спарсить контент")
            sys.exit(1)


if __name__ == "__main__":
    main()
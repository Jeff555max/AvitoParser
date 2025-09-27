#!/usr/bin/env python3
"""
Скрипт инициализации проекта для установки зависимостей и настройки окружения
"""

import subprocess
import sys
import os

def install_playwright_browsers():
    """Установка браузеров Playwright"""
    try:
        print("Установка браузеров Playwright...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        print("Браузеры Playwright успешно установлены!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка установки браузеров Playwright: {e}")
        sys.exit(1)

def install_dependencies():
    """Установка зависимостей проекта"""
    try:
        print("Установка зависимостей проекта...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Зависимости успешно установлены!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка установки зависимостей: {e}")
        sys.exit(1)

def main():
    print("Инициализация проекта AvitoParser...")
    
    # Установка зависимостей
    install_dependencies()
    
    # Установка браузеров Playwright
    install_playwright_browsers()
    
    print("Инициализация проекта завершена!")

if __name__ == "__main__":
    main()
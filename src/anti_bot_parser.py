import time
import json
import os
import sys
from typing import Optional, Dict, Any

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from curl_cffi import requests as curl_requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from base_parser import BaseParser
from services.headers import CUSTOM_HEADERS


class AntiBotParser(BaseParser):
    """Реализация парсера с обходом защиты от ботов с использованием curl-cffi и Playwright"""
    
    def __init__(self, base_url: str, cookies_file: str = "cookies.json"):
        super().__init__(base_url, cookies_file)
        self.playwright = None
        self.browser = None
        self.context = None
        # Прокси из переменной окружения
        self.proxy = os.getenv("PROXY_URL")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
    
    def init_browser(self) -> None:
        """Инициализация браузера Playwright для обхода Cloudflare с поддержкой прокси"""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            launch_args = {"headless": True}
            if self.proxy:
                # Playwright proxy format: {server: ..., username: ..., password: ...}
                from urllib.parse import urlparse
                proxy_url = urlparse(self.proxy)
                launch_args["proxy"] = {
                    "server": f"{proxy_url.scheme}://{proxy_url.hostname}:{proxy_url.port}"
                }
                if proxy_url.username and proxy_url.password:
                    launch_args["proxy"]["username"] = proxy_url.username
                    launch_args["proxy"]["password"] = proxy_url.password
            self.browser = self.playwright.chromium.launch(**launch_args)
            self.context = self.browser.new_context()
            # Загрузка cookies, если доступны
            if self.session_cookies:
                self.context.add_cookies(self.format_cookies_for_playwright())
    
    def close_browser(self) -> None:
        """Закрытие браузера Playwright"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def format_cookies_for_playwright(self) -> list:
        """Форматирование cookies для Playwright"""
        playwright_cookies = []
        for name, value in self.session_cookies.items():
            playwright_cookies.append({
                "name": name,
                "value": value,
                "domain": self.base_url.replace("https://", "").replace("http://", "").split("/")[0],
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": False
            })
        return playwright_cookies
    
    def extract_cookies_from_playwright(self, context) -> Dict[str, Any]:
        """Извлечение cookies из контекста Playwright"""
        cookies = context.cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        return cookie_dict
    
    def bypass_cloudflare_with_playwright(self, url: str) -> Optional[str]:
        """Обход защиты Cloudflare с использованием Playwright"""
        try:
            self.init_browser()
            
            # Создание новой страницы
            page = self.context.new_page()
            
            # Переход по URL
            print(f"Переход по адресу {url} с помощью Playwright...")
            response = page.goto(url, wait_until="networkidle")
            
            # Ожидание загрузки страницы и завершения проверки Cloudflare
            time.sleep(5)
            
            # Извлечение cookies
            cookies = self.extract_cookies_from_playwright(self.context)
            self.save_cookies(cookies)
            self.session_cookies = cookies
            
            # Получение содержимого страницы
            content = page.content()
            
            # Закрытие страницы
            page.close()
            
            return content
        except Exception as e:
            print(f"Ошибка обхода Cloudflare с помощью Playwright: {e}")
            return None
    
    def parse_with_curl(self, url: str) -> Optional[str]:
        """Парсинг URL с использованием curl-cffi с пользовательскими заголовками и поддержкой прокси"""
        try:
            print(f"Парсинг {url} с помощью curl-cffi...")
            kwargs = {
                "headers": CUSTOM_HEADERS,
                "cookies": self.session_cookies,
                "impersonate": "chrome110"
            }
            if self.proxy:
                kwargs["proxies"] = self.proxy
            response = curl_requests.get(url, **kwargs)
            # Обновление cookies
            if response.cookies:
                cookies_dict = dict(response.cookies)
                self.session_cookies.update(cookies_dict)
                self.save_cookies(self.session_cookies)
            return response.text
        except Exception as e:
            print(f"Ошибка парсинга с помощью curl-cffi: {e}")
            return None
    
    def parse(self, url: str) -> Optional[str]:
        """Парсинг URL с обходом защиты от ботов"""
        # Сначала пробуем с Playwright, так как у curl-cffi могут быть проблемы
        print("Использование Playwright в качестве основного парсера...")
        content = self.bypass_cloudflare_with_playwright(url)
        
        # Если это не удалось, пробуем curl-cffi как резервный вариант
        if not content:
            print("Playwright не удался, пробуем curl-cffi как резервный вариант...")
            content = self.parse_with_curl(url)
        
        return content
    
    def extract_data(self, html_content: str) -> Dict[str, Any]:
        """Извлечение данных из HTML-контента"""
        if not html_content:
            return {}
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Извлечение заголовка
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Без заголовка"
            
            # Извлечение всего текстового контента
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Извлечение ссылок
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            return {
                "title": title_text,
                "text_content": text_content[:1000],  # Ограничение текстового контента
                "links": links[:50],  # Ограничение ссылок
                "total_links": len(links)
            }
        except Exception as e:
            print(f"Ошибка извлечения данных: {e}")
            return {}
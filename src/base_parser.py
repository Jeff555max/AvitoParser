import json
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseParser(ABC):
    """Базовый класс парсера с возможностями обхода защиты от ботов"""
    
    def __init__(self, base_url: str, cookies_file: str = "cookies.json"):
        self.base_url = base_url
        self.cookies_file = cookies_file
        self.session_cookies = {}
        self.load_cookies()
    
    def load_cookies(self) -> None:
        """Загрузить cookies из файла, если он существует"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    self.session_cookies = json.load(f)
                print(f"Cookies загружены из {self.cookies_file}")
            except Exception as e:
                print(f"Ошибка при загрузке cookies: {e}")
                self.session_cookies = {}
        else:
            print(f"Файл cookies не найден по адресу {self.cookies_file}")
    
    def save_cookies(self, cookies: Dict[str, Any]) -> None:
        """Сохранить cookies в файл"""
        try:
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            print(f"Cookies сохранены в {self.cookies_file}")
        except Exception as e:
            print(f"Ошибка при сохранении cookies: {e}")
    
    @abstractmethod
    def parse(self, url: str) -> Optional[str]:
        """Абстрактный метод для парсинга URL"""
        pass
    
    def send_to_module(self, data: str, module_name: str) -> None:
        """Отправить спарсенные данные в другой модуль для обработки"""
        print(f"Отправка данных в модуль '{module_name}': {data[:100]}...")
        # Это будет реализовано в зависимости от требований конкретного модуля
        # Пока что просто выводим в консоль, как требуется
import random

# Пользовательские заголовки для запросов
# Замените этот словарь своими заголовками

def get_random_user_agent():
    """Получение случайного user agent из списка"""
    try:
        with open('services/user_agent_pc.txt', 'r') as f:
            user_agents = [line.strip() for line in f.readlines() if line.strip()]
        return random.choice(user_agents) if user_agents else 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    except Exception:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'

def get_custom_headers():
    """Получение пользовательских заголовков со случайным user agent"""
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': get_random_user_agent(),
    }

# Для обратной совместимости
CUSTOM_HEADERS = get_custom_headers()
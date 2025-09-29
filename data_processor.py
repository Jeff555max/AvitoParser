import sqlite3
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

def parse_objects_from_html(html: str, base_url: str = ""):  # base_url нужен для формирования абсолютных ссылок
    soup = BeautifulSoup(html, 'lxml')
    results = []
    for div in soup.find_all('div', class_='index-root'):
        obj = {}
        # title
        title_tag = div.find(['h3', 'h2', 'a'], recursive=True)
        obj['title'] = title_tag.get_text(strip=True) if title_tag else ''
        # price
        price_tag = div.find('meta', itemprop='price')
        if price_tag and price_tag.get('content'):
            obj['price'] = price_tag['content'] + ' ₽'
        else:
            price_text = div.get_text()
            price_match = re.search(r'(\d[\d\s]+)\s*₽', price_text)
            obj['price'] = price_match.group(0) if price_match else ''
        # bail
        bail_match = re.search(r'Залог\s*([\d\s]+\s*₽)', div.get_text())
        obj['bail'] = bail_match.group(0) if bail_match else ''
        # tax
        tax_match = re.search(r'Комиссия\s*\d+%?', div.get_text())
        obj['tax'] = tax_match.group(0) if tax_match else ''
        # services
        services_match = re.search(r'ЖКУ[^\n]+', div.get_text())
        obj['services'] = services_match.group(0) if services_match else ''
        # address
        address_tag = div.find('span', {'data-marker': 'item-address'})
        obj['address'] = address_tag.get_text(strip=True) if address_tag else ''
        # desc
        desc_tag = div.find('div', {'data-marker': 'item-description'})
        obj['desc'] = desc_tag.get_text(strip=True) if desc_tag else ''
        # images
        images = []
        for img_tag in div.find_all('img'):
            src = img_tag.get('src')
            if src and src.startswith('http'):
                images.append(src)
        obj['images'] = images
        # link
        link_tag = div.find('a', href=True)
        if link_tag:
            href = link_tag['href']
            if href.startswith('http'):
                obj['link'] = href
            else:
                obj['link'] = base_url.rstrip('/') + href
        else:
            obj['link'] = ''
        # Добавляем только если есть title и link
        if obj['title'] and obj['link']:
            results.append(obj)
    return results

def save_objects_to_sqlite(objects: List[Dict[str, Any]], db_path: str = "results.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            bail TEXT,
            tax TEXT,
            services TEXT,
            address TEXT,
            desc TEXT,
            images TEXT,
            link TEXT
        )
    ''')
    for obj in objects:
        c.execute('''
            INSERT INTO objects (title, price, bail, tax, services, address, desc, images, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj.get('title', ''),
            obj.get('price', ''),
            obj.get('bail', ''),
            obj.get('tax', ''),
            obj.get('services', ''),
            obj.get('address', ''),
            obj.get('desc', ''),
            ','.join(obj.get('images', [])),
            obj.get('link', '')
        ))
    conn.commit()
    conn.close()

def process_html_and_save(html: str, base_url: str = ""):
    objects = parse_objects_from_html(html, base_url)
    save_objects_to_sqlite(objects)
    print(f"Сохранено объектов: {len(objects)}")

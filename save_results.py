import sqlite3
import pandas as pd
from typing import Dict, Any
import os

def save_to_sqlite(data: Dict[str, Any], db_path: str = "results.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            title TEXT,
            text_content TEXT,
            total_links INTEGER
        )
    ''')
    c.execute('''
        INSERT INTO results (url, title, text_content, total_links) VALUES (?, ?, ?, ?)
    ''', (
        data.get('url', ''),
        data.get('title', ''),
        data.get('text_content', ''),
        data.get('total_links', 0)
    ))
    conn.commit()
    conn.close()

def save_to_excel(data: Dict[str, Any], excel_path: str = "results.xlsx"):
    # Если файл существует, читаем и добавляем новую строку
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path)
    else:
        df = pd.DataFrame(columns=["url", "title", "text_content", "total_links"])
    new_row = {
        "url": data.get('url', ''),
        "title": data.get('title', ''),
        "text_content": data.get('text_content', ''),
        "total_links": data.get('total_links', 0)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(excel_path, index=False)

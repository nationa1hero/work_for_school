import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Selenium и webdriver_manager для получения страницы
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Wand для конвертации SVG в PNG (ImageMagick должен быть установлен и настроен)
from wand.image import Image

# Определяем базовую директорию относительно текущего файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к файлу sql-data.sql (находится в School_Diplom/postgresql)
DUMP_FILE = os.path.join(BASE_DIR, "postgresql", "sql-data.sql")
# Базовый URL для страницы задачи
BASE_PROBLEM_URL = "https://math6-vpr.sdamgia.ru/problem?id="
# Базовый URL для формирования абсолютного пути к изображениям
BASE_URL = "https://math6-vpr.sdamgia.ru"


# --------------------------
# Часть 1. Извлечение задач из sql-data.sql
# --------------------------

def parse_insert_statements(file_path):
    r"""
    Читает файл sql-data.sql и извлекает блоки INSERT-запросов для таблицы backend_task.
    Ожидается, что запросы имеют вид:
    
      INSERT INTO public.backend_task (id, subject_id, text, answer, topic, type, level, number_of_points, original_id, image_name) VALUES
      (543, 1, 'Вычислите: −21+98:7.', '−7', 'Действия с отрицательными числами', 'Common', 1, 2, 9827, null),
      (723, 1, 'На рисунке изображён план комнаты. ...', 'от 400 до 490 сантиметров', 'Оценка размеров объектов на плане', 'Common', 2, 2, 1964, '723.png'),
      ...
      
    Функция возвращает список строк, содержащих данные внутри VALUES.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"INSERT INTO public\.backend_task\s*\(.*?\)\s*VALUES\s*(.*?);"
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    return matches

def split_rows(insert_values_str: str) -> list[str]:
    """
    Разбивает блок VALUES на отдельные кортежи, корректно
    игнорируя круглые скобки, запятые и переносы строк,
    находящиеся внутри одинарных кавычек.
    """
    rows = []
    current = []
    depth = 0          
    in_quote = False  
    escape = False     

    for ch in insert_values_str:
        
        if in_quote and ch == "\\" and not escape:
            escape = True
            current.append(ch)
            continue

        if ch == "'" and not escape:          
            in_quote = not in_quote
            current.append(ch)
            continue
        escape = False

        if ch == "(" and not in_quote:        
            if depth == 0:
                current.clear()
            else:
                current.append(ch)
            depth += 1
            continue

        if ch == ")" and not in_quote:        
            depth -= 1
            if depth == 0:
                rows.append("".join(current).strip())
                current.clear()
            else:
                current.append(ch)
            continue

        # обычный символ
        current.append(ch)

    return rows

def split_fields(row_str):
    r"""
    Разбивает строку записи на отдельные поля, не разделяя запятые внутри одинарных кавычек.
    """
    fields = re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", row_str)
    return [field.strip() for field in fields]
    
def extract_tasks(file_path):
    r"""
    Извлекает задачи из файла sql-data.sql.
    Для каждой записи извлекаются:
      - local_id (индекс 0)
      - original_id (индекс 8)
      - image_name (индекс 9)
    Запись обрабатывается, если image_name заполнено (не равно "null" и не равно "\N")
    и если original_id состоит только из цифр и больше 0.
    Возвращает список словарей с ключами: local_id, original_id, old_image_name.
    """
    tasks = []
    insert_blocks = parse_insert_statements(file_path)
    for block in insert_blocks:
        rows = split_rows(block)
        for row in rows:
            # print(row, sep='\n')
            fields = split_fields(row)
            if len(fields) < 10:
                continue
            local_id = fields[0].strip("'")
            original_id = fields[8].strip("'")  # Извлекаем original_id из поля с индексом 8
            image_name = fields[9].strip().strip("'")
            if image_name and image_name.lower() != "null" and image_name != "\\N" and original_id.isdigit() and int(original_id) > 0:
                tasks.append({
                    "local_id": local_id,
                    "original_id": original_id,
                    "old_image_name": image_name
                }) 
    return tasks
    

a = extract_tasks(DUMP_FILE)
print(len(a))
print()
for i in a:
    print(i['old_image_name'], sep='\t')

    

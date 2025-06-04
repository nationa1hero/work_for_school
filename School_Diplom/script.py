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

def split_rows(insert_values_str):
    r"""
    Разбивает строку с данными на отдельные записи.
    """
    rows = re.findall(r"\((.*?)\)", insert_values_str, re.DOTALL)
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

# --------------------------
# Часть 2. Получение HTML страницы через Selenium и извлечение URL изображения
# --------------------------

def get_page_source(url):
    r"""
    Запускает Chrome в headless-режиме с помощью Selenium, открывает страницу по URL и возвращает её HTML.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # При необходимости, укажите путь к исполняемому файлу Chrome:
    # chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    # Ждем 5 секунд для базовой загрузки страницы
    time.sleep(5)
    page_source = driver.page_source
    driver.quit()
    return page_source

def fetch_svg_url(original_id):
    r"""
    Формирует URL страницы задачи по original_id, получает HTML через Selenium,
    и извлекает URL изображения из элемента <img> внутри div.pbody, у которого src начинается с "/get_file?id=".
    Возвращает абсолютный URL (предположительно указывающий на SVG) или None, если элемент не найден.
    """
    url = BASE_PROBLEM_URL + original_id
    html = get_page_source(url)
    soup = BeautifulSoup(html, "html.parser")
    img_tag = soup.select_one("div.pbody img[src^='/get_file?id=']")
    if img_tag and img_tag.get("src"):
        svg_url = urljoin(BASE_URL, img_tag["src"])
        return svg_url
    else:
        print(f"Изображение не найдено на странице {url}")
        return None

# --------------------------
# Часть 3. Конвертация SVG в PNG и сохранение изображения
# --------------------------

def convert_svg_to_png(svg_url, output_filename):
    r"""
    Скачивает содержимое по svg_url (ожидается, что это SVG),
    конвертирует его в PNG с помощью Wand, и сохраняет результат в output_filename.
    """
    try:
        response = requests.get(svg_url)
        response.raise_for_status()
        svg_data = response.content
        with Image(blob=svg_data, format="svg") as img:
            img.format = "png"
            img.save(filename=output_filename)
        print(f"SVG успешно конвертирован и сохранён как {output_filename}")
    except Exception as e:
        print(f"Ошибка при конвертации SVG: {e}")

# --------------------------
# Часть 4. Основной процесс обработки задач
# --------------------------

def main():
    tasks = extract_tasks(DUMP_FILE)
    print(f"Найдено задач для обработки: {len(tasks)}")
    
    images_dir = os.path.join(BASE_DIR, "downloaded_images")
    os.makedirs(images_dir, exist_ok=True)
    
    results = []
    for task in tasks:
        original_id = task["original_id"]
        local_id = task["local_id"]
        print(f"Обработка задачи: original_id={original_id}, local_id={local_id}")
        
        svg_url = fetch_svg_url(original_id)
        if svg_url:
            image_save_path = os.path.join(images_dir, f"{local_id}.png")
            convert_svg_to_png(svg_url, image_save_path)
            new_image_name = f"{local_id}.png"
        else:
            new_image_name = ""
        
        results.append({
            "local_id": local_id,
            "original_id": original_id,
            "new_image_name": new_image_name
        })
    
    output_file = os.path.join(BASE_DIR, "parsed_tasks.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Парсинг завершён. Результаты сохранены в {output_file}.")

if __name__ == "__main__":
    main()

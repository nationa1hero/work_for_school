import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Selenium и webdriver_manager для получения страницы
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Wand для конвертации SVG в PNG (ImageMagick должен быть установлен и настроен)
from wand.image import Image

# Определяем базовую директорию относительно текущего файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Файл с id задач (по одному id на строку)
TASK_IDS_FILE = os.path.join(BASE_DIR, "task_ids.txt")

# Базовый URL для страницы задачи и для формирования абсолютного пути к изображениям
BASE_PROBLEM_URL = "https://math6-vpr.sdamgia.ru/problem?id="
BASE_URL = "https://math6-vpr.sdamgia.ru"

# --------------------------
# Часть 1. Извлечение задач из текстового документа
# --------------------------

def extract_tasks_from_file(file_path):
    """
    Читает текстовый документ, содержащий id задач (по одному id на строку),
    и возвращает список задач в виде словарей с ключами:
      - local_id
      - original_id
    Здесь предполагается, что в файле указаны id, используемые для формирования URL страницы.
    """
    tasks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            task_id = line.strip()
            if task_id:
                tasks.append({
                    "local_id": task_id,
                    "original_id": task_id
                })
    return tasks

# --------------------------
# Часть 2. Получение HTML страницы через Selenium и извлечение URL изображения
# --------------------------

def get_page_source(url):
    """
    Запускает Chrome в headless-режиме с помощью Selenium, открывает страницу по URL и возвращает её HTML.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)
    # Ждем несколько секунд для загрузки страницы
    time.sleep(5)
    page_source = driver.page_source
    driver.quit()
    return page_source

def fetch_svg_url(original_id):
    """
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
    """
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
    # Извлекаем задачи из текстового документа с id
    tasks = extract_tasks_from_file(TASK_IDS_FILE)
    print(f"Найдено задач для обработки: {len(tasks)}")
    
    # Создаем директорию для сохранения изображений, если ее еще нет
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
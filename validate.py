import re
import os
from pathlib import Path

def parse_filename(filename):
    """Парсит имя файла аниме-серии с улучшенной обработкой озвучки"""
    name = Path(filename).stem
    
    # Основные паттерны для разных форматов
    patterns = [
        # Формат: "12 серия Название [Озвучка Аниме | Окане].mp4"
        r"(?P<episode>\d+)\s*серия\s*(?P<title>.+?)\s*(?:\[(?P<dub_type>Озвучка\s*Аниме\s*[|]\s*Окане|Озвучка\s*Аниме|Окане|Рекаст|Редаб)\])?$",
        
        # Формат: "12 серия Название Озвучка Аниме | Окане.mp4"
        r"(?P<episode>\d+)\s*серия\s*(?P<title>.+?)\s*(?P<dub_type>Озвучка\s*Аниме\s*[|]\s*Окане|Озвучка\s*Аниме|Окане|Рекаст|Редаб)?$",
        
        # Формат: "12 серия Название (Редаб).mp4"
        r"(?P<episode>\d+)\s*серия\s*(?P<title>.+?)\s*[(\[](?P<dub_type>Рекаст|Редаб)[)\]]?$",
        
        # Формат: "Название - 12 [Окане].mp4"
        r"(?P<title>.+?)\s*-\s*(?P<episode>\d+)\s*(?:\[(?P<dub_type>Окане|Рекаст|Редаб)\])?$",
        
        # Формат: "12 Название Рекаст.mp4"
        r"(?P<episode>\d+)\s*(?P<title>.+?)\s*(?P<dub_type>Рекаст|Редаб|Окане)?$"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, name, re.IGNORECASE)
        if match:
            # Безопасное получение и обработка dub_type
            dub_type = match.groupdict().get("dub_type")
            if dub_type is not None:
                dub_type = dub_type.strip()
                if "Озвучка Аниме |" in dub_type or "Окан" in dub_type.lower():
                    dub_type = "Окане"
                elif "Озвучка Аниме" in dub_type:
                    dub_type = "Окане"
            else:
                # Автоматическое определение по ключевым словам
                if "рекаст" in name.lower():
                    dub_type = "Рекаст"
                elif "редаб" in name.lower():
                    dub_type = "Редаб"
                elif "окан" in name.lower():
                    dub_type = "Окане"
                else:
                    dub_type = "Стандартная"
            
            return {
                "episode": match.group("episode").zfill(2),
                "title": match.group("title").strip(" -[]()"),
                "dub_type": dub_type
            }
    
    return None

def scan_directory(directory, recursive=False):
    """Сканирует директорию и выводит отладочную информацию"""
    print(f"\nСканирую директорию: {directory}")  # Отладочная печать
    results = []
    for item in Path(directory).iterdir():
        print(f"Обрабатываю: {item.name}")  # Отладочная печать
        if item.is_file():
            parsed = parse_filename(item.name)
            if parsed:
                print(f"Найдено совпадение: {item.name} -> {parsed}")  # Отладочная печать
                results.append({
                    "file": item.name,
                    "path": str(item),
                    **parsed
                })
        elif recursive and item.is_dir():
            results.extend(scan_directory(item, recursive=True))
    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Парсер названий аниме-серий")
    parser.add_argument("directory", help="Директория для сканирования")
    parser.add_argument("-r", "--recursive", action="store_true", help="Рекурсивный поиск")
    parser.add_argument("-d", "--debug", action="store_true", help="Режим отладки")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Ошибка: '{args.directory}' не является директорией")
        exit(1)

    results = scan_directory(args.directory, args.recursive)

    if not results:
        print("\nНе найдено подходящих файлов. Проверьте:")
        print("1. Формат имен файлов (должен содержать номер серии)")
        print("2. Что файлы действительно существуют в указанной директории")
        print("3. Отладочный вывод выше для анализа проблем")
        exit(0)

    # Вывод в виде таблицы
    print(f"\nНайдено {len(results)} файлов:\n")
    print(f"{'Серия':<6} | {'Название':<40} | {'Озвучка':<20} | {'Файл'}")
    print("-" * 90)
    for item in results:
        print(f"{item['episode']:<6} | {item['title'][:40]:<40} | {item['dub_type']:<20} | {item['file']}")

    # Сохранение в CSV
    csv_path = os.path.join(args.directory, "anime_list.csv")
    import csv
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["episode", "title", "dub_type", "file", "path"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nРезультаты сохранены в {csv_path}")

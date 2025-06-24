import re
import os
from pathlib import Path

def parse_filename(filename):
    # Удаляем расширение файла (всё что после последней точки)
    name_without_ext = re.sub(r'\.[^.]*$', '', filename)
    
    # Обновлённое регулярное выражение:
    pattern = r"""
        ^
        (?:Серия\s*)?  # Опциональный префикс "Серия" 
        (?P<episode>\d+)
        \s*серия\s*
        (?P<title>.+?)  # Нежадное совпадение
        (?:\s*-\s*)?    # Опциональный дефис
        \s*
        (?P<dub_type>Рекаст|Редаб|Озвучка)?
        $
    """
    match = re.search(pattern, name_without_ext, re.VERBOSE | re.IGNORECASE)
    
    if match:
        return {
            "episode": match.group("episode"),
            "title": match.group("title").strip(),
            "dub_type": match.group("dub_type") or "Стандартная"
        }
    return None

def scan_directory(directory, recursive=False):
    results = []
    for item in Path(directory).iterdir():
        if item.is_file():
            parsed = parse_filename(item.name)
            if parsed:
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
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Ошибка: '{args.directory}' не является директорией")
        exit(1)

    results = scan_directory(args.directory, args.recursive)

    if not results:
        print("Не найдено подходящих файлов")
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

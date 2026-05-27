import os

def load_ignore_list(directory):
    """Читает файл fs_ignore.txt и возвращает список путей/имен."""
    ignore_file = os.path.join(directory, 'fs_ignore.txt')
    if os.path.exists(ignore_file):
        with open(ignore_file, 'r', encoding='utf-8') as f:
            # Читаем строки, удаляем пробелы и пустые строки
            return [line.strip() for line in f if line.strip()]
    return []

def should_ignore(path, ignore_list):
    """Проверяет, нужно ли игнорировать файл/папку."""
    name = os.path.basename(path)
    # Игнорируем сам файл настроек и всё из списка
    if name == 'fs_ignore.txt':
        return True
    return name in ignore_list

def list_files_recursive(directory, out_file, ignore_list):
    out_file.write(f"--- Список файлов в {os.path.abspath(directory)} ---\n\n")
    for root, dirs, files in os.walk(directory):
        # Исключаем папки из списка dirs, если они в игноре
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_list)]

        folder_rel_path = os.path.relpath(root, directory)
        display_name = folder_rel_path if folder_rel_path != "." else os.path.basename(os.path.abspath(directory))

        out_file.write(f"{display_name}:\n")
        for file in files:
            if not should_ignore(file, ignore_list):
                out_file.write(f"{display_name}: {file}\n")

        out_file.write("\n")

def find_and_show_content(directory, out_file, ignore_list):
    filenames_input = input("Введите пути или названия файлов через запятую: ")
    target_paths = [f.strip().replace('\\', '/') for f in filenames_input.split(',')]

    found_any = False
    out_file.write(f"--- Результаты поиска содержимого ---\n\n")

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_list)]

        for file in files:
            if should_ignore(file, ignore_list):
                continue

            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, directory).replace('\\', '/')

            if rel_path in target_paths or file in target_paths:
                found_any = True
                out_file.write(f"{rel_path}:\n")
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                        out_file.write(f.read() + "\n")
                except Exception as e:
                    out_file.write(f"[Ошибка чтения файла: {e}]\n")
                out_file.write("-" * 40 + "\n")

    if not found_any:
        out_file.write("Файлы с такими именами или путями не найдены.\n")

def main():
    target_path = input("Введите путь к основной папке (пусто для текущей): ").strip() or "."

    ignore_list = []
    use_ignore = input("Использовать fs_ignore.txt? (y/n): ").lower() == 'y'
    if use_ignore:
        ignore_list = load_ignore_list(target_path)
        print(f"Загружено игнорируемых элементов: {len(ignore_list)}")

    output_filename = input("Имя файла для сохранения результата: ").strip() or "output.txt"
    print("\n1 - Список всех файлов\n2 - Содержимое файлов")
    choice = input("Ваш выбор (1 или 2): ").strip()

    try:
        with open(output_filename, 'w', encoding='utf-8') as out_f:
            if choice == '1':
                list_files_recursive(target_path, out_f, ignore_list)
            elif choice == '2':
                find_and_show_content(target_path, out_f, ignore_list)
            print(f"Готово! Результат в {output_filename}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()

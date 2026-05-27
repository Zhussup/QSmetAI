import fitz  # PyMuPDF
import os

def pdf_to_images(pdf_path):
    # имя файла без расширения
    file_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # папка для сохранения
    output_folder = f"{file_name}_output"

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Создана папка: {output_folder}")

    # открываем PDF
    pdf_document = fitz.open(pdf_path)

    # обходим страницы
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)

        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        image_name = f"{file_name}_page{page_number + 1}.png"
        image_path = os.path.join(output_folder, image_name)

        pix.save(image_path)
        print(f"Сохранено: {image_name}")

    pdf_document.close()
    print("\nГотово! Все страницы сохранены.")


# -------- ЗАПУСК --------

pdf_file = r"/home/zhus/Desktop/QS/input/АР Школа 1500.pdf"

if os.path.exists(pdf_file):
    pdf_to_images(pdf_file)
else:
    print("Файл не найден. Проверь путь к PDF.")
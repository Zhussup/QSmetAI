# pip install pdf2image
from pdf2image import convert_from_path

def pdf_to_images(pdf_path, output_folder):
    images = convert_from_path(pdf_path, dpi=300) # 300 DPI для четкости чертежей
    for i, image in enumerate(images):
        image.save(f"{output_folder}/page_{i+1}.jpg", "JPEG")

# pdf_to_images("project.pdf", "dataset/images")
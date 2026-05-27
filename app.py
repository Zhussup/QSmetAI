import os
import uuid
import fitz  # PyMuPDF
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Detectron2 импорты
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2 import model_zoo

app = FastAPI(title="Document Segmentation Service")

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Монтируем статику для доступа к сохраненным изображениям
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# Категории из вашего датасета
CATEGORY_MAP = {
    1: "Table",
    2: "Notes",
    3: "Table With Blueprint",
    4: "Blueprint"
}

# Инициализация модели Detectron2
MODEL_WEIGHTS_PATH = os.path.join(BASE_DIR, "checkpoints", "model_final.pth") 

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4
cfg.MODEL.DEVICE = "cpu"  # Смените на "cuda", если запускаете на GPU

# Проверяем наличие весов
if os.path.exists(MODEL_WEIGHTS_PATH):
    cfg.MODEL.WEIGHTS = MODEL_WEIGHTS_PATH
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 
    predictor = DefaultPredictor(cfg)
    print("Модель успешно загружена с весами:", MODEL_WEIGHTS_PATH)
else:
    predictor = None
    print(f"ВНИМАНИЕ: Файл весов {MODEL_WEIGHTS_PATH} не найден. Работает в режиме заглушки.")


def process_pdf(pdf_path, run_id):
    """Конвертирует PDF в картинки и запускает детекцию объектов."""
    pdf_document = fitz.open(pdf_path)
    run_dir = os.path.join(OUTPUT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    results = []

    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        zoom = 2.0  # Увеличение разрешения для детектора
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        image_name = f"page_{page_number + 1}.png"
        image_path = os.path.join(run_dir, image_name)
        pix.save(image_path)
        
        detected_blocks = []
        if predictor is not None:
            img = cv2.imread(image_path)
            outputs = predictor(img)
            instances = outputs["instances"].to("cpu")
            
            boxes = instances.pred_boxes.tensor.numpy()
            scores = instances.scores.numpy()
            classes = instances.pred_classes.numpy()
            
            for i in range(len(boxes)):
                box = boxes[i]
                class_id = int(classes[i]) + 1
                category_name = CATEGORY_MAP.get(class_id, "Unknown")
                
                detected_blocks.append({
                    "box": [float(box[0]), float(box[1]), float(box[2]), float(box[3])],
                    "score": float(scores[i]),
                    "class_id": class_id,
                    "category": category_name
                })
        else:
            # Демонстрационная заглушка, если веса не найдены
            detected_blocks = [
                {
                    "box": [50.0, 50.0, 400.0, 250.0],
                    "score": 0.95,
                    "class_id": 1,
                    "category": "Table"
                },
                {
                    "box": [50.0, 300.0, 450.0, 600.0],
                    "score": 0.85,
                    "class_id": 2,
                    "category": "Notes"
                },
                {
                    "box": [500.0, 50.0, 1000.0, 800.0],
                    "score": 0.88,
                    "class_id": 4,
                    "category": "Blueprint"
                }
            ]
            
        results.append({
            "page": page_number + 1,
            "image_url": f"/output/{run_id}/{image_name}",
            "blocks": detected_blocks
        })
        
    pdf_document.close()
    return results


# Отдаем HTML-файл напрямую с диска, минуя Jinja2
@app.get("/")
async def read_root():
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Файл templates/index.html не найден")
    return FileResponse(html_path)


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF файлы.")
        
    run_id = str(uuid.uuid4())[:8]
    temp_pdf_path = os.path.join(OUTPUT_DIR, f"{run_id}_temp.pdf")
    
    with open(temp_pdf_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        data = process_pdf(temp_pdf_path, run_id)
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
            
    return JSONResponse(content={"run_id": run_id, "pages": data})
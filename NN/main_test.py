import torch
import os
import cv2
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.data.datasets import register_coco_instances
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo

def run_tests():
    print("--- ТЕСТ 1: Проверка GPU ---")
    print(f"PyTorch version: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"CUDA доступна: ДА, устройство: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA доступна: НЕТ (работаем на CPU, будет медленно!)")

    print("\n--- ТЕСТ 2: Проверка датасета ---")
    root_dir = "/home/zhus/Desktop/QS"
    json_path = os.path.join(root_dir, "dataset/annotations_coco.json")
    img_dir = os.path.join(root_dir, "dataset/images")

    # Проверка путей
    if not os.path.exists(json_path) or not os.path.exists(img_dir):
        print(f"ОШИБКА: Пути к данным не найдены!")
        print(f"JSON: {json_path} (Exists: {os.path.exists(json_path)})")
        print(f"IMG: {img_dir} (Exists: {os.path.exists(img_dir)})")
    else:
        # Безопасная регистрация (очистка, если имя уже занято)
        dataset_name = "docs_dataset"
        if dataset_name in DatasetCatalog.list():
            DatasetCatalog.remove(dataset_name)
            MetadataCatalog.remove(dataset_name)
        
        register_coco_instances(dataset_name, {}, json_path, img_dir)
        
        try:
            dataset_dicts = DatasetCatalog.get(dataset_name)
            print(f"Датасет зарегистрирован. Найдено картинок: {len(dataset_dicts)}")
            # Проверка, читается ли файл
            if len(dataset_dicts) > 0:
                first_img = dataset_dicts[0]['file_name']
                print(f"Первая картинка: {first_img}")
                if os.path.exists(first_img):
                    print("Проверка чтения файла: OK")
                else:
                    print(f"ВНИМАНИЕ: Файл {first_img} не найден по указанному пути!")
        except Exception as e:
            print(f"ОШИБКА в загрузке данных: {e}")

    print("\n--- ТЕСТ 3: Проверка модели ---")
    try:
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4
        
        # ДОБАВЬТЕ ЭТУ СТРОКУ:
        cfg.MODEL.DEVICE = "cpu" 
        
        cfg.MODEL.WEIGHTS = "" 
        
        from detectron2.modeling import build_model
        model = build_model(cfg)
        print("Архитектура модели успешно создана в памяти на CPU!")
    except Exception as e:
        print(f"ОШИБКА инициализации модели: {e}")

if __name__ == "__main__":
    run_tests()
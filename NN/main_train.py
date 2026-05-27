import os
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances

def train_model():
    # Пути
    root_dir = "/home/zhus/Desktop/QS"
    json_file = os.path.join(root_dir, "dataset/annotations_coco.json")
    img_dir = os.path.join(root_dir, "dataset/images")
    output_dir = os.path.join(root_dir, "checkpoints")
    
    os.makedirs(output_dir, exist_ok=True)

    # Регистрация (используем один набор для train и val из-за малого кол-ва данных)
    register_coco_instances("docs_dataset", {}, json_file, img_dir)

    cfg = get_cfg()
    cfg.MODEL.DEVICE = "cpu"
    
    cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"))
    
    cfg.DATASETS.TRAIN = ("docs_dataset",)
    cfg.DATASETS.TEST = () # Тест можно отключить, если данных очень мало
    cfg.DATALOADER.NUM_WORKERS = 2
    
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml")
    
    cfg.SOLVER.IMS_PER_BATCH = 1 
    cfg.SOLVER.BASE_LR = 0.00025
    cfg.SOLVER.MAX_ITER = 1000 # Достаточно для начала
    
    cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
    cfg.MODEL.ROI_HEADS.NUM_CLASSES = 4 # Согласно вашему XML
    cfg.OUTPUT_DIR = output_dir

    trainer = DefaultTrainer(cfg)
    trainer.resume_or_load(resume=False)
    trainer.train()

if __name__ == "__main__":
    train_model()
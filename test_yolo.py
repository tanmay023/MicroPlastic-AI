from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.train(
    data="dataset/yolo/data.yaml",
    epochs=1,
    imgsz=640,
    batch=8,
    device=0,
    workers=0,
    cache=False
)
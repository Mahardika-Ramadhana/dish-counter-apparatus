from ultralytics import YOLO

def main():
    print("Memulai training YOLOv8...")
    model = YOLO("yolov8n-seg.pt")
    
    results = model.train(
        data="/home/dika/projects/dish-counter-apparatus/dataset/data.yaml",
        epochs=50,
        imgsz=640,
        batch=2,
        device="cpu",
        project="/home/dika/projects/dish-counter-apparatus/runs",
        name="dica_2kelas"
    )
    print("Training Selesai! Model disimpan di runs/dica_2kelas/weights/best.pt")

if __name__ == "__main__":
    main()

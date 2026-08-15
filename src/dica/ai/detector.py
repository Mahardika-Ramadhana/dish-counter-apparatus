import os
from typing import Any

import cv2
import numpy as np

from dica.core import config

try:
    import tflite_runtime.interpreter as tflite

    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import ai_edge_litert.interpreter as tflite

        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False
        print(
            "Peringatan: tflite_runtime / ai_edge_litert tidak ditemukan. Menggunakan mode dummy."
        )

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Gagal memuat ultralytics. Alasan: {e}")
    YOLO_AVAILABLE = False


class ObjectDetector:
    def __init__(self):
        self.interpreter = None
        self.yolo_model = None
        self.input_details = None
        self.output_details = None
        self.labels = {0: "ayam", 1: "nasi"}
        self.is_dummy = True

    def load_model(self):
        is_prod = getattr(config, "ENVIRONMENT", "development") == "production"

        if not is_prod:
            if not YOLO_AVAILABLE:
                import tkinter.messagebox as mb

                try:
                    pass
                except Exception as e:
                    mb.showerror(
                        "Error AI",
                        f"Ultralytics gagal dimuat di Raspberry Pi!\n\nAlasan: {e}\n\nKemungkinan proses instalasi belum selesai atau gagal karena Raspberry Pi kehabisan memori.",
                    )

            if YOLO_AVAILABLE:
                print("INFO: Mencari model YOLO lokal untuk Development...")
                model_paths = [
                    "models/dica_2kelas.pt",
                    "models/yolov8n-seg.pt",
                    "models/yolov8n.pt",
                    "models/yolo11n-seg.pt"
                ]
                
                loaded = False
                for p in model_paths:
                    if os.path.exists(p):
                        print(f"Menggunakan model {p}...")
                        self.yolo_model = YOLO(p)
                        self.is_dummy = False
                        loaded = True
                        break
                
                if not loaded:
                    print("Model YOLO tidak ditemukan. Menggunakan mode dummy.")

        if not TFLITE_AVAILABLE:
            if getattr(config, "ENVIRONMENT", "development") == "production":
                raise RuntimeError(
                    "❌ ERROR: Library tflite_runtime tidak ditemukan! Aplikasi menolak menyala."
                )
            print("Mode dummy aktif untuk Detektor.")
            return

        if not os.path.exists(config.MODEL_PATH):
            if getattr(config, "ENVIRONMENT", "development") == "production":
                raise FileNotFoundError(
                    f"❌ ERROR: Model TFLite '{config.MODEL_PATH}' tidak ditemukan! Aplikasi menolak menyala tanpa AI."
                )
            print(f"Model {config.MODEL_PATH} tidak ditemukan. Menggunakan mode dummy.")
            return

        try:
            self.interpreter = tflite.Interpreter(model_path=config.MODEL_PATH)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            self.is_dummy = False
            print("Model TFLite berhasil dimuat.")
        except Exception as e:
            print(f"Gagal memuat model: {e}")

    def _calculate_iou(self, boxA, boxB):
        # Calculate intersection over union for two boxes [x1,y1,x2,y2]
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        if interArea == 0:
            return 0.0

        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

    def detect(self, frame: np.ndarray) -> list[dict[str, Any]]:
        self.last_annotated_frame = None
        self.has_occlusion = False

        if self.is_dummy or frame is None:
            return self._dummy_detection(frame)

        if self.yolo_model:
            return self._run_yolo_inference(frame)
        else:
            return self._run_tflite_inference(frame)

    def _run_yolo_inference(self, frame: np.ndarray) -> list[dict[str, Any]]:
        try:
            # Turunkan threshold agar AI bisa mendeteksi bentuk walau remang-remang
            results = self.yolo_model(frame, conf=0.15, verbose=False)
            detections = []

            if len(results) > 0:
                r = results[0]

                # Gunakan slot kelas 0 dan 1 agar tidak bentrok atau crash dengan sistem internal YOLO
                r.names[0] = "ayam"
                r.names[1] = "nasi"

                if r.boxes is not None:
                    for i in range(len(r.boxes)):
                        cls_id = int(r.boxes.cls[i])
                        class_name = "nasi" if cls_id == 1 else "ayam"

                        conf = float(r.boxes.conf[i])
                        x1, y1, x2, y2 = map(int, r.boxes.xyxy[i])
                        detections.append(
                            {
                                "class_id": cls_id,
                                "class_name": class_name,
                                "confidence": conf,
                                "bbox": [x1, y1, x2, y2],
                                "original_coco": "any",
                            }
                        )

                    # Cek Oklusi (Tumpang Tindih > 50%)
                    for i in range(len(detections)):
                        for j in range(i + 1, len(detections)):
                            if (
                                self._calculate_iou(detections[i]["bbox"], detections[j]["bbox"])
                                > 0.5
                            ):
                                self.has_occlusion = True

                # Plot dengan boxes=False dan labels=False agar tidak crash, lalu kita gambar labelnya sendiri
                self.last_annotated_frame = r.plot(boxes=False, labels=False)

                # Gambar label kustom secara manual
                for det in detections:
                    x1, y1, x2, y2 = det["bbox"]
                    label = f"{det['class_name'].upper()} {det['confidence']:.2f}"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    # Gambar kotak hitam untuk background teks
                    cv2.rectangle(
                        self.last_annotated_frame,
                        (x1, max(0, y1 - 25)),
                        (x1 + tw + 10, max(0, y1)),
                        (0, 0, 0),
                        -1,
                    )
                    # Tulis teks Nasi/Ayam
                    cv2.putText(
                        self.last_annotated_frame,
                        label,
                        (x1 + 5, max(0, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2,
                    )

            return detections

        except Exception as e:
            import traceback

            error_msg = str(e)[:100]
            print("DETECTOR ERROR:", traceback.format_exc())
            err_frame = frame.copy()
            cv2.putText(
                err_frame,
                "AI ERROR: " + error_msg,
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            self.last_annotated_frame = err_frame
            return []

    def _run_tflite_inference(self, frame: np.ndarray) -> list[dict[str, Any]]:
        img = cv2.resize(frame, config.INPUT_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        self.interpreter.set_tensor(self.input_details[0]["index"], img)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])

        return self._parse_yolov8_output(output_data, frame.shape)

    def _parse_yolov8_output(self, output_data, frame_shape):
        detections = []
        out = output_data[0]

        if out.shape[0] < out.shape[1]:
            out = out.transpose()

        boxes = out[:, :4]
        scores = out[:, 4:]

        class_ids = np.argmax(scores, axis=1)
        max_scores = np.max(scores, axis=1)

        mask = max_scores > config.CONFIDENCE_THRESHOLD

        filtered_boxes = boxes[mask]
        filtered_scores = max_scores[mask]
        filtered_class_ids = class_ids[mask]

        h, w = frame_shape[:2]

        for box, score, class_id in zip(filtered_boxes, filtered_scores, filtered_class_ids):
            xc, yc, bw, bh = box

            xc = xc / config.INPUT_SIZE[0] * w
            bw = bw / config.INPUT_SIZE[0] * w
            yc = yc / config.INPUT_SIZE[1] * h
            bh = bh / config.INPUT_SIZE[1] * h

            x1 = int(xc - bw / 2)
            y1 = int(yc - bh / 2)
            x2 = int(xc + bw / 2)
            y2 = int(yc + bh / 2)

            class_name = self.labels.get(int(class_id), "unknown")

            detections.append(
                {
                    "class_id": int(class_id),
                    "class_name": class_name,
                    "confidence": float(score),
                    "bbox": [x1, y1, x2, y2],
                }
            )

        return detections

    def _dummy_detection(self, frame) -> list[dict[str, Any]]:
        detections = []
        import random

        if random.random() > 0.5:
            items = list(self.labels.values())
            chosen = random.choice(items)
            detections.append(
                {
                    "class_id": list(self.labels.values()).index(chosen),
                    "class_name": chosen,
                    "confidence": random.uniform(0.6, 0.99),
                    "bbox": [50, 50, 200, 200],
                }
            )
        return detections

    def consolidate_max_count(
        self, det1: list[dict[str, Any]], det2: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Menggabungkan deteksi 2 kamera dengan logika Max Count per kelas untuk menghindari perhitungan ganda."""
        from collections import defaultdict

        count1 = defaultdict(list)
        for d in det1:
            count1[d["class_name"]].append(d)

        count2 = defaultdict(list)
        for d in det2:
            count2[d["class_name"]].append(d)

        final_detections = []
        all_classes = set(list(count1.keys()) + list(count2.keys()))

        for cls in all_classes:
            list1 = count1[cls]
            list2 = count2[cls]
            if len(list1) >= len(list2):
                final_detections.extend(list1)
            else:
                final_detections.extend(list2)

        return final_detections

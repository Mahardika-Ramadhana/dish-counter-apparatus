import os
from typing import Any

import cv2
import numpy as np

from dica.core import config

try:
    from ultralytics import YOLO

    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"DEBUG: Gagal memuat ultralytics. Alasan: {e}")
    YOLO_AVAILABLE = False


class ObjectDetector:
    def __init__(self):
        self.yolo_model = None
        self.labels = {
            0: "ayam_goreng",
            1: "ayam_rebus",
            2: "nasi_porsi",
            3: "sambal",
            4: "sayur",
            5: "tahu",
            6: "telur",
            7: "telur_balado",
            8: "tempe",
            9: "tempe_mendoan",
            10: "ikan_lele",
        }
        self.is_dummy = True
        self.last_annotated_frame = None
        self.has_occlusion = False

    def load_model(self):
        if not YOLO_AVAILABLE:
            print("❌ ERROR: Pustaka ultralytics tidak ditemukan! Aplikasi menolak menyala.")
            self.is_dummy = True
            return

        if not os.path.exists(config.MODEL_PATH):
            print(
                f"❌ ERROR: Model TFLite '{config.MODEL_PATH}' tidak ditemukan! Menggunakan dummy."
            )
            self.is_dummy = True
            return

        try:
            print(
                f"INFO: Memuat model ringan {config.MODEL_PATH} menggunakan Ultralytics (Segmentasi)..."
            )
            # Kita paksa task='segment' agar ultralytics bisa memecah hasil tflite menjadi polygon
            self.yolo_model = YOLO(config.MODEL_PATH, task="segment")
            self.is_dummy = False
            print("Model TFLite (Segmentasi) berhasil dimuat.")
        except Exception as e:
            print(f"Gagal memuat model: {e}")
            self.is_dummy = True

    def _calculate_iou(self, boxA, boxB):
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

        return self._run_yolo_inference(frame)

    def _run_yolo_inference(self, frame: np.ndarray) -> list[dict[str, Any]]:
        try:
            # Inference ringan di TFLite
            results = self.yolo_model(frame, conf=config.CONFIDENCE_THRESHOLD, verbose=False)
            detections = []

            if len(results) > 0:
                r = results[0]

                if r.boxes is not None:
                    for i in range(len(r.boxes)):
                        cls_id = int(r.boxes.cls[i])
                        raw_class_name = r.names[cls_id]

                        # Normalisasi format ke snake_case sesuai config.json
                        class_name = raw_class_name.lower().replace(" ", "_")
                        if class_name == "nasi":
                            class_name = "nasi_porsi"
                        elif class_name == "tahu_goreng":
                            class_name = "tahu"

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

                # Biarkan Ultralytics merender Polygon Masker yang cantik secara otomatis!
                self.last_annotated_frame = r.plot(boxes=True, labels=True)

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

import sys
import time

print("Checking ultralytics...")
try:
    import ultralytics
    print("YOLO is AVAILABLE")
except ImportError:
    print("YOLO NOT available")

print("Checking ai_edge_litert...")
try:
    import ai_edge_litert.interpreter as tflite
    print("TFLite is AVAILABLE")
except ImportError:
    print("TFLite NOT available")

import os
model_path = os.path.join(os.path.dirname(__file__), 'model.tflite')
print(f"model.tflite exists? {os.path.exists(model_path)}")

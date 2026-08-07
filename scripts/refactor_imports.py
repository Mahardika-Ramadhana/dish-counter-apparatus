import os
import re

import_map = {
    "config": "dica.core.config",
    "logger": "dica.core.logger",
    "state_machine": "dica.core.state_machine",
    "app": "dica.core.app",
    "main": "dica.core.app",
    
    "camera": "dica.hardware.camera",
    "loadcell": "dica.hardware.loadcell",
    "printer": "dica.hardware.printer",
    "display": "dica.hardware.display",
    
    "detector": "dica.ai.detector",
    
    "web_server": "dica.api.web_server",
    
    "qris": "dica.utils.qris",
    "wifi_manager": "dica.utils.wifi_manager",
    
    "database": "dica.db.database",
    "cloud_sync": "dica.db.cloud_sync"
}

def replace_in_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Simple regex for `import X` and `from X import Y`
    for old, new in import_map.items():
        # Handle `import config` -> `import dica.core.config as config`
        content = re.sub(rf'^import {old}$', f'import {new} as {old}', content, flags=re.MULTILINE)
        
        # Handle `from config import ...` -> `from dica.core.config import ...`
        content = re.sub(rf'^from {old} import ', f'from {new} import ', content, flags=re.MULTILINE)
        
        # Handle internal usages like `import config` but in tests
        content = re.sub(rf"patch\('{old}\.", f"patch('{new}.", content)

    # Some specific fixes
    content = content.replace("from main import App", "from dica.core.app import App")
    content = content.replace("patch('main.", "patch('dica.core.app.")
    
    # Config file path fix inside config.py (since it moved to src/dica/core/)
    if "config.py" in filepath:
        content = content.replace(
            "os.path.join(os.path.dirname(__file__), 'data', 'config.json')",
            "os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'config.json')"
        )
        content = content.replace(
            "models/yolo11n-seg.tflite",
            "../../../models/yolo11n-seg.tflite"
        )

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, _, files in os.walk('src/dica'):
    for file in files:
        if file.endswith('.py'):
            replace_in_file(os.path.join(root, file))

for root, _, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            replace_in_file(os.path.join(root, file))

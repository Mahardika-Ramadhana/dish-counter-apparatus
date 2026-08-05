#!/bin/bash
set -e

# Reset to the commit after PDF was uploaded (28721ce)
git reset --soft 28721ce
git reset HEAD .

# Group 1: Project setup
git add .gitignore requirements.txt run.sh config.py src/__init__.py scripts/check_env.py
git commit -m "chore: initial project setup and dependencies"

# Group 2: Database & Web Server
git add src/database.py src/web_server.py templates/ tests/unit/test_database.py src/logger.py data/
git commit -m "feat: implement sqlite database and local web dashboard"

# Group 3: Hardware & Networking
git add src/camera.py src/loadcell.py src/wifi_manager.py
git commit -m "feat: implement hardware interfaces (hx711, camera) and wifi manager"

# Group 4: AI / Vision
git add src/detector.py models/ yolov8n.pt yolov8n-seg.pt scripts/augment.py scripts/train_model.py tests/unit/test_detector.py
git commit -m "feat: implement yolov8 computer vision pipeline and custom dataset"

# Group 5: QRIS & App Logic
git add src/qris.py src/gui.py src/main.py tests/integration/test_fusion.py tests/e2e/test_gui_flow.py
git commit -m "feat: implement dynamic qris generation and main application gui"

# Group 6: Docs (everything else)
git add README.md Proposal/
git commit -m "docs: complete system architecture documentation and proposal"

# Push force to overwrite remote
git push --force origin main

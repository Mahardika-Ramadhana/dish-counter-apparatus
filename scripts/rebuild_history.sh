#!/bin/bash
set -e

echo "Resetting history to initial state..."
git reset --soft 28721ce
git reset HEAD .

echo "Group 1: Build & Toolchain"
git add Makefile requirements.txt Dockerfile docker-compose.yml .gitignore scripts/ LICENSE README.md
git commit -m "build: setup project toolchain, docker, and scripts"

echo "Group 2: Docs"
git add docs/
git commit -m "docs: add Gemastik proposal, backlog, and techstack documentation"

echo "Group 3: Assets & Data"
git add data/ assets/ models/
git commit -m "chore: initialize data schemas, models, and static assets"

echo "Group 4: Core Module"
git add src/dica/__init__.py src/dica/core/
git commit -m "feat(core): implement central state machine and configuration management"

echo "Group 5: Hardware Abstraction"
git add src/dica/hardware/
git commit -m "feat(hardware): integrate hardware abstractions for display, camera, loadcell, and printer"

echo "Group 6: AI & Vision"
git add src/dica/ai/
git commit -m "feat(ai): implement computer vision object detection pipeline"

echo "Group 7: DB & Utils"
git add src/dica/db/ src/dica/utils/
git commit -m "feat(data): implement local sqlite storage, utils, and cloud synchronization"

echo "Group 8: API & Web Server"
git add src/dica/api/
git commit -m "feat(api): implement REST API and web dashboard templates"

echo "Group 9: Testing Suite"
git add tests/
git commit -m "test: add comprehensive unit and integration test suites"

echo "Group 10: Final Polish"
git add .
git commit -m "refactor: finalize Domain-Driven Design repository layout"

echo "Force pushing to remote..."
git push --force origin main
echo "Done!"

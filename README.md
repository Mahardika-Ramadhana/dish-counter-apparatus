# Dish Counter Apparatus (DICA)

DICA is an automated, edge-computing point-of-sale (POS) system engineered for high-throughput, unstructured food servicing environments. It utilizes a rule-based sensor fusion architecture combining stereoscopic vision AI (YOLO11n-seg) and precision load cell telemetry to deliver high-accuracy, real-time transaction automated validation.

## Architecture Overview

- **Vision Intelligence:** Powered by YOLO11 Nano Segmentation (State-of-the-Art, 2.8M parameters) exported via TFLite for CPU-optimized inference.
- **Stereo Vision:** Dual 60-degree camera arrays to mitigate visual occlusion of unstructured overlapping items.
- **Hardware Telemetry:** Real-time mass verification using an HX711-amplified 5kg load cell.
- **State Management:** Decoupled `StateMachine` orchestration for IDLE, PROCESSING, VALIDATION, and PAYMENT states.
- **Edge-First Deployment:** Designed to operate in zero-connectivity environments on low-power ARM SBCs (e.g., Orange Pi 3 LTS) with asynchronous Supabase cloud synchronization.

## Prerequisites

- **OS:** Debian-based Linux (ARM64)
- **Runtime:** Python 3.10+
- **Package Manager:** `uv`
- **Hardware:**
  - 1x Quad-Core ARM Cortex-A53 SBC (Minimum 2GB RAM)
  - 2x Standard USB UVC Cameras
  - 1x 5Kg Aluminum Load Cell with HX711 Amplifier module
  - Thermal Printer (USB/Serial)

## Repository Structure (Domain-Driven)

```text
dish_counter/
  ├── data/                  # Offline SQLite DB & configs
  ├── models/                # YOLO/TFLite model files
  ├── src/dica/              # Main Package
  │   ├── core/              # Config, Logger, StateMachine, App
  │   ├── hardware/          # Camera, Loadcell, Printer, Display
  │   ├── ai/                # Object Detector
  │   ├── api/               # Flask Web Server & Cloud API
  │   ├── utils/             # QRIS generator, WiFi Manager
  │   └── db/                # Database and Cloud Sync
  ├── tests/                 # Unit & Integration Tests
  ├── Makefile               # Developer Experience scripts
  ├── run.sh                 # Entrypoint
  └── requirements.txt       # Dependencies
```

## System Installation

1. **Clone Repository:**
```bash
git clone https://github.com/Mahardika-Ramadhana/dish-counter-apparatus.git
cd dish-counter-apparatus
```

2. **Initialize Environment (via Make):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make setup
```

## Hardware Interfacing (GPIO)

Ensure the HX711 telemetry module is wired to the SBC GPIO header according to the following specifications:
- `VCC` -> 5V / 3.3V
- `GND` -> Ground
- `DT`  -> GPIO Pin 5
- `SCK` -> GPIO Pin 6

Thermal printer and cameras connect natively via USB.

## Developer Experience (Make)

A `Makefile` is provided to simplify developer workflows:
- `make setup`: Initialize `uv` virtual environment and install requirements.
- `make run`: Run the headless app (Web Server + AI Engine).
- `make test`: Run pytest suite.
- `make test-coverage`: Run pytest and output coverage metrics (Currently 81%+).
- `make lint`: Run flake8 linter.
- `make format`: Auto-format codebase using autopep8.

## API Documentation

The Headless Server exposes a local REST API (default `http://<IP>:5000`) for the web dashboard. All state-mutating endpoints (`POST`) are protected with Bearer Token Authorization.

**Auth Requirement:** `Authorization: Bearer <CONFIG_API_KEY>`

### Endpoints
1. `GET /api/stream`: MJPEG live video stream feed.
2. `GET /api/state`: Returns the current `StateMachine` status (IDLE/PROCESSING/VALIDATION/PAYMENT), recognized items, total price, and real-time loadcell weight.
3. `POST /api/validate`: Submit cashier validation of detected items (Requires Auth).
4. `POST /api/confirm`: Confirm payment and trigger receipt print & DB save (Requires Auth).
5. `POST /api/clear_transactions`: Truncate local SQLite database history (Requires Auth).
6. `POST /api/sync_cloud`: Manually trigger Supabase Cloud sync for offline data (Requires Auth).
7. `POST /api/tare`: Zero the load cell scale (Requires Auth).
8. `POST /api/toggle_auto`: Toggle auto-validation bypass state (Requires Auth).

## Execution

Initialize the unified service (Flask Backend and Asymmetric Multiprocessing Inference Engine):

```bash
make run
```

## System Constraints & Maintenance

- **Display Resolution:** The native graphical dashboard is best viewed at 800x480 resolution (5-inch touchscreen).
- **Load Cell Calibration:** Negative or erratic mass readings mandate physical orientation verification (load direction arrow) and subsequent tare recalibration via the Dashboard.
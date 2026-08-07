# Dish Counter Apparatus (DICA) 🥘🤖

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![Coverage](https://img.shields.io/badge/coverage-81%25-brightgreen)](#)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](#)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DICA is an automated, edge-computing point-of-sale (POS) system engineered for high-throughput, unstructured food servicing environments. It utilizes a rule-based sensor fusion architecture combining stereoscopic vision AI (YOLO11n-seg) and precision load cell telemetry to deliver high-accuracy, real-time transaction automated validation.

## Architecture Overview

- **Vision Intelligence:** Powered by YOLO11 Nano Segmentation (State-of-the-Art, 2.8M parameters) exported via TFLite for CPU-optimized inference.
- **Stereo Vision:** Dual 60-degree camera arrays to mitigate visual occlusion of unstructured overlapping items.
- **Hardware Telemetry:** Real-time mass verification using an HX711-amplified 5kg load cell.
- **State Management:** Decoupled `StateMachine` orchestration for IDLE, PROCESSING, VALIDATION, and PAYMENT states.
- **Flexible Deployment (Edge/Cloud):** Operates entirely offline on Edge devices (Orange Pi / Raspberry Pi) or acts as a Cloud AI Node processing payloads (`POST /api/remote_snapshot`) triggered from cheap microcontrollers (ESP32).

## Prerequisites

- **OS:** Debian-based Linux (ARM64 / x86_64)
- **Runtime:** Python 3.10+
- **Package Manager:** `uv`
- **Hardware (Edge Configuration):**
  - 1x Quad-Core ARM Cortex-A53 SBC (Minimum 2GB RAM)
  - 1x USB UVC Camera
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
  ├── tests/                 # Unit & Integration Tests (100% Core Coverage)
  ├── scripts/               # CI and Maintenance scripts
  ├── pyproject.toml         # Packaging, Linting, & Formatting Standards
  └── Makefile               # Developer Experience scripts
```

## System Installation

1. **Clone Repository:**
```bash
git clone https://github.com/Mahardika-Ramadhana/dish-counter-apparatus.git
cd dish-counter-apparatus
```

2. **Initialize Environment:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Hardware Interfacing (GPIO)

Ensure the HX711 telemetry module is wired to the SBC GPIO header according to the following specifications:
- `VCC` -> 5V / 3.3V
- `GND` -> Ground
- `DT`  -> GPIO Pin 5
- `SCK` -> GPIO Pin 6

Thermal printer and cameras connect natively via USB. Display defaults to `HEADLESS` unless configured via `data/config.json`.

## Developer Experience

This repository maintains strict engineering standards (Ruff, Pytest, MyPy).

- `make run`: Run the application (Web Server + AI Engine).
- `make test`: Run pytest suite.
- `make test-coverage`: Run pytest and output coverage metrics.
- `bash scripts/ci.sh`: Run local CI (Format, Lint, Test).

## API Documentation

The Headless Server exposes a local REST API (default `http://<IP>:5000`) for the web dashboard. All state-mutating endpoints (`POST`) are protected with Bearer Token Authorization.

**Auth Requirement:** `Authorization: Bearer <CONFIG_API_KEY>`

### Endpoints
1. `GET /api/status`: Returns the current `StateMachine` status (IDLE/PROCESSING/VALIDATION/PAYMENT), recognized items, total price, and real-time loadcell weight.
2. `GET /api/image`: MJPEG live video stream feed with bounding boxes.
3. `POST /api/remote_snapshot`: Push an image and weight payload to process AI inference remotely (Cloud AI Mode).
4. `POST /api/validate`: Submit cashier validation of detected items.
5. `POST /api/confirm`: Confirm payment and trigger receipt print & DB save.
6. `POST /api/clear_transactions`: Truncate local SQLite database history.
7. `POST /api/sync_cloud`: Manually trigger Supabase Cloud sync for offline data.
8. `POST /api/tare`: Zero the load cell scale.
9. `POST /api/toggle_auto`: Toggle auto-validation bypass state.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
# ADR 0001: Adoption of Domain-Driven Design for Project Architecture

**Date:** 2026-08-08
**Status:** Accepted

## Context

The initial iteration of the Dish Counter Apparatus (DICA) project was built as a monolithic script-based architecture with all Python files residing flatly inside a single `src/` directory. As the system expanded to support multiple hardware configurations (Edge OrangePi vs Cloud ESP32) and multiple output displays (Headless vs LCD vs TFT), the monolithic design led to:

1. **Tight Coupling:** Core transaction state machine was heavily intertwined with `main.py` threading loops.
2. **Circular Dependencies:** Components importing each other created fragility when initializing hardware.
3. **Difficult Onboarding:** New contributors could not easily locate where the AI logic ended and where the database sync logic began.

## Decision

We decided to restructure the entire repository following a strictly modular, Domain-Driven Design (DDD) layout.

The new package structure strictly enforces boundaries:
* `dica.core`: The brain. Contains the transaction state machine and config. Cannot import hardware or ai modules directly.
* `dica.hardware`: Device drivers (Camera, Loadcell, Display, Printer). Implements abstract interfaces (Adapter Pattern).
* `dica.ai`: The object detection pipeline. Entirely agnostic of how the image was captured.
* `dica.api`: The REST API and Web Dashboard. Consumes core and hardware but doesn't dictate business logic.
* `dica.db`: Persistence and Cloud Synchronization.
* `dica.utils`: Helper modules (Wifi, QRIS).

## Consequences

**Positive:**
- **High Cohesion & Low Coupling:** Hardware logic is fully abstracted. Adding a new display type (e.g., e-Ink) only requires implementing `BaseDisplay` inside `hardware/display.py`.
- **Testability:** Mocking becomes trivial. `make test` now isolates unit tests per domain cleanly, significantly increasing test reliability and allowing us to achieve >80% coverage.
- **Enterprise-Grade Readiness:** The project structure is now on par with world-class open-source Python repositories, facilitating easier onboarding for community contributors.

**Negative:**
- Imports became slightly more verbose (`from dica.core.config import ...` rather than `import config`).
- Requires strict adherence to dependency direction (e.g., `core` should not depend on `api`) which might require enforcing via linters in the future.

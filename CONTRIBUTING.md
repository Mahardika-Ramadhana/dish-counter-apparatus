# Contributing to Dish Counter Apparatus (DICA)

First off, thank you for considering contributing to DICA! It's people like you that make open-source software such a great community to learn, inspire, and create.

## 1. Local Development Setup

To ensure consistency and ease of onboarding, this project uses `uv` for dependency management.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mahardika-Ramadhana/dish-counter-apparatus.git
   cd dish-counter-apparatus
   ```

2. **Set up the virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

3. **Install Pre-Commit Hooks:**
   We enforce formatting and linting automatically upon commit.
   ```bash
   pre-commit install
   ```

## 2. Architecture & Code Structure

We strictly follow a Domain-Driven Design (DDD) approach. Please ensure your contributions belong in the right module:

- `src/dica/core/`: Application orchestration, state machines, and configuration.
- `src/dica/hardware/`: Device abstractions (Camera, Loadcell, LCD, Printer).
- `src/dica/ai/`: Computer vision pipelines.
- `src/dica/api/`: Web dashboard and external API interfaces.
- `src/dica/db/`: Persistence layers (SQLite, Supabase Sync).

Before submitting a PR, please read `docs/ADR/0001-domain-driven-design.md` for our architectural context.

## 3. Testing Requirements

All new features **MUST** include corresponding unit tests. We strive for a minimum of 80% coverage.

To run tests locally:
```bash
make test
```

To run tests with coverage reporting:
```bash
make test-coverage
```

## 4. Submitting a Pull Request

1. Create a new branch: `git checkout -b feat/your-feature-name` or `fix/your-fix`.
2. Commit your changes using Semantic Commit Messages (e.g., `feat: add new hardware support`).
3. Push to your fork and submit a PR to the `main` branch.
4. Ensure all CI checks (linting, tests) pass.

We look forward to reviewing your contribution!

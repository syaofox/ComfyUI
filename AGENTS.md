# AGENTS.md - ComfyUI Development Guidelines

## Project Overview

ComfyUI is a modular visual AI engine for stable diffusion pipelines. The project uses:
- **Python 3.12+** with **uv** for package management
- **run.sh** script to launch the application
- **custom_nodes/** contains sub-repositories (individual git repos for custom nodes)

---

## Running the Project

```bash
# Start ComfyUI (uses uv run)
./run.sh

# Or directly with uv
uv run main.py
```

---

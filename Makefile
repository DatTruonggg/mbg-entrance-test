# Define Python interpreter and script locations
PYTHON = python
LOAD_SCRIPT = task_load_data.py
GRADIO = gradio_ui.py

# Default target: show available commands
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make help        - Show available commands"
	@echo "  make setup       - Set up the environment and dependencies"
	@echo "  make load_data   - Load case files into Qdrant"
	@echo "  make fastapi     - Run FastAPI backend"
	@echo "  make gradio_ui   - Run Gradio UI"

.PHONY: setup
setup:
	@echo "Starting setup new environment..."
	conda create -n crypto_detective python=3.10 -y
	@echo "Activate environment manually: conda activate crypto_detective"
	@echo "Installing dependencies..."
	conda run -n crypto_detective pip install -r requirements.txt
	@echo "Setting up PYTHONPATH..."
	@echo 'export PYTHONPATH="$PYTHONPATH:$$(pwd)"' >> ~/.bashrc
	@echo "Setup complete. Restart your shell or run: source ~/.bashrc"

.PHONY: load_data
load_data:
	@echo "Loading case files into Qdrant..."
	$(PYTHON) $(LOAD_SCRIPT)

.PHONY: fastapi
fastapi:
	@echo "Running FastAPI..."
	$(PYTHON) -m uvicorn app.application:app --host 0.0.0.0 --port 8000 --reload

.PHONY: gradio_ui
gradio_ui:
	@echo "Running Gradio UI..."
	$(PYTHON) $(GRADIO)

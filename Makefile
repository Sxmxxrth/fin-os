.PHONY: up down logs setup clean

setup:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Virtual environment created and dependencies installed."

up:
	bash start_fin_os.sh
	@echo "🚀 Fin-OS is live at http://localhost:8501"

down:
	killall uvicorn 2>/dev/null || true
	killall streamlit 2>/dev/null || true
	@echo "🛑 All Fin-OS servers stopped."

logs:
	tail -f backend.log frontend.log

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -f backend.log frontend.log

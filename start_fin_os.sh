#!/bin/bash

echo "🛑 Force killing any hanging servers..."
killall uvicorn 2>/dev/null
killall streamlit 2>/dev/null

echo "🐍 Activating Virtual Environment..."
source venv/bin/activate

echo "📦 Ensuring dependencies are installed..."
pip install -r requirements.txt -q

echo "🚀 Starting FastAPI Backend (Port 8005)..."
nohup uvicorn backend.api:app --host 0.0.0.0 --port 8005 > backend.log 2>&1 &

echo "📊 Starting Streamlit Dashboard (Port 8501)..."
nohup streamlit run frontend/dashboard.py > frontend.log 2>&1 &

echo "✅ Fin-OS is now live!"
echo "Dashboard: http://localhost:8501"
echo "API Docs: http://localhost:8005/docs"

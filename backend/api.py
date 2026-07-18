from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os

# Ensure the backend directory is in the path so we can import quant_engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from quant_engine import QuantEngine
from playground_engine import QuantPlaygroundEngine

app = FastAPI(title="Fin-OS Real-Time Quant API", description="Serving 70%+ Precision Predictions")

# Initialize the engines
engine = QuantEngine()
playground = QuantPlaygroundEngine()

class PredictionRequest(BaseModel):
    ticker: str

class StrategyRequest(BaseModel):
    ticker: str
    strategy_text: str

@app.get("/")
def health_check():
    return {"status": "Quant Engine API is online and ready for live trading."}

@app.post("/api/predict")
def predict_live(req: PredictionRequest):
    try:
        # Run the highly optimized probability threshold prediction
        result = engine.predict_realtime(req.ticker.upper())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/playground/backtest")
def backtest_strategy(req: StrategyRequest):
    try:
        # 1. Translate NLP to Code
        pandas_code = playground.nlp_to_code(req.strategy_text)
        
        # 2. Run Vectorized Backtest
        results = playground.run_vectorized_backtest(req.ticker.upper(), pandas_code)
        
        if results.get("status") == "error":
            raise HTTPException(status_code=400, detail=results.get("message"))
            
        # Attach the generated code so the user can see what the LLM wrote
        results["generated_code"] = pandas_code
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

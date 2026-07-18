import sys
import os
from backend.playground_engine import QuantPlaygroundEngine

try:
    engine = QuantPlaygroundEngine()
    print("Testing NLP to Code...")
    code = engine.nlp_to_code("Buy when 50 SMA crosses 200 SMA")
    print(f"Generated Code:\n{code}")
    
    print("\nTesting Vectorized Backtest...")
    res = engine.run_vectorized_backtest("^NSEI", code)
    print(f"Backtest Result:\n{res}")
    
except Exception as e:
    import traceback
    traceback.print_exc()

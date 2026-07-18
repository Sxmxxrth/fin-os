import requests
import json

url = "http://localhost:8005/api/playground/backtest"
payload = {
    "ticker": "^NSEI",
    "strategy_text": "Buy when the 50-day moving average crosses above the 200-day moving average, and sell when it crosses below."
}

try:
    print(f"Testing {url} with {payload['ticker']}...")
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    if data.get('status') == 'success':
        print("✅ SUCCESS! Generated Code:")
        print(data.get('generated_code'))
        print(f"\nTotal Return: {data.get('total_return')}%")
        print(f"Sharpe Ratio: {data.get('sharpe_ratio')}")
        print(f"Win Rate: {data.get('win_rate')}%")
    else:
        print("❌ API Error:", data)
except Exception as e:
    print("❌ Critical Failure:", e)

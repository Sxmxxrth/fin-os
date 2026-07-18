import pandas as pd
import numpy as np
import yfinance as yf
from backend.config import config
from backend.logger import get_logger

log = get_logger(__name__)

class QuantPlaygroundEngine:
    def __init__(self):
        self.groq_key = config.GROQ_API_KEY
        if self.groq_key:
            import groq
            self.client = groq.Groq(api_key=self.groq_key)
        else:
            log.warning("GROQ_API_KEY missing from config. NLP-to-Code will run in mock mode.")

    def fetch_backtest_data(self, ticker: str, period="5y"):
        """Fetches standard OHLCV data for backtesting."""
        df = yf.Ticker(ticker).history(period=period)
        df = df.dropna()
        return df

    def nlp_to_code(self, natural_language_strategy: str):

        """Translates an English trading strategy into Pandas Vectorized Code using Gemini API."""
        system_prompt = "You are a quantitative developer. Write Python `pandas` code to generate a 'Signal' column (1 for holding, 0 for flat). IMPORTANT: 'Signal' represents the POSITION. If the strategy says 'buy when X > Y', Signal should be 1 for ALL days where X > Y, not just the crossover day. Do NOT wrap code in functions like def generate_signal(). Just write flat vectorized operations like df['Signal'] = np.where(X > Y, 1, 0). Assume dataframe `df` with columns: ['Open', 'High', 'Low', 'Close', 'Volume']. Output ONLY valid Python code, no markdown formatting."
        prompt = f"{system_prompt}\nStrategy: {natural_language_strategy}"
        
        if not self.groq_key:
            return "df['SMA_50'] = df['Close'].rolling(window=50).mean()\ndf['SMA_200'] = df['Close'].rolling(window=200).mean()\ndf['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)\n# Note: Missing API Key. Using Fallback Strategy."
            
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": natural_language_strategy}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            )
            code = chat_completion.choices[0].message.content
            return code.replace('```python', '').replace('```', '').strip()
        except Exception as e:
            log.error(f"Groq API Error: {e}")
            fallback_code = "df['SMA_50'] = df['Close'].rolling(window=50).mean()\ndf['SMA_200'] = df['Close'].rolling(window=200).mean()\ndf['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)"
            return f"{fallback_code}\n# Note: API Error. Using Fallback Strategy."

    def run_vectorized_backtest(self, ticker: str, pandas_code: str):
        """Executes the pandas code on historical data and calculates quant metrics."""
        df = self.fetch_backtest_data(ticker)
        
        try:
            # DANGEROUS IN PROD: We use exec() here for the playground architecture.
            # In a real enterprise system, this code would run in an isolated Docker sandbox.
            local_vars = {'df': df, 'np': np, 'pd': pd}
            exec(pandas_code, {}, local_vars)
            df = local_vars['df']
            
            if 'Signal' not in df.columns:
                raise ValueError("The generated code did not produce a 'Signal' column.")
            
            # Vectorized Backtest Math
            # Shift signal by 1 so we calculate returns based on closing price TOMORROW if signal triggered TODAY
            df['Position'] = df['Signal'].shift(1).fillna(0)
            df['Market_Returns'] = df['Close'].pct_change().fillna(0)
            df['Strategy_Returns'] = df['Position'] * df['Market_Returns']
            
            # Cumulative returns (Equity Curve)
            df['Cumulative_Market'] = (1 + df['Market_Returns']).cumprod()
            df['Cumulative_Strategy'] = (1 + df['Strategy_Returns']).cumprod()
            
            # Calculate Quant Metrics
            total_return = df['Cumulative_Strategy'].iloc[-1] - 1
            
            # Sharpe Ratio (Assuming 252 trading days and 4% risk free rate)
            daily_rf = 0.04 / 252
            excess_returns = df['Strategy_Returns'] - daily_rf
            sharpe_ratio = (excess_returns.mean() / df['Strategy_Returns'].std()) * np.sqrt(252) if df['Strategy_Returns'].std() != 0 else 0
            
            # Max Drawdown
            rolling_max = df['Cumulative_Strategy'].cummax()
            drawdown = (df['Cumulative_Strategy'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Win Rate
            winning_days = len(df[df['Strategy_Returns'] > 0])
            total_trading_days = len(df[df['Position'] > 0])
            win_rate = winning_days / total_trading_days if total_trading_days > 0 else 0
            
            return {
                "status": "success",
                "total_return": round(total_return * 100, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "win_rate": round(win_rate * 100, 2),
                "equity_curve": {
                    "dates": df.index.strftime('%Y-%m-%d').tolist(),
                    "strategy": df['Cumulative_Strategy'].tolist(),
                    "market": df['Cumulative_Market'].tolist()
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

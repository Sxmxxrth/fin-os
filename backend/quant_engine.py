import yfinance as yf
import pandas as pd
import numpy as np
import ta
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score
import joblib
import os
from config import config
from logger import get_logger

log = get_logger(__name__)

class QuantEngine:
    def __init__(self, data_dir="data"):
        self.models = {}
        self.scaler = StandardScaler()
        self.data_dir = data_dir
        self.confidence_threshold = config.CONFIDENCE_THRESHOLD  # 70%+ Precision Requirement

    def fetch_realtime_data(self, ticker="^NSEI", period="60d", interval="15m"):
        """Fetches 15-minute interval data (smoother and less noisy than 5m)."""
        df = yf.Ticker(ticker).history(period=period, interval=interval)
        return df

    def engineer_features(self, df):
        """Calculates advanced Institutional quantitative features."""
        # Momentum & Trend
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd = ta.trend.MACD(df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        # Volatility
        bollinger = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        
        # Price Action
        df['Returns'] = df['Close'].pct_change()
        
        # Target: Will the price be strictly higher 2 intervals (30 mins) from now?
        df['Target'] = (df['Close'].shift(-2) > df['Close']).astype(int)
        
        return df.dropna()

    def train_ensemble(self, ticker="^NSEI"):
        log.info(f"Fetching 15m Real-Time Data for {ticker}...")
        df = self.fetch_realtime_data(ticker)
        df = self.engineer_features(df)
        
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 'BB_High', 'BB_Low', 'Returns']
        X = df[features]
        y = df['Target']
        
        X_scaled = self.scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, shuffle=False)
        
        log.info(f"Training Ensemble models for {ticker}...")
        xgb_model = xgb.XGBClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
        xgb_model.fit(X_train, y_train)
        
        rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        rf_model.fit(X_train, y_train)
        
        gb_model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=5, random_state=42)
        gb_model.fit(X_train, y_train)
        
        self.models = {'xgb': xgb_model, 'rf': rf_model, 'gb': gb_model}
        
        # Test the thresholding logic
        y_probs_xgb = xgb_model.predict_proba(X_test)[:, 1]
        y_probs_rf = rf_model.predict_proba(X_test)[:, 1]
        y_probs_gb = gb_model.predict_proba(X_test)[:, 1]
        
        # Average the probability across all 3 models
        avg_probs = (y_probs_xgb + y_probs_rf + y_probs_gb) / 3
        
        # ONLY take trades where average confidence is > threshold
        final_predictions = (avg_probs > self.confidence_threshold).astype(int)
        
        precision = precision_score(y_test, final_predictions, zero_division=0)
        total_trades = sum(final_predictions)
        
        log.info("✅ High-Accuracy Ensemble Trained!")
        log.info(f"🎯 Precision (Win-Rate on executed trades): {precision * 100:.2f}%")
        log.info(f"📉 Number of Trades taken (out of {len(y_test)} intervals): {total_trades}")
        
        if precision > 0.70:
            log.info("🔥 QUANT LEVEL ACHIEVED: Win Rate > 70%")
            
        # Save models
        os.makedirs("../data", exist_ok=True)
        joblib.dump(self.models, "../data/ensemble_dict.pkl")
        joblib.dump(self.scaler, "../data/ensemble_scaler.pkl")
        
        return precision

    def predict_realtime(self, ticker="^NSEI"):
        if not self.models:
            self.models = joblib.load("../data/ensemble_dict.pkl")
            self.scaler = joblib.load("../data/ensemble_scaler.pkl")
            
        df = self.fetch_realtime_data(ticker, period="5d") # Fetch last 5 days just to calculate indicators
        df = self.engineer_features(df)
        
        latest_data = df.iloc[-1:]
        features = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'MACD', 'MACD_Signal', 'BB_High', 'BB_Low', 'Returns']
        
        X_latest = self.scaler.transform(latest_data[features])
        
        p_xgb = self.models['xgb'].predict_proba(X_latest)[0][1]
        p_rf = self.models['rf'].predict_proba(X_latest)[0][1]
        p_gb = self.models['gb'].predict_proba(X_latest)[0][1]
        
        avg_confidence = (p_xgb + p_rf + p_gb) / 3
        
        # Threshold Logic
        if avg_confidence >= self.confidence_threshold:
            signal = "STRONG BUY"
        elif avg_confidence <= (1 - self.confidence_threshold):
            signal = "STRONG SELL"
        else:
            signal = "NEUTRAL / DO NOT TRADE"
            
        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": float(avg_confidence),
            "latest_close": float(latest_data['Close'].iloc[0])
        }

if __name__ == "__main__":
    engine = QuantEngine()
    engine.train_ensemble("^NSEI")

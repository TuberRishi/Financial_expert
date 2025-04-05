import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import base64
from io import BytesIO

class StockTools:
    """
    Tools for stock market analysis and visualization.
    """
    
    @staticmethod
    def get_stock_price(ticker):
        """
        Get the latest stock price for a ticker.
        
        Args:
            ticker: The stock ticker symbol (e.g., AAPL for Apple)
            
        Returns:
            Latest stock price
        """
        try:
            data = yf.Ticker(ticker)
            price = data.history(period='1d').iloc[-1].Close
            return {
                "price": round(float(price), 2),
                "currency": data.info.get("currency", "USD"),
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {"error": f"Error getting stock price: {str(e)}"}
    
    @staticmethod
    def get_stock_info(ticker):
        """
        Get basic information about a stock.
        
        Args:
            ticker: The stock ticker symbol (e.g., AAPL for Apple)
            
        Returns:
            Dictionary containing stock information
        """
        try:
            data = yf.Ticker(ticker)
            info = data.info
            
            result = {
                "name": info.get("shortName", "Unknown"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", None),
                "dividend_yield": info.get("dividendYield", None),
                "52_week_high": info.get("fiftyTwoWeekHigh", None),
                "52_week_low": info.get("fiftyTwoWeekLow", None)
            }
            
            # Format market cap to billions/millions
            if result["market_cap"]:
                if result["market_cap"] > 1_000_000_000:
                    result["market_cap_formatted"] = f"${round(result['market_cap']/1_000_000_000, 2)}B"
                else:
                    result["market_cap_formatted"] = f"${round(result['market_cap']/1_000_000, 2)}M"
                    
            # Format dividend yield as percentage
            if result["dividend_yield"]:
                result["dividend_yield"] = round(result["dividend_yield"] * 100, 2)
                
            return result
        except Exception as e:
            return {"error": f"Error getting stock info: {str(e)}"}
    
    @staticmethod
    def calculate_sma(ticker, window=20):
        """
        Calculate Simple Moving Average for a stock.
        
        Args:
            ticker: The stock ticker symbol
            window: The time window for calculation (default: 20 days)
            
        Returns:
            The SMA value
        """
        try:
            data = yf.Ticker(ticker).history(period='1y').Close
            sma = data.rolling(window=window).mean().iloc[-1]
            return {
                "sma": round(float(sma), 2),
                "window": window,
                "current_price": round(float(data.iloc[-1]), 2)
            }
        except Exception as e:
            return {"error": f"Error calculating SMA: {str(e)}"}
    
    @staticmethod
    def calculate_ema(ticker, window=20):
        """
        Calculate Exponential Moving Average for a stock.
        
        Args:
            ticker: The stock ticker symbol
            window: The time window for calculation (default: 20 days)
            
        Returns:
            The EMA value
        """
        try:
            data = yf.Ticker(ticker).history(period='1y').Close
            ema = data.ewm(span=window, adjust=False).mean().iloc[-1]
            return {
                "ema": round(float(ema), 2),
                "window": window,
                "current_price": round(float(data.iloc[-1]), 2)
            }
        except Exception as e:
            return {"error": f"Error calculating EMA: {str(e)}"}
    
    @staticmethod
    def calculate_rsi(ticker, window=14):
        """
        Calculate Relative Strength Index for a stock.
        
        Args:
            ticker: The stock ticker symbol
            window: The time window for calculation (default: 14 days)
            
        Returns:
            The RSI value
        """
        try:
            data = yf.Ticker(ticker).history(period='1y').Close
            delta = data.diff()
            up = delta.clip(lower=0)
            down = -1 * delta.clip(upper=0)
            ema_up = up.ewm(com=window-1, adjust=False).mean()
            ema_down = down.ewm(com=window-1, adjust=False).mean()
            rs = ema_up / ema_down
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            return {
                "rsi": round(float(rsi), 2),
                "window": window,
                "interpretation": "Oversold" if rsi < 30 else "Overbought" if rsi > 70 else "Neutral"
            }
        except Exception as e:
            return {"error": f"Error calculating RSI: {str(e)}"}
    
    @staticmethod
    def calculate_macd(ticker):
        """
        Calculate MACD (Moving Average Convergence Divergence) for a stock.
        
        Args:
            ticker: The stock ticker symbol
            
        Returns:
            MACD values
        """
        try:
            data = yf.Ticker(ticker).history(period='1y').Close
            short_ema = data.ewm(span=12, adjust=False).mean()
            long_ema = data.ewm(span=26, adjust=False).mean()
            
            macd = short_ema - long_ema
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal
            
            return {
                "macd": round(float(macd.iloc[-1]), 4),
                "signal": round(float(signal.iloc[-1]), 4),
                "histogram": round(float(histogram.iloc[-1]), 4),
                "bullish": bool(histogram.iloc[-1] > 0 and histogram.iloc[-1] > histogram.iloc[-2])
            }
        except Exception as e:
            return {"error": f"Error calculating MACD: {str(e)}"}
    
    @staticmethod
    def plot_stock_price(ticker, period="1y"):
        """
        Create a stock price chart.
        
        Args:
            ticker: The stock ticker symbol
            period: Time period (default: 1y - 1 year)
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Get data
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return {"error": f"No data found for ticker: {ticker}"}
            
            # Create figure
            plt.figure(figsize=(10, 6))
            plt.plot(data.index, data.Close, 'b-', linewidth=2)
            plt.title(f"{stock.info.get('shortName', ticker)} Stock Price - {period}", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel(f"Price ({stock.info.get('currency', 'USD')})", fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Add recent price annotation
            latest_price = data.Close.iloc[-1]
            latest_date = data.index[-1]
            plt.annotate(f"${latest_price:.2f}", 
                        xy=(latest_date, latest_price),
                        xytext=(latest_date, latest_price*1.05),
                        fontsize=12, 
                        arrowprops=dict(arrowstyle="->", color="black"))
            
            # Save to BytesIO
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            # Encode to base64
            img_str = base64.b64encode(buffer.read()).decode()
            
            return {
                "image": img_str,
                "ticker": ticker,
                "latest_price": round(float(latest_price), 2),
                "period": period
            }
        except Exception as e:
            return {"error": f"Error plotting stock price: {str(e)}"}
    
    @staticmethod
    def plot_technical_indicators(ticker, period="1y"):
        """
        Create a technical analysis chart with price, SMA, EMA, and volume.
        
        Args:
            ticker: The stock ticker symbol
            period: Time period (default: 1y - 1 year)
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Get data
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
            
            if data.empty:
                return {"error": f"No data found for ticker: {ticker}"}
            
            # Calculate indicators
            data['SMA20'] = data['Close'].rolling(window=20).mean()
            data['SMA50'] = data['Close'].rolling(window=50).mean()
            data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
            
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
            
            # Price and indicators on top subplot
            ax1.plot(data.index, data.Close, 'b-', linewidth=2, label='Price')
            ax1.plot(data.index, data.SMA20, 'r--', linewidth=1.5, label='SMA (20)')
            ax1.plot(data.index, data.SMA50, 'g--', linewidth=1.5, label='SMA (50)')
            ax1.plot(data.index, data.EMA20, 'm-.', linewidth=1.5, label='EMA (20)')
            
            ax1.set_title(f"{stock.info.get('shortName', ticker)} Technical Analysis - {period}", fontsize=16)
            ax1.set_ylabel(f"Price ({stock.info.get('currency', 'USD')})", fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='upper left')
            
            # Volume on bottom subplot
            ax2.bar(data.index, data.Volume, color='blue', alpha=0.5)
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to BytesIO
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            # Encode to base64
            img_str = base64.b64encode(buffer.read()).decode()
            
            return {
                "image": img_str,
                "ticker": ticker,
                "latest_price": round(float(data.Close.iloc[-1]), 2),
                "latest_sma20": round(float(data.SMA20.iloc[-1]), 2) if not pd.isna(data.SMA20.iloc[-1]) else None,
                "latest_sma50": round(float(data.SMA50.iloc[-1]), 2) if not pd.isna(data.SMA50.iloc[-1]) else None,
                "period": period
            }
        except Exception as e:
            return {"error": f"Error plotting technical indicators: {str(e)}"}
    
    @staticmethod
    def get_historical_data(ticker, period="1y"):
        """
        Get historical data for a stock.
        
        Args:
            ticker: The stock ticker symbol
            period: Time period (default: 1y - 1 year)
            
        Returns:
            Dictionary with historical data
        """
        try:
            data = yf.Ticker(ticker).history(period=period)
            
            # Calculate daily returns
            data['Daily_Return'] = data['Close'].pct_change() * 100
            
            # Format the result
            result = {
                "ticker": ticker,
                "period": period,
                "start_date": data.index[0].strftime('%Y-%m-%d'),
                "end_date": data.index[-1].strftime('%Y-%m-%d'),
                "price_start": round(float(data.Close.iloc[0]), 2),
                "price_end": round(float(data.Close.iloc[-1]), 2),
                "price_change": round(float(data.Close.iloc[-1] - data.Close.iloc[0]), 2),
                "price_change_pct": round(float((data.Close.iloc[-1] / data.Close.iloc[0] - 1) * 100), 2),
                "highest_price": round(float(data.High.max()), 2),
                "lowest_price": round(float(data.Low.min()), 2),
                "avg_volume": int(data.Volume.mean()),
                "avg_daily_return": round(float(data.Daily_Return.mean()), 2),
                "volatility": round(float(data.Daily_Return.std()), 2),
            }
            
            return result
        except Exception as e:
            return {"error": f"Error getting historical data: {str(e)}"}
    
    @staticmethod
    def compare_stocks(tickers, period="1y"):
        """
        Compare multiple stocks performance.
        
        Args:
            tickers: List of stock ticker symbols
            period: Time period (default: 1y - 1 year)
            
        Returns:
            Base64 encoded image string with comparison chart
        """
        try:
            if not isinstance(tickers, list):
                tickers = [tickers]
                
            if len(tickers) > 5:
                tickers = tickers[:5]  # Limit to 5 stocks for readability
                
            # Create dataframe to store normalized prices
            compare_data = pd.DataFrame()
            
            # Get data for each ticker and normalize
            for ticker in tickers:
                stock_data = yf.Ticker(ticker).history(period=period)
                if not stock_data.empty:
                    # Normalize to 100 at the beginning
                    compare_data[ticker] = stock_data.Close / stock_data.Close.iloc[0] * 100
            
            if compare_data.empty:
                return {"error": "No data found for the provided tickers"}
            
            # Create the comparison chart
            plt.figure(figsize=(12, 7))
            
            for ticker in compare_data.columns:
                plt.plot(compare_data.index, compare_data[ticker], linewidth=2, label=ticker)
                
            plt.title("Stock Price Performance Comparison (Normalized to 100)", fontsize=16)
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Normalized Price", fontsize=12)
            plt.legend(loc="best")
            plt.grid(True, alpha=0.3)
            
            # Add annotations for final values
            for ticker in compare_data.columns:
                final_value = compare_data[ticker].iloc[-1]
                change = final_value - 100
                sign = "+" if change >= 0 else ""
                plt.annotate(f"{ticker}: {sign}{change:.2f}%", 
                            xy=(compare_data.index[-1], final_value),
                            xytext=(10, 0),
                            textcoords="offset points",
                            fontsize=10)
            
            # Save to BytesIO
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            buffer.seek(0)
            plt.close()
            
            # Encode to base64
            img_str = base64.b64encode(buffer.read()).decode()
            
            # Prepare performance summary
            performance = {}
            for ticker in compare_data.columns:
                final_value = compare_data[ticker].iloc[-1]
                performance[ticker] = round(final_value - 100, 2)
            
            return {
                "image": img_str,
                "tickers": tickers,
                "period": period,
                "performance": performance
            }
        except Exception as e:
            return {"error": f"Error comparing stocks: {str(e)}"} 
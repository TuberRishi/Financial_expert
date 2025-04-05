from search_tools import SearchTool
from sentiment_analyzer import SentimentAnalyzer
from stock_tools import StockTools
from typing import Dict, Any, Optional, List, Union
import re

class FinancialAgent:
    """
    Financial sentiment analysis agent that coordinates searching and sentiment analysis.
    """
    
    def __init__(self):
        self.search_tool = SearchTool()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.stock_tools = StockTools()
        # Add memory for conversation history
        self.conversation_history = []
        self.context = {
            "last_entity": None,  # Last entity mentioned (person, company, etc.)
            "last_topic": None,   # Last topic discussed
            "last_query": None,   # Last query processed
            "last_response": None # Last response given
        }
        
    def handle_query(self, query: str) -> Dict[str, Any]:
        """
        Handle a user query.
        
        Args:
            query: The user query
            
        Returns:
            Dictionary containing the response
        """
        try:
            # Update context with current query
            self.context["last_query"] = query
            
            # Check if this is a follow-up question
            if self._is_follow_up_question(query):
                # Enhance query with context
                enhanced_query = self._enhance_query_with_context(query)
                print(f"Enhanced query with context: {enhanced_query}")
                query = enhanced_query
            
            # Check if query is finance-related
            if not self.sentiment_analyzer.is_finance_related(query):
                return {
                    "is_finance_related": False,
                    "is_report_query": False,
                    "response": "I can only help you with finance, business, or market related queries."
                }
            
            # Check if it's a stock query
            stock_result = self.handle_stock_query(query)
            if stock_result:
                # Update context with stock information
                if "ticker" in stock_result:
                    self.context["last_entity"] = stock_result.get("ticker")
                    self.context["last_topic"] = "stock"
                return stock_result
            
            # Simple factual queries that don't need web search
            simple_answer = self.handle_simple_query(query)
            if simple_answer:
                # Update context with simple query information
                self._update_context_from_simple_query(query, simple_answer)
                return {
                    "is_finance_related": True,
                    "is_simple_query": True,
                    "is_report_query": False,
                    "response": simple_answer
                }
            
            # Identify if this is a report query or a normal question
            is_report_query = self._is_report_query(query)
            
            # For complex queries, search the web
            print(f"Searching for: {query}")
            search_results = self.search_tool.search_and_consolidate(query)
            print(f"Got {len(search_results.split())} words of search results")
            
            if not search_results or search_results == "No information found. Please try a different query or check your internet connection.":
                return {
                    "is_finance_related": True,
                    "is_simple_query": False,
                    "is_report_query": False,
                    "error": True,
                    "response": "I couldn't find any relevant information for your query. Please try rephrasing or ask about a more specific financial topic."
                }
            
            # Analyze sentiment
            print("Analyzing sentiment...")
            analysis = self.sentiment_analyzer.analyze_sentiment(search_results, query)
            print(f"Analysis complete with sentiment: {analysis.get('sentiment', 'UNKNOWN')}")
            
            # Extract entities from the query and update context
            self._extract_and_update_entities(query, search_results)
            
            # Store the conversation in history
            self.conversation_history.append({
                "query": query,
                "response": analysis.get("summary", ""),
                "entities": self.context["last_entity"]
            })
            
            # Limit conversation history to last 10 exchanges
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return {
                "is_finance_related": True,
                "is_simple_query": False,
                "is_report_query": is_report_query,
                "search_results": search_results,
                "analysis": analysis
            }
        except Exception as e:
            print(f"Error handling query: {e}")
            import traceback
            traceback.print_exc()
            return {
                "is_finance_related": True,
                "is_simple_query": False,
                "is_report_query": False,
                "error": True,
                "response": f"An error occurred while processing your query: {str(e)}"
            }
    
    def _is_follow_up_question(self, query: str) -> bool:
        """
        Determine if the current query is a follow-up to a previous question.
        
        Args:
            query: The current query
            
        Returns:
            True if this is a follow-up question
        """
        # Check for pronouns or references to previous context
        follow_up_indicators = [
            "he", "she", "it", "they", "them", "their", "his", "her", "its",
            "this", "that", "these", "those", "the company", "the stock",
            "the report", "the statement", "the financial", "the latest"
        ]
        
        query_lower = query.lower()
        
        # Check if query contains follow-up indicators
        has_follow_up_indicators = any(indicator in query_lower for indicator in follow_up_indicators)
        
        # Check if we have previous context
        has_previous_context = self.context["last_entity"] is not None
        
        return has_follow_up_indicators and has_previous_context
    
    def _enhance_query_with_context(self, query: str) -> str:
        """
        Enhance a follow-up query with context from previous exchanges.
        
        Args:
            query: The current query
            
        Returns:
            Enhanced query with context
        """
        # Replace pronouns with the last entity
        if self.context["last_entity"]:
            query = query.replace(" he ", f" {self.context['last_entity']} ")
            query = query.replace(" she ", f" {self.context['last_entity']} ")
            query = query.replace(" it ", f" {self.context['last_entity']} ")
            query = query.replace(" they ", f" {self.context['last_entity']} ")
            query = query.replace(" them ", f" {self.context['last_entity']} ")
            query = query.replace(" their ", f" {self.context['last_entity']}'s ")
            query = query.replace(" his ", f" {self.context['last_entity']}'s ")
            query = query.replace(" her ", f" {self.context['last_entity']}'s ")
            query = query.replace(" its ", f" {self.context['last_entity']}'s ")
            
            # Replace generic references
            query = query.replace(" the company ", f" {self.context['last_entity']} ")
            query = query.replace(" the stock ", f" {self.context['last_entity']} ")
            query = query.replace(" the report ", f" {self.context['last_entity']}'s report ")
            query = query.replace(" the statement ", f" {self.context['last_entity']}'s statement ")
            query = query.replace(" the financial ", f" {self.context['last_entity']}'s financial ")
            query = query.replace(" the latest ", f" {self.context['last_entity']}'s latest ")
        
        return query
    
    def _extract_and_update_entities(self, query: str, search_results: str) -> None:
        """
        Extract entities from query and search results and update context.
        
        Args:
            query: The user query
            search_results: The search results
        """
        # Extract potential stock tickers
        tickers = self._extract_tickers(query)
        if tickers:
            self.context["last_entity"] = tickers[0]
            self.context["last_topic"] = "stock"
            return
        
        # Extract company names
        company_names = [
            "Apple", "Microsoft", "Amazon", "Google", "Alphabet", "Facebook", "Meta",
            "Tesla", "Netflix", "Nvidia", "Walmart", "Disney", "Coca-Cola", "IBM",
            "Intel", "Alibaba", "AMD", "Nike", "JP Morgan", "Bank of America",
            "Goldman Sachs", "Pfizer", "Johnson & Johnson"
        ]
        
        for company in company_names:
            if company.lower() in query.lower():
                self.context["last_entity"] = company
                self.context["last_topic"] = "company"
                return
        
        # Extract person names
        person_names = [
            "Elon Musk", "Warren Buffett", "Jeff Bezos", "Mark Zuckerberg",
            "Tim Cook", "Satya Nadella", "Jerome Powell", "Janet Yellen",
            "Ray Dalio", "Cathie Wood", "Peter Lynch", "George Soros"
        ]
        
        for person in person_names:
            if person.lower() in query.lower():
                self.context["last_entity"] = person
                self.context["last_topic"] = "person"
                return
    
    def _update_context_from_simple_query(self, query: str, answer: str) -> None:
        """
        Update context from simple query results.
        
        Args:
            query: The user query
            answer: The answer to the query
        """
        query_lower = query.lower()
        
        # Extract ticker information
        if "ticker" in query_lower:
            if "apple" in query_lower:
                self.context["last_entity"] = "AAPL"
                self.context["last_topic"] = "stock"
            elif "microsoft" in query_lower:
                self.context["last_entity"] = "MSFT"
                self.context["last_topic"] = "stock"
            elif "google" in query_lower:
                self.context["last_entity"] = "GOOGL"
                self.context["last_topic"] = "stock"
            elif "amazon" in query_lower:
                self.context["last_entity"] = "AMZN"
                self.context["last_topic"] = "stock"
            elif "tesla" in query_lower:
                self.context["last_entity"] = "TSLA"
                self.context["last_topic"] = "stock"
        
        # Extract financial terms
        if "market cap" in query_lower or "market capitalization" in query_lower:
            self.context["last_topic"] = "financial_term"
        elif "p/e ratio" in query_lower:
            self.context["last_topic"] = "financial_term"
    
    def handle_stock_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Handle queries related to stocks and stock data.
        """
        query_lower = query.lower()
        
        # Extract potential stock tickers from query
        tickers = self._extract_tickers(query)
        
        # Stock price query
        if ("stock price" in query_lower or "price of" in query_lower or "current price" in query_lower or 
            "trading at" in query_lower or "what is the price" in query_lower) and tickers:
            ticker = tickers[0]
            price_data = self.stock_tools.get_stock_price(ticker)
            info_data = self.stock_tools.get_stock_info(ticker)
            
            if "error" in price_data:
                return {
                    "is_finance_related": True,
                    "is_stock_query": True,
                    "is_simple_query": True,
                    "response": f"Sorry, I couldn't get the stock price for {ticker}. {price_data['error']}"
                }
            
            # Create nice report
            company_name = info_data.get("name", ticker)
            price = price_data.get("price", "N/A")
            currency = price_data.get("currency", "USD")
            
            response = f"## {company_name} ({ticker})\n\n"
            response += f"**Current Price**: ${price} {currency}\n\n"
            
            # Add additional info if available
            if not "error" in info_data:
                if info_data.get("sector"):
                    response += f"**Sector**: {info_data.get('sector')}\n\n"
                if info_data.get("market_cap_formatted"):
                    response += f"**Market Cap**: {info_data.get('market_cap_formatted')}\n\n"
                if info_data.get("pe_ratio"):
                    response += f"**P/E Ratio**: {info_data.get('pe_ratio'):.2f}\n\n"
                if info_data.get("dividend_yield"):
                    response += f"**Dividend Yield**: {info_data.get('dividend_yield')}%\n\n"
            
            return {
                "is_finance_related": True,
                "is_stock_query": True,
                "is_simple_query": True,
                "is_report_query": False,
                "response": response.strip()
            }
            
        # Stock chart query
        if ("chart" in query_lower or "graph" in query_lower or "plot" in query_lower or 
            "performance" in query_lower or "trend" in query_lower or "historical" in query_lower) and tickers:
            ticker = tickers[0]
            
            # Determine the period
            period = "1y"  # default 1 year
            if "day" in query_lower or "24 hour" in query_lower or "today" in query_lower:
                period = "1d"
            elif "week" in query_lower:
                period = "1wk"
            elif "month" in query_lower:
                period = "1mo"
            elif "3 month" in query_lower or "quarter" in query_lower:
                period = "3mo"
            elif "6 month" in query_lower:
                period = "6mo"
            elif "year" in query_lower or "12 month" in query_lower:
                period = "1y"
            elif "2 year" in query_lower:
                period = "2y"
            elif "5 year" in query_lower:
                period = "5y"
            elif "max" in query_lower or "all time" in query_lower or "all-time" in query_lower:
                period = "max"
            
            # Check if technical analysis is requested
            if "technical" in query_lower or "indicator" in query_lower or "sma" in query_lower or "ema" in query_lower:
                chart_data = self.stock_tools.plot_technical_indicators(ticker, period)
            else:
                chart_data = self.stock_tools.plot_stock_price(ticker, period)
            
            if "error" in chart_data:
                return {
                    "is_finance_related": True,
                    "is_stock_query": True,
                    "is_chart_query": True,
                    "is_simple_query": False,
                    "response": f"Sorry, I couldn't generate a chart for {ticker}. {chart_data['error']}"
                }
            
            return {
                "is_finance_related": True,
                "is_stock_query": True,
                "is_chart_query": True,
                "is_simple_query": False,
                "is_report_query": False,
                "chart_data": chart_data,
                "ticker": ticker
            }
            
        # Stock comparison query
        if ("compare" in query_lower or "vs" in query_lower or "versus" in query_lower or 
            "against" in query_lower or "which is better" in query_lower) and len(tickers) > 1:
            
            # Determine the period
            period = "1y"  # default 1 year
            if "day" in query_lower or "24 hour" in query_lower:
                period = "1d"
            elif "week" in query_lower:
                period = "1wk"
            elif "month" in query_lower:
                period = "1mo"
            elif "3 month" in query_lower or "quarter" in query_lower:
                period = "3mo"
            elif "6 month" in query_lower:
                period = "6mo"
            elif "year" in query_lower or "12 month" in query_lower:
                period = "1y"
            elif "2 year" in query_lower:
                period = "2y"
            elif "5 year" in query_lower:
                period = "5y"
            elif "max" in query_lower or "all time" in query_lower:
                period = "max"
                
            comparison_data = self.stock_tools.compare_stocks(tickers, period)
            
            if "error" in comparison_data:
                return {
                    "is_finance_related": True,
                    "is_stock_query": True,
                    "is_comparison_query": True,
                    "is_simple_query": False,
                    "response": f"Sorry, I couldn't compare these stocks. {comparison_data['error']}"
                }
                
            return {
                "is_finance_related": True,
                "is_stock_query": True,
                "is_comparison_query": True,
                "is_simple_query": False,
                "is_report_query": False,
                "comparison_data": comparison_data,
                "tickers": tickers
            }
            
        # Technical indicators query
        if (("indicator" in query_lower or "technical" in query_lower) and
            ("rsi" in query_lower or "macd" in query_lower or "moving average" in query_lower or 
             "sma" in query_lower or "ema" in query_lower)) and tickers:
            
            ticker = tickers[0]
            indicator_data = {}
            response = f"## Technical Indicators for {ticker}\n\n"
            
            # RSI
            if "rsi" in query_lower or "relative strength index" in query_lower:
                rsi_data = self.stock_tools.calculate_rsi(ticker)
                if "error" not in rsi_data:
                    indicator_data["rsi"] = rsi_data
                    response += f"**RSI (14)**: {rsi_data.get('rsi')}\n"
                    response += f"**Interpretation**: {rsi_data.get('interpretation')}\n\n"
            
            # MACD
            if "macd" in query_lower or "moving average convergence divergence" in query_lower:
                macd_data = self.stock_tools.calculate_macd(ticker)
                if "error" not in macd_data:
                    indicator_data["macd"] = macd_data
                    response += f"**MACD**: {macd_data.get('macd')}\n"
                    response += f"**Signal**: {macd_data.get('signal')}\n"
                    response += f"**Histogram**: {macd_data.get('histogram')}\n"
                    response += f"**Signal**: {'Bullish' if macd_data.get('bullish') else 'Bearish'}\n\n"
            
            # SMA
            if "sma" in query_lower or "simple moving average" in query_lower:
                window = 20  # default
                if "50" in query_lower:
                    window = 50
                elif "200" in query_lower:
                    window = 200
                elif "100" in query_lower:
                    window = 100
                
                sma_data = self.stock_tools.calculate_sma(ticker, window)
                if "error" not in sma_data:
                    indicator_data["sma"] = sma_data
                    response += f"**SMA ({window})**: {sma_data.get('sma')}\n"
                    response += f"**Current Price**: {sma_data.get('current_price')}\n"
                    above_below = "above" if sma_data.get('current_price', 0) > sma_data.get('sma', 0) else "below"
                    response += f"**Status**: Price is {above_below} SMA {window}\n\n"
            
            # EMA
            if "ema" in query_lower or "exponential moving average" in query_lower:
                window = 20  # default
                if "50" in query_lower:
                    window = 50
                elif "200" in query_lower:
                    window = 200
                elif "100" in query_lower:
                    window = 100
                
                ema_data = self.stock_tools.calculate_ema(ticker, window)
                if "error" not in ema_data:
                    indicator_data["ema"] = ema_data
                    response += f"**EMA ({window})**: {ema_data.get('ema')}\n"
                    response += f"**Current Price**: {ema_data.get('current_price')}\n"
                    above_below = "above" if ema_data.get('current_price', 0) > ema_data.get('ema', 0) else "below"
                    response += f"**Status**: Price is {above_below} EMA {window}\n\n"
            
            if not indicator_data:
                return {
                    "is_finance_related": True,
                    "is_stock_query": True,
                    "is_simple_query": True,
                    "response": f"Sorry, I couldn't calculate the requested indicators for {ticker}."
                }
                
            # Add a recommendation based on indicators
            response += self._generate_technical_recommendation(indicator_data, ticker)
            
            return {
                "is_finance_related": True,
                "is_stock_query": True,
                "is_indicator_query": True,
                "is_simple_query": True,
                "is_report_query": False,
                "response": response.strip(),
                "indicator_data": indicator_data,
                "ticker": ticker
            }
        
        # Historical data query
        if "historical" in query_lower and tickers:
            ticker = tickers[0]
            
            # Determine the period
            period = "1y"  # default 1 year
            if "month" in query_lower:
                period = "1mo"
            elif "3 month" in query_lower or "quarter" in query_lower:
                period = "3mo"
            elif "6 month" in query_lower:
                period = "6mo"
            elif "year" in query_lower or "12 month" in query_lower:
                period = "1y"
            elif "2 year" in query_lower:
                period = "2y"
            elif "5 year" in query_lower:
                period = "5y"
            elif "10 year" in query_lower:
                period = "10y"
            elif "max" in query_lower or "all time" in query_lower:
                period = "max"
                
            hist_data = self.stock_tools.get_historical_data(ticker, period)
            
            if "error" in hist_data:
                return {
                    "is_finance_related": True,
                    "is_stock_query": True,
                    "is_simple_query": True,
                    "response": f"Sorry, I couldn't get historical data for {ticker}. {hist_data['error']}"
                }
                
            # Format response
            company_name = self.stock_tools.get_stock_info(ticker).get("name", ticker)
            response = f"## Historical Performance: {company_name} ({ticker})\n\n"
            response += f"**Period**: {hist_data.get('start_date')} to {hist_data.get('end_date')}\n\n"
            
            # Price Change
            price_change = hist_data.get('price_change_pct')
            price_change_sign = '+' if price_change >= 0 else ''
            response += f"**Price Change**: {price_change_sign}{price_change}%\n"
            response += f"**Starting Price**: ${hist_data.get('price_start')}\n"
            response += f"**Ending Price**: ${hist_data.get('price_end')}\n\n"
            
            # High/Low
            response += f"**Highest Price**: ${hist_data.get('highest_price')}\n"
            response += f"**Lowest Price**: ${hist_data.get('lowest_price')}\n\n"
            
            # Volatility & Volume
            response += f"**Average Daily Return**: {hist_data.get('avg_daily_return')}%\n"
            response += f"**Volatility (Std Dev)**: {hist_data.get('volatility')}%\n"
            response += f"**Average Daily Volume**: {hist_data.get('avg_volume'):,}\n"
            
            return {
                "is_finance_related": True,
                "is_stock_query": True,
                "is_historical_query": True,
                "is_simple_query": True,
                "is_report_query": False,
                "response": response.strip(),
                "hist_data": hist_data,
                "ticker": ticker
            }
        
        # Not a stock query
        return None
    
    def _extract_tickers(self, query: str) -> List[str]:
        """Extract potential stock tickers from query."""
        # Common stock tickers mentioned with $ sign
        dollar_tickers = re.findall(r'\$([A-Z]{1,5})', query)
        
        # Common stock tickers in all caps
        words = query.split()
        cap_tickers = [word.strip('.,?!()[]{}') for word in words 
                      if word.strip('.,?!()[]{}').isupper() and 
                      1 <= len(word.strip('.,?!()[]{}')) <= 5]
        
        # Common stock names to ticker mapping
        name_to_ticker = {
            # US Stocks
            'apple': 'AAPL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'facebook': 'META',
            'meta': 'META',
            'tesla': 'TSLA',
            'netflix': 'NFLX',
            'nvidia': 'NVDA',
            'walmart': 'WMT',
            'disney': 'DIS',
            'coca cola': 'KO',
            'coca-cola': 'KO',
            'coke': 'KO',
            'ibm': 'IBM',
            'intel': 'INTC',
            'alibaba': 'BABA',
            'amd': 'AMD',
            'nike': 'NKE',
            'jp morgan': 'JPM',
            'jpmorgan': 'JPM',
            'bank of america': 'BAC',
            'goldman sachs': 'GS',
            'pfizer': 'PFE',
            'johnson & johnson': 'JNJ',
            
            # Indian Stocks
            'reliance': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'hdfc': 'HDFCBANK.NS',
            'infosys': 'INFY.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'hul': 'HINDUNILVR.NS',
            'hindustan unilever': 'HINDUNILVR.NS',
            'unilever': 'HINDUNILVR.NS',
            'sbi': 'SBIN.NS',
            'state bank': 'SBIN.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'asian paints': 'ASIANPAINT.NS',
            'asianpaints': 'ASIANPAINT.NS',
            'kotak bank': 'KOTAKBANK.NS',
            'kotak': 'KOTAKBANK.NS',
            'lt': 'LT.NS',
            'larsen': 'LT.NS',
            'larsen & toubro': 'LT.NS',
            'hcl tech': 'HCLTECH.NS',
            'hcl': 'HCLTECH.NS',
            'wipro': 'WIPRO.NS',
            'axis bank': 'AXISBANK.NS',
            'axis': 'AXISBANK.NS',
            'maruti': 'MARUTI.NS',
            'maruti suzuki': 'MARUTI.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'sunpharma': 'SUNPHARMA.NS',
            'titan': 'TITAN.NS',
            'titan company': 'TITAN.NS',
            'bajaj finance': 'BAJFINANCE.NS',
            'bajajfinance': 'BAJFINANCE.NS',
            'bajaj auto': 'BAJAJ-AUTO.NS',
            'bajajauto': 'BAJAJ-AUTO.NS',
            'mahindra': 'M&M.NS',
            'mahindra & mahindra': 'M&M.NS',
            'ultra tech': 'ULTRACEMCO.NS',
            'ultratech': 'ULTRACEMCO.NS',
            'ultracemco': 'ULTRACEMCO.NS',
            'nestle': 'NESTLEIND.NS',
            'nestle india': 'NESTLEIND.NS',
            'tata steel': 'TATASTEEL.NS',
            'tatasteel': 'TATASTEEL.NS',
            'tata motors': 'TATAMOTORS.NS',
            'tatamotors': 'TATAMOTORS.NS',
            'tata consultancy': 'TCS.NS',
            'tata consult': 'TCS.NS',
            'adani ports': 'ADANIPORTS.NS',
            'adaniports': 'ADANIPORTS.NS',
            'adani green': 'ADANIGREEN.NS',
            'adanigreen': 'ADANIGREEN.NS',
            'adani enterprises': 'ADANIENT.NS',
            'adanient': 'ADANIENT.NS',
            'adani power': 'ADANIPOWER.NS',
            'adanipower': 'ADANIPOWER.NS',
            'adani transmission': 'ADANITRANS.NS',
            'adanitrans': 'ADANITRANS.NS',
            'adani total gas': 'ATGL.NS',
            'atgl': 'ATGL.NS',
            'adani wilmar': 'AWL.NS',
            'awl': 'AWL.NS'
        }
        
        name_tickers = []
        query_lower = query.lower()
        for name, ticker in name_to_ticker.items():
            if name in query_lower:
                name_tickers.append(ticker)
        
        # Combine all found tickers and remove duplicates
        all_tickers = dollar_tickers + cap_tickers + name_tickers
        return list(dict.fromkeys(all_tickers))  # Remove duplicates while preserving order
    
    def _generate_technical_recommendation(self, indicator_data: Dict[str, Any], ticker: str) -> str:
        """Generate a recommendation based on technical indicators."""
        signals = []
        
        # RSI signals
        if "rsi" in indicator_data:
            rsi = indicator_data["rsi"].get("rsi", 50)
            if rsi < 30:
                signals.append(("bullish", "RSI indicates oversold conditions"))
            elif rsi > 70:
                signals.append(("bearish", "RSI indicates overbought conditions"))
                
        # MACD signals
        if "macd" in indicator_data:
            if indicator_data["macd"].get("bullish", False):
                signals.append(("bullish", "MACD shows bullish momentum"))
            else:
                signals.append(("bearish", "MACD shows bearish momentum"))
                
        # Moving Average signals
        for ma_type in ["sma", "ema"]:
            if ma_type in indicator_data:
                current = indicator_data[ma_type].get("current_price", 0)
                ma_value = indicator_data[ma_type].get(ma_type, 0)
                window = indicator_data[ma_type].get("window", 0)
                
                if current > ma_value:
                    signals.append(("bullish", f"Price is above {ma_type.upper()} {window}"))
                else:
                    signals.append(("bearish", f"Price is below {ma_type.upper()} {window}"))
        
        # Count signals
        bullish = sum(1 for signal in signals if signal[0] == "bullish")
        bearish = sum(1 for signal in signals if signal[0] == "bearish")
        
        # Generate recommendation
        recommendation = "## Technical Analysis Summary\n\n"
        
        if bullish > bearish:
            recommendation += f"**Overall Signal**: BULLISH\n\n"
        elif bearish > bullish:
            recommendation += f"**Overall Signal**: BEARISH\n\n"
        else:
            recommendation += f"**Overall Signal**: NEUTRAL\n\n"
            
        recommendation += "**Signals**:\n"
        for signal_type, reason in signals:
            indicator = "📈" if signal_type == "bullish" else "📉"
            recommendation += f"- {indicator} {reason}\n"
            
        recommendation += "\n**Note**: Technical analysis should be combined with fundamental analysis and overall market conditions."
        
        return recommendation
    
    def _is_report_query(self, query: str) -> bool:
        """
        Determine if the query is asking for a detailed report.
        
        Args:
            query: The user query
            
        Returns:
            True if the query is asking for a detailed analysis/report
        """
        query_lower = query.lower()
        report_indicators = [
            "report", "analysis", "analyze", "sentiment", "impact", "effect", 
            "market impact", "detailed", "what does this mean for", "how will this affect",
            "annual report", "earnings report", "quarterly report", "statement", "press release"
        ]
        
        influential_figures = [
            "warren buffett", "elon musk", "jpmorgan", "goldman sachs", "federal reserve", 
            "fed", "jerome powell", "ray dalio", "rakesh jhunjhunwala", "cathie wood",
            "janet yellen", "james simons", "peter lynch", "george soros", "carl icahn",
            "investors", "analysts"
        ]
        
        # Check for report indicators
        is_report = any(indicator in query_lower for indicator in report_indicators)
        
        # Check for influential figures
        mentions_figure = any(figure in query_lower for figure in influential_figures)
        
        # Check for news references
        has_news = "news" in query_lower or "latest" in query_lower or "recent" in query_lower
        
        # If it mentions a figure and refers to news or has a report indicator, it's likely a report query
        return (mentions_figure and (has_news or is_report)) or is_report
    
    def handle_simple_query(self, query: str) -> Optional[str]:
        """
        Handle simple factual queries without web search.
        
        Args:
            query: The user query
            
        Returns:
            Answer to the query if it's simple, None otherwise
        """
        query_lower = query.lower()
        
        # Stock tickers
        if "ticker" in query_lower and "apple" in query_lower:
            return "Apple Inc.'s stock ticker is AAPL."
        elif "ticker" in query_lower and "microsoft" in query_lower:
            return "Microsoft Corporation's stock ticker is MSFT."
        elif "ticker" in query_lower and "google" in query_lower:
            return "Alphabet Inc.'s (Google's parent company) stock tickers are GOOGL and GOOG."
        elif "ticker" in query_lower and "amazon" in query_lower:
            return "Amazon.com Inc.'s stock ticker is AMZN."
        elif "ticker" in query_lower and "tesla" in query_lower:
            return "Tesla Inc.'s stock ticker is TSLA."
            
        # Common financial terms
        if "what is market cap" in query_lower or "what is market capitalization" in query_lower:
            return "Market capitalization (market cap) is the total value of a company's outstanding shares of stock, calculated by multiplying the stock's price by the total number of shares outstanding."
        
        if "what is p/e ratio" in query_lower:
            return "The price-to-earnings (P/E) ratio is a valuation metric that compares a company's stock price to its earnings per share (EPS). It indicates how much investors are willing to pay for each dollar of earnings."
        
        # No simple answer found
        return None
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """
        Format the response for display to the user.
        
        Args:
            result: The result dictionary from handle_query
            
        Returns:
            Formatted response string
        """
        if not result.get("is_finance_related", False):
            return self._format_simple_response(result["response"])
        
        # Handle stock chart queries
        if result.get("is_stock_query", False) and result.get("is_chart_query", False):
            chart_data = result.get("chart_data", {})
            ticker = result.get("ticker", "")
            
            # This just returns the data, the Streamlit app will handle rendering the image
            return chart_data

        # Handle stock comparison queries
        if result.get("is_stock_query", False) and result.get("is_comparison_query", False):
            comparison_data = result.get("comparison_data", {})
            tickers = result.get("tickers", [])
            
            # This just returns the data, the Streamlit app will handle rendering the image
            return comparison_data
            
        if result.get("is_simple_query", False) or not result.get("is_report_query", True):
            # For simple queries or non-report complex queries, return a formatted response
            if "response" in result:
                return self._format_simple_response(result["response"])
            
            # For complex queries that are not report requests, format as conversational
            analysis = result["analysis"]
            sentiment = analysis.get("sentiment", "UNKNOWN")
            summary = analysis.get("summary", "No summary available.")
            
            return self._format_conversational_response(summary, sentiment)
            
        # Format detailed report response
        return self._format_detailed_report(result)
    
    def _format_simple_response(self, response: str) -> str:
        """
        Format a simple response with appealing markdown.
        
        Args:
            response: The response text
            
        Returns:
            Formatted response string
        """
        # If response already has markdown formatting, clean it up
        if response.startswith("#") or "**" in response or "##" in response:
            # Clean up any markdown that might be visible to the user
            cleaned_response = response
            
            # Replace markdown headers with HTML
            cleaned_response = re.sub(r'^# (.*)$', r'<h1>\1</h1>', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'^## (.*)$', r'<h2>\1</h2>', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'^### (.*)$', r'<h3>\1</h3>', cleaned_response, flags=re.MULTILINE)
            
            # Replace markdown bold with HTML
            cleaned_response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', cleaned_response)
            
            # Replace markdown lists with HTML
            cleaned_response = re.sub(r'^\s*[-*]\s+(.*)$', r'<li>\1</li>', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'(<li>.*</li>)(\n<li>.*</li>)+', r'<ul>\1\2</ul>', cleaned_response, flags=re.DOTALL)
            
            # Replace markdown horizontal rule
            cleaned_response = re.sub(r'^---$', r'<hr>', cleaned_response, flags=re.MULTILINE)
            
            # Replace markdown italic
            cleaned_response = re.sub(r'\*(.*?)\*', r'<em>\1</em>', cleaned_response)
            
            return cleaned_response
            
        # Format as a simple response with emoji
        return f"""<h1>💬 Response</h1>

{response}

<hr>
<em>This information is provided for educational purposes only.</em>
"""
    
    def _format_conversational_response(self, summary: str, sentiment: str) -> str:
        """
        Format a conversational response with appealing markdown.
        
        Args:
            summary: The summary text
            sentiment: The sentiment (POSITIVE, NEGATIVE, NEUTRAL, MIXED)
            
        Returns:
            Formatted response string
        """
        # Choose emoji based on sentiment
        sentiment_emoji = "🔍"
        if sentiment == "POSITIVE":
            sentiment_emoji = "📈"
        elif sentiment == "NEGATIVE":
            sentiment_emoji = "📉"
        elif sentiment == "NEUTRAL":
            sentiment_emoji = "➡️"
        elif sentiment == "MIXED":
            sentiment_emoji = "🔄"
            
        return f"""<h1>Financial Insight {sentiment_emoji}</h1>

<h2>Summary</h2>
{summary}

<h2>Sentiment Analysis</h2>
Overall sentiment appears to be <strong>{sentiment.lower()}</strong>.

<hr>
<em>This analysis is based on publicly available information and should not be considered financial advice.</em>
"""
    
    def _format_detailed_report(self, result: Dict[str, Any]) -> str:
        """Format a detailed financial report with clean layout."""
        analysis = result["analysis"]
        
        # Get sentiment details with fallbacks
        sentiment = analysis.get("sentiment", "UNDETERMINED")
        confidence = analysis.get("confidence", "Insufficient data")
        market_impact = analysis.get("market_impact", "Unable to determine market impact")
        detailed_analysis = analysis.get("detailed_analysis", "No detailed analysis available")
        summary = analysis.get("summary", "Insufficient information for summary")
        recommendations = analysis.get("recommendations", "No specific recommendations available")
        
        # Format the sentiment section with appropriate emoji
        sentiment_emoji = "🔍"
        if sentiment == "POSITIVE":
            sentiment_emoji = "📈"
        elif sentiment == "NEGATIVE":
            sentiment_emoji = "📉"
        elif sentiment == "NEUTRAL":
            sentiment_emoji = "➡️"
        elif sentiment == "MIXED":
            sentiment_emoji = "🔄"
            
        # Process recommendations to convert to HTML list if it's a string with bullet points
        recommendations_html = recommendations
        if isinstance(recommendations, str):
            # Check if it contains bullet points or numbered lists
            if re.search(r'^\s*[-*•]\s+', recommendations, re.MULTILINE):
                # Convert bullet points to HTML list
                recommendations_html = re.sub(r'^\s*[-*•]\s+(.*)$', r'<li>\1</li>', recommendations, flags=re.MULTILINE)
                recommendations_html = f"<ul>{recommendations_html}</ul>"
            elif re.search(r'^\s*\d+\.\s+', recommendations, re.MULTILINE):
                # Convert numbered lists to HTML list
                recommendations_html = re.sub(r'^\s*\d+\.\s+(.*)$', r'<li>\1</li>', recommendations, flags=re.MULTILINE)
                recommendations_html = f"<ol>{recommendations_html}</ol>"
        
        # Process detailed analysis to convert to HTML list if it's a string with bullet points
        detailed_analysis_html = detailed_analysis
        if isinstance(detailed_analysis, str):
            # Check if it contains bullet points or numbered lists
            if re.search(r'^\s*[-*•]\s+', detailed_analysis, re.MULTILINE):
                # Convert bullet points to HTML list
                detailed_analysis_html = re.sub(r'^\s*[-*•]\s+(.*)$', r'<li>\1</li>', detailed_analysis, flags=re.MULTILINE)
                detailed_analysis_html = f"<ul>{detailed_analysis_html}</ul>"
            elif re.search(r'^\s*\d+\.\s+', detailed_analysis, re.MULTILINE):
                # Convert numbered lists to HTML list
                detailed_analysis_html = re.sub(r'^\s*\d+\.\s+(.*)$', r'<li>\1</li>', detailed_analysis, flags=re.MULTILINE)
                detailed_analysis_html = f"<ol>{detailed_analysis_html}</ol>"
            
        # Build the report
        formatted_response = f"""<h1>Financial Market Analysis {sentiment_emoji}</h1>

<h2>Key Findings</h2>

<strong>Sentiment:</strong> {sentiment}
<strong>Confidence Level:</strong> {confidence}

<h2>Summary</h2>
{summary}

<h2>Market Impact</h2>
{market_impact}

<h2>Analysis Details</h2>
{detailed_analysis_html}

<h2>Recommendations</h2>
{recommendations_html}

<hr>
<em>Analysis based on information gathered from market sources. This is for informational purposes only and should not be considered financial advice.</em>
"""
        
        # Only add sources if requested (typically not shown by default to keep output clean)
        # Uncomment to include sources:
        # formatted_response += "\n\n## Information Sources\n\n"
        # formatted_response += result.get("search_results", "No sources available.")
        
        return formatted_response 
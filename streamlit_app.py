import streamlit as st
from financial_agent import FinancialAgent
import os
from dotenv import load_dotenv
import base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Initialize the financial agent
financial_agent = FinancialAgent()

# Set page config
st.set_page_config(
    page_title="Financial Insights AI",
    page_icon="💹",
    layout="wide"
)

# Custom CSS for better formatting
st.markdown("""
<style>
    .report-container {
        background-color: #f0f6ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1e88e5;
        margin-bottom: 20px;
        color: #000000;
    }
    .chat-container {
        background-color: #e0f0ff;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 15px;
        color: #000000;
    }
    .sentiment-positive {
        color: #2e7d32;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #c62828;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #546e7a;
        font-weight: bold;
    }
    .sentiment-mixed {
        color: #6a1b9a;
        font-weight: bold;
    }
    .header-container {
        padding: 1.5rem;
        background: linear-gradient(90deg, #1e3a8a, #0d47a1);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    h1, h2, h3 {
        color: #0d47a1;
    }
    /* Fix markdown rendering of headers inside containers */
    .report-container h1, .report-container h2, .report-container h3 {
        color: #0d47a1;
        font-weight: bold;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    /* Fix all text color inside containers */
    .report-container p, .chat-container p {
        color: #333333;
    }
    /* Ensure lists are visible */
    .report-container ul, .report-container ol {
        color: #333333;
        margin-left: 1.5em;
    }
    /* Ensure links stand out */
    a {
        color: #0d47a1 !important;
        text-decoration: underline;
    }
    /* Stock data styling */
    .stock-container {
        background-color: #e8f5e9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #43a047;
        margin-bottom: 20px;
        color: #333333;
    }
    .stock-chart {
        padding: 10px;
        background-color: white;
        border-radius: 8px;
        margin-top: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .indicator-bullish {
        color: #2e7d32;
        font-weight: bold;
    }
    .indicator-bearish {
        color: #c62828;
        font-weight: bold;
    }
    .indicator-neutral {
        color: #546e7a;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-container"><div class="main-title">Financial Insights AI</div><div class="subtitle">Market sentiment analysis powered by AI</div></div>', unsafe_allow_html=True)

# Create columns for layout
col1, col2 = st.columns([7, 3])

with col2:
    st.markdown("### Example Queries")
    
    # Query categories with examples
    categories = {
        "Market Sentiment": [
            "What did Warren Buffett say in his latest annual report?",
            "What is the market sentiment around Tesla stock?",
            "How have Elon Musk's recent tweets affected the crypto market?"
        ],
        "Stock Data": [
            "What is the current price of AAPL?",
            "Show me a chart of Tesla stock",
            "Compare AAPL, MSFT, and GOOGL performance",
            "What are the technical indicators for NVDA?"
        ],
        "Financial News": [
            "What is the latest news about the Federal Reserve?",
            "How will the latest inflation report impact the market?",
            "What are analysts saying about the tech sector?"
        ],
        "Quick Info": [
            "What is the ticker symbol for Apple?",
            "What is market capitalization?",
            "What is P/E ratio?"
        ]
    }
    
    # Display categories and examples
    for category, examples in categories.items():
        with st.expander(category, expanded=category=="Stock Data"):
            for example in examples:
                if st.button(example, key=example):
                    st.session_state.query = example
                    st.session_state.run_query = True

with col1:
    # Query input
    st.markdown("### Ask a financial question")
    query = st.text_input(
        "Enter your question about markets, stocks, or financial figures",
        value=st.session_state.get("query", ""),
        placeholder="e.g., What is the current price of AAPL?",
        key="query_input"
    )
    
    # Run button with co-located help text
    col_btn, col_help = st.columns([1, 5])
    with col_btn:
        run_query = st.button("Analyze", type="primary")
    with col_help:
        st.caption("For stock charts, try questions like 'Show me a chart of AAPL' or 'Compare AAPL and MSFT'")
    
    # Initialize session state
    if "run_query" not in st.session_state:
        st.session_state.run_query = False
    
    # Process query
    if run_query or st.session_state.get("run_query", False):
        if query:
            # Reset the run query flag if it was set from a sidebar button
            st.session_state.run_query = False
            
            with st.spinner("Analyzing financial data..."):
                try:
                    # Process the query
                    result = financial_agent.handle_query(query)
                    response = financial_agent.format_response(result)
                    
                    # Handle stock chart requests
                    if result.get("is_stock_query", False) and result.get("is_chart_query", False):
                        chart_data = response  # The response is the chart data
                        ticker = result.get("ticker", "")
                        
                        if "error" in chart_data:
                            st.error(f"Error generating chart: {chart_data['error']}")
                        else:
                            # Display stock chart
                            st.markdown(f"## Stock Chart for {ticker}")
                            
                            # Convert base64 to image and display
                            image_bytes = base64.b64decode(chart_data["image"])
                            st.image(image_bytes, caption=f"{ticker} - {chart_data.get('period', '1y')}")
                            
                            # Display some basic info
                            st.markdown(f"**Latest Price**: ${chart_data.get('latest_price', 'N/A')}")
                            
                            # Display technical indicators if available
                            if "latest_sma20" in chart_data:
                                st.markdown("### Technical Indicators")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**SMA (20)**: ${chart_data.get('latest_sma20', 'N/A')}")
                                with col2:
                                    st.markdown(f"**SMA (50)**: ${chart_data.get('latest_sma50', 'N/A')}")
                    
                    # Handle stock comparison requests
                    elif result.get("is_stock_query", False) and result.get("is_comparison_query", False):
                        comparison_data = response  # The response is the comparison data
                        tickers = result.get("tickers", [])
                        
                        if "error" in comparison_data:
                            st.error(f"Error comparing stocks: {comparison_data['error']}")
                        else:
                            # Display comparison chart
                            st.markdown(f"## Stock Comparison: {', '.join(tickers)}")
                            
                            # Convert base64 to image and display
                            image_bytes = base64.b64decode(comparison_data["image"])
                            st.image(image_bytes, caption=f"Performance Comparison - {comparison_data.get('period', '1y')}")
                            
                            # Display performance summary
                            st.markdown("### Performance Summary")
                            performance = comparison_data.get("performance", {})
                            
                            # Create a neat performance table
                            performance_data = []
                            for tick, perf in performance.items():
                                sign = "+" if perf >= 0 else ""
                                status = "📈" if perf >= 0 else "📉"
                                performance_data.append({"Ticker": tick, "Change": f"{sign}{perf}%", "Status": status})
                                
                            if performance_data:
                                perf_df = pd.DataFrame(performance_data)
                                st.table(perf_df)
                    
                    # Different display for report vs. normal chat response
                    elif result.get("is_report_query", False) and not result.get("is_simple_query", False):
                        # Convert markdown to HTML for proper display
                        import re
                        html_content = response
                        # Convert headers
                        html_content = re.sub(r'# (.*)', r'<h1>\1</h1>', html_content)
                        html_content = re.sub(r'## (.*)', r'<h2>\1</h2>', html_content)
                        html_content = re.sub(r'### (.*)', r'<h3>\1</h3>', html_content)
                        # Convert bold
                        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
                        # Convert line breaks
                        html_content = html_content.replace('\n', '<br>')
                        
                        # Display report with proper styling
                        st.markdown(f'<div class="report-container">{html_content}</div>', unsafe_allow_html=True)
                    else:
                        # For stock data response, use a different style
                        if result.get("is_stock_query", False):
                            # Clean up markdown for HTML display
                            import re
                            html_content = response
                            # Convert headers
                            html_content = re.sub(r'# (.*)', r'<h1>\1</h1>', html_content)
                            html_content = re.sub(r'## (.*)', r'<h2>\1</h2>', html_content)
                            html_content = re.sub(r'### (.*)', r'<h3>\1</h3>', html_content)
                            # Convert bold
                            html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
                            # Style signals
                            html_content = re.sub(r'BULLISH', r'<span class="indicator-bullish">BULLISH</span>', html_content)
                            html_content = re.sub(r'BEARISH', r'<span class="indicator-bearish">BEARISH</span>', html_content)
                            html_content = re.sub(r'NEUTRAL', r'<span class="indicator-neutral">NEUTRAL</span>', html_content)
                            # Convert line breaks
                            html_content = html_content.replace('\n', '<br>')
                            
                            # Display stock data with proper styling
                            st.markdown(f'<div class="stock-container">{html_content}</div>', unsafe_allow_html=True)
                        else:
                            # Display simple chat response with better visibility
                            st.markdown(f'<div class="chat-container">{response}</div>', unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
        else:
            st.warning("Please enter a question about finance, business, or markets.")
    
    # Show usage tips for first-time users
    if "first_visit" not in st.session_state:
        st.session_state.first_visit = False
        with st.expander("Tips for getting the best results", expanded=True):
            st.markdown("""
            ### Query Types:
            
            - **Stock Data**: Ask about current prices, charts, or technical indicators
                - Example: "What is the current price of AAPL?" or "Show me a chart of Tesla"
            
            - **Stock Comparison**: Compare performance of multiple stocks
                - Example: "Compare AAPL, MSFT, and GOOGL"
            
            - **Market Sentiment**: Get analysis of statements from influential figures
                - Example: "What did Warren Buffett say in his latest annual report?"
            
            - **Simple Questions**: Get quick answers about financial terms
                - Example: "What is a P/E ratio?"
            """)

# Footer
st.markdown("---")
st.markdown("⚠️ **Disclaimer**: This is a prototype tool for educational purposes. The analysis is based on publicly available information and should not be used for financial decisions.")
st.markdown("Powered by [Gemini AI](https://ai.google.dev/) and [Yahoo Finance](https://finance.yahoo.com/)")

# Add chat history to keep track of previous interactions
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] 
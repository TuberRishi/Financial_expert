# Financial Insights AI

An intelligent AI-powered tool that performs sentiment analysis on financial statements, tweets, and news from influential figures in the finance world.

![Financial Insights AI](https://img.shields.io/badge/AI-Financial%20Insights-blue)

## Features

- **Smart Query Understanding**: Automatically detects when analysis or simple facts are needed
- **Dual Modes**:
  - **Analysis Mode**: Provides detailed sentiment analysis for market-impacting statements
  - **Chat Mode**: Gives direct answers to simple financial questions
- **Web Intelligence**: Gathers information from multiple sources to provide comprehensive analysis
- **Contextual Understanding**: Interprets implicit meanings in financial communications
- **Smart Formatting**: Delivers reports with clear sentiment indicators, summaries, and recommendations

## Use Cases

- Analyze statements from financial figures (Warren Buffett, Rakesh Jhunjhunwala, etc.)
- Analyze statements from influential figures (Elon Musk, Donald Trump, etc.)
- Understand market impact of news and reports
- Get quick information about financial terms and stock tickers

## Screenshot

![App Screenshot](https://via.placeholder.com/728x400.png?text=Financial+Insights+AI+Screenshot)
*(Replace with actual screenshot)*

## Getting Started

See [how_to_run.md](how_to_run.md) for detailed setup and usage instructions.

Quick start:
```bash
# Install dependencies
pip install -r requirements.txt

# Set up API key in .env file
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env

# Run the application
streamlit run streamlit_app.py
```

## Technology Stack

- **Frontend**: Streamlit
- **AI**: Google Gemini AI
- **Web Search**: DuckDuckGo Search API
- **Language**: Python 3.8+

## Limitations

- Only answers finance, business, or market-related questions
- Performance depends on the quality of web search results
- Requires an active internet connection
- This is a prototype for informational purposes only

## Contributing

Feel free to submit issues or pull requests to improve the functionality or fix bugs. 
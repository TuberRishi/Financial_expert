# How to Run the Financial Insights AI

## Prerequisites

1. Python 3.8 or higher
2. Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))

## Setup Instructions

1. **Clone the repository**

2. **Create a virtual environment (recommended)**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - MacOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Set up your environment variables**
   - Copy the `.env.example` file to `.env`
   - Add your Google API key to the `.env` file:
     ```
     GOOGLE_API_KEY=your_gemini_api_key_here
     ```

6. **Run the application**
   ```
   streamlit run streamlit_app.py
   ```
   - Your browser should automatically open to: http://localhost:8501
   - If not, copy and paste the URL into your browser

## Using the Application

### Types of Queries
The application can handle two types of queries:
1. **Simple questions** - Quick fact-based questions about finance (e.g., "What is the ticker for Apple?")
2. **Analysis requests** - Detailed sentiment analysis of financial statements or market impact (e.g., "What did Warren Buffett say in his latest annual report?")

### Features
- **Categorized examples** in the sidebar to help you get started
- **Detailed reports** for analysis queries with sentiment assessment
- **Conversational responses** for simple financial questions

## Troubleshooting

1. **API Key Issues**
   - Make sure your API key is correctly set in the `.env` file
   - Verify that your API key has access to the Gemini model

2. **Dependencies Issues**
   - Try reinstalling the dependencies:
     ```
     pip install -r requirements.txt --force-reinstall
     ```

3. **Display Issues**
   - If you encounter display problems, try:
     - Refreshing the browser
     - Using a different browser
     - Running with debug mode: `streamlit run streamlit_app.py --debug` 
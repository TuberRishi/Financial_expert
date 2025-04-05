import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Dict, Any, Tuple, List

load_dotenv()

class SentimentAnalyzer:
    """Sentiment analysis module using Gemini API."""
    
    def __init__(self):
        # Initialize the Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        
        # Get available models
        self.model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    
    def is_finance_related(self, query: str) -> bool:
        """
        Check if the query is related to finance, business, or markets.
        
        Args:
            query: The user query
            
        Returns:
            True if the query is finance-related, False otherwise
        """
        prompt = f"""
        Determine if the following query is related to finance, business, or markets. 
        If it asks about stocks, investments, financial figures, companies, market trends,
        economic news, or similar topics, respond with "YES". Otherwise, respond with "NO".
        
        Query: {query}
        
        Answer only with YES or NO:
        """
        
        response = self.model.generate_content(prompt)
        answer = response.text.strip().upper()
        
        return "YES" in answer
    
    def analyze_sentiment(self, search_results: str, user_query: str) -> Dict[str, Any]:
        """
        Analyze the sentiment of financial information.
        
        Args:
            search_results: The consolidated search results
            user_query: The original user query
            
        Returns:
            Dictionary containing detailed analysis and sentiment
        """
        prompt = f"""
        You are a financial expert specializing in sentiment analysis. Analyze the following information related to this query: "{user_query}"
        
        INFORMATION:
        {search_results}
        
        Please provide a structured analysis with these exact headings and format:
        
        1. SENTIMENT: [Clearly state if the sentiment is POSITIVE, NEGATIVE, NEUTRAL, or MIXED. Be definitive.]
        
        2. CONFIDENCE: [State Low, Medium, or High]
        
        3. MARKET IMPACT: [Analyze potential impact on relevant markets, companies, or industries]
        
        4. DETAILED ANALYSIS: [Provide reasoning, analyze both explicit and implicit meanings]
        
        5. SUMMARY: [Give a 2-3 sentence summary]
        
        6. RECOMMENDATIONS: [Provide 2-3 actionable insights]
        
        Use only the information provided. If there is truly insufficient information for any section, indicate "Insufficient information available" in that section.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text
            
            # Initialize sections with default values
            sections = {
                "sentiment": "Unable to determine sentiment",
                "confidence": "Low",
                "market_impact": "Insufficient information to assess market impact",
                "detailed_analysis": "No detailed analysis available",
                "summary": "Insufficient information to provide a summary",
                "recommendations": "Unable to provide recommendations with available information"
            }
            
            # Define section markers
            markers = [
                ("1. SENTIMENT:", "sentiment"),
                ("2. CONFIDENCE:", "confidence"),
                ("3. MARKET IMPACT:", "market_impact"),
                ("4. DETAILED ANALYSIS:", "detailed_analysis"),
                ("5. SUMMARY:", "summary"),
                ("6. RECOMMENDATIONS:", "recommendations")
            ]
            
            # Split the text by the numbered sections
            for i, (marker, key) in enumerate(markers):
                if marker in result:
                    parts = result.split(marker, 1)
                    if len(parts) > 1:
                        # Find the end of this section (start of next section or end of text)
                        section_text = parts[1]
                        for next_marker, _ in markers[i+1:]:
                            if next_marker in section_text:
                                section_text = section_text.split(next_marker, 1)[0]
                                break
                        
                        # Clean up and store the section text
                        cleaned_text = section_text.strip()
                        if cleaned_text:
                            sections[key] = cleaned_text
            
            # Determine sentiment label based on content
            sentiment = sections["sentiment"].lower()
            if "positive" in sentiment:
                sections["sentiment"] = "POSITIVE"
            elif "negative" in sentiment:
                sections["sentiment"] = "NEGATIVE"
            elif "neutral" in sentiment:
                sections["sentiment"] = "NEUTRAL"
            elif "mixed" in sentiment:
                sections["sentiment"] = "MIXED"
            
            return sections
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            # Return default sections if analysis fails
            return {
                "sentiment": "UNDETERMINED",
                "confidence": "Unable to assess confidence",
                "market_impact": f"Error during analysis: {str(e)}",
                "detailed_analysis": "Analysis failed",
                "summary": "Unable to generate summary",
                "recommendations": "No recommendations available"
            } 
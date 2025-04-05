from duckduckgo_search import DDGS
from typing import List, Dict, Any, Optional
import re
import requests
from urllib.parse import urlparse

class SearchTool:
    """Tool for searching the web and retrieving relevant information."""
    
    def __init__(self):
        self.ddgs = DDGS()
        
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search the web for the given query.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results with title, body, and href
        """
        try:
            results = list(self.ddgs.text(query, max_results=max_results))
            return results
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_content(self, url: str) -> Optional[str]:
        """
        Get the text content from a URL.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            The text content of the URL or None if failed
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            # Simple extraction - in a real app, use a proper parser
            text = re.sub(r'<.*?>', ' ', response.text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_domain(self, url: str) -> str:
        """Extract the domain name from a URL."""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain
        
    def formulate_search_query(self, user_query: str) -> str:
        """
        Enhance the user query for better search results.
        
        Args:
            user_query: The original user query
            
        Returns:
            Enhanced search query
        """
        # Extract potential entities (people, companies)
        entities = re.findall(r'"([^"]*)"', user_query)
        
        if "annual report" in user_query.lower() or "yearly report" in user_query.lower():
            if entities:
                return f"{entities[0]} latest annual report financial analysis"
            else:
                return user_query + " latest financial analysis"
                
        if "news" in user_query.lower():
            if entities:
                return f"{entities[0]} latest financial news market impact"
            else:
                return user_query + " financial market impact"
        
        if "tweet" in user_query.lower() or "statement" in user_query.lower():
            if entities:
                return f"{entities[0]} recent statements tweets financial market"
            else:
                return user_query + " recent financial statements market impact"
        
        # Default enhancement
        return user_query + " financial market analysis"
        
    def search_and_consolidate(self, user_query: str, max_results: int = 5) -> str:
        """
        Search and consolidate information from multiple sources.
        
        Args:
            user_query: The original user query
            max_results: Maximum number of search results to process
            
        Returns:
            Consolidated information
        """
        search_query = self.formulate_search_query(user_query)
        results = self.search(search_query, max_results)
        
        if not results:
            return "No information found. Please try a different query or check your internet connection."
        
        consolidated_info = []
        consolidated_info.append(f"SEARCH QUERY: {search_query}\n\n")
        
        # Get content from top 3 results for better analysis
        for i, result in enumerate(results[:3]):
            domain = self.extract_domain(result['href'])
            
            # Try to get more detailed content (limited to prevent overwhelming)
            try:
                additional_content = self.get_content(result['href'])
                additional_content = additional_content[:5000] if additional_content else "Content extraction failed."
            except:
                additional_content = "Content extraction failed."
            
            # Add structured information
            consolidated_info.append(f"SOURCE {i+1}: {result['title']} ({domain})\n")
            consolidated_info.append(f"URL: {result['href']}\n")
            consolidated_info.append(f"SUMMARY: {result['body']}\n")
            consolidated_info.append(f"CONTENT EXCERPT: {additional_content[:1500]}...\n\n")
        
        # Add remaining results as summaries
        if len(results) > 3:
            consolidated_info.append("ADDITIONAL SOURCES:\n")
            for i, result in enumerate(results[3:], start=4):
                domain = self.extract_domain(result['href'])
                consolidated_info.append(f"SOURCE {i}: {result['title']} ({domain})\n")
                consolidated_info.append(f"SUMMARY: {result['body']}\n\n")
        
        return "".join(consolidated_info) 
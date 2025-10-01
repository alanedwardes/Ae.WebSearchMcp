#!/usr/bin/env python3
"""
Web Search MCP HTTP Server

An HTTP-based Model Context Protocol (MCP) server that provides web search functionality.
This server can be used with OpenWebUI or other MCP-compatible clients.

The server automatically detects all configured search engines and randomly selects one
for each search request, providing load balancing and redundancy.

Usage:
    python web_search_mcp.py

Environment Variables:
    GOOGLE_API_KEY: Your Google Custom Search API key
    GOOGLE_SEARCH_ENGINE_ID: Your Google Custom Search Engine ID
    OLLAMA_API_KEY: Your Ollama API key (optional, for hosted Ollama service)

Note: At least one search engine must be configured. The server will automatically
detect all available engines and randomly select one for each search request.
"""

import asyncio
import logging
import os
import random
import signal
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
from ollama import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Web Search MCP Server", host="0.0.0.0")


class SearchResult:
    """Represents a single search result from any search engine."""
    
    def __init__(self, link: str, title: Optional[str] = None, snippet: Optional[str] = None):
        self.link = link
        self.title = title
        self.snippet = snippet
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "link": self.link,
            "title": self.title,
            "snippet": self.snippet
        }


class SearchEngineProvider(ABC):
    """Abstract base class for search engine providers."""
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        count: int = 10
    ) -> List[SearchResult]:
        """
        Perform a search query.
        
        Args:
            query: The search query
            count: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        pass


class GoogleSearchProvider(SearchEngineProvider):
    """Google Custom Search API implementation."""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
    
    async def search(
        self, 
        query: str, 
        count: int = 10
    ) -> List[SearchResult]:
        """
        Search Google using the Custom Search API.
        
        Args:
            query: The search query
            count: Number of results to return (max 10 per request)
            
        Returns:
            List of SearchResult objects
        """
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(count, 10)  # Google API max is 10 per request
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    
                    results.append(SearchResult(link, title, snippet))
                
                return results[:count]
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during Google search: {e}")
            raise Exception(f"Failed to search Google: {e}")
        except Exception as e:
            logger.error(f"Error during Google search: {e}")
            raise Exception(f"Search failed: {e}")


class OllamaSearchProvider(SearchEngineProvider):
    """Ollama web search API implementation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = Client()
        if api_key:
            self.client.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def search(
        self, 
        query: str, 
        count: int = 10
    ) -> List[SearchResult]:
        """
        Search using Ollama's web search API.
        
        Args:
            query: The search query
            count: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            # Use asyncio.to_thread to run the synchronous ollama client in a thread
            result = await asyncio.to_thread(
                self.client.web_search, 
                query=query, 
                max_results=count
            )
            
            # Convert ollama response to our SearchResult format
            results = []
            if hasattr(result, 'results') and result.results:
                for item in result.results:
                    link = getattr(item, 'url', '')
                    title = getattr(item, 'title', '')
                    snippet = getattr(item, 'content', '')
                    
                    results.append(SearchResult(link, title, snippet))
            
            return results[:count]
                
        except Exception as e:
            logger.error(f"Error during Ollama search: {e}")
            raise Exception(f"Ollama search failed: {e}")


def detect_available_engines() -> List[SearchEngineProvider]:
    """Detect all available search engines based on environment variables."""
    available_engines = []
    
    # Check for Google Custom Search configuration
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    if google_api_key and google_search_engine_id:
        available_engines.append(GoogleSearchProvider(google_api_key, google_search_engine_id))
        logger.info("Google Custom Search engine detected and configured")
    
    # Check for Ollama configuration
    ollama_api_key = os.getenv("OLLAMA_API_KEY")
    if ollama_api_key or True:  # Ollama can work without API key (local instance)
        available_engines.append(OllamaSearchProvider(ollama_api_key))
        logger.info("Ollama search engine detected and configured")
    
    return available_engines


def get_available_search_providers() -> List[SearchEngineProvider]:
    """Get all available search providers."""
    available_engines = detect_available_engines()
    
    if not available_engines:
        raise Exception("No search engines configured. Please set up at least one of: GOOGLE_API_KEY+GOOGLE_SEARCH_ENGINE_ID or OLLAMA_API_KEY")
    
    return available_engines


def get_random_search_provider() -> SearchEngineProvider:
    """Get a randomly selected search provider from available engines."""
    available_engines = get_available_search_providers()
    
    selected_engine = random.choice(available_engines)
    engine_name = "Google" if isinstance(selected_engine, GoogleSearchProvider) else "Ollama"
    logger.info(f"Selected search engine: {engine_name}")
    
    return selected_engine


@mcp.tool()
async def web_search(
    query: str,
    count: int = 10
) -> str:
    """
    Search the web using a randomly selected search engine with fallback support.
    If the selected engine fails or returns no results, another engine will be tried.
    
    Args:
        query: The search query to execute
        count: Number of results to return (default: 10, max: 10)
        
    Returns:
        Formatted search results as text
    """
    logger.info(f"Searching web for: {query}")
    
    # Get max snippet length from environment variable
    max_snippet_length = None
    try:
        max_snippet_length = int(os.getenv("MAX_SNIPPET_LENGTH", "512"))
    except ValueError:
        logger.warning("Invalid MAX_SNIPPET_LENGTH value, using default of 512")
        max_snippet_length = 512
    
    # Get all available search providers
    available_providers = get_available_search_providers()
    
    # Create a shuffled list to try engines in random order
    providers_to_try = available_providers.copy()
    random.shuffle(providers_to_try)
    
    # Try each provider until we get results or exhaust all options
    for attempt, provider in enumerate(providers_to_try, 1):
        engine_name = "Google" if isinstance(provider, GoogleSearchProvider) else "Ollama"
        
        try:
            logger.info(f"Attempt {attempt}: Using {engine_name} search engine")
            
            # Perform the search
            results = await provider.search(query, count)
            
            if results:
                logger.info(f"Successfully found {len(results)} results using {engine_name}")
                
                # Apply snippet length limit to all results
                for result in results:
                    if result.snippet and max_snippet_length and len(result.snippet) > max_snippet_length:
                        result.snippet = result.snippet[:max_snippet_length - 3] + "..."
                
                # Format results as text
                formatted_results = []
                for i, result in enumerate(results, 1):
                    formatted_results.append(f"{i}. **{result.title}**\n   {result.snippet}\n   {result.link}\n")
                
                response_text = f"Web Search Results for '{query}' (via {engine_name}):\n\n" + "\n".join(formatted_results)
                return response_text
            else:
                logger.warning(f"No results returned from {engine_name}, trying next engine...")
                
        except Exception as e:
            logger.error(f"Error with {engine_name} search engine: {e}")
            if attempt < len(providers_to_try):
                logger.info(f"Trying next available search engine...")
            else:
                logger.error(f"All search engines failed. Last error: {e}")
    
    # If we get here, all engines failed or returned no results
    return f"No results found for query: {query}. All available search engines were tried."


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)


def main():
    """Main entry point for the MCP HTTP server."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Web Search MCP HTTP Server...")
    
    # Detect and log available search engines
    try:
        available_engines = detect_available_engines()
        if not available_engines:
            logger.error("No search engines configured. Please set up at least one of:")
            logger.error("  - GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID for Google Custom Search")
            logger.error("  - OLLAMA_API_KEY for Ollama search (or run local Ollama instance)")
            sys.exit(1)
        
        logger.info(f"Detected {len(available_engines)} available search engine(s):")
        for engine in available_engines:
            if isinstance(engine, GoogleSearchProvider):
                logger.info("  - Google Custom Search")
            elif isinstance(engine, OllamaSearchProvider):
                logger.info("  - Ollama Search")
        
        logger.info("Search engine will be randomly selected for each request")
        
    except Exception as e:
        logger.error(f"Error detecting search engines: {e}")
        sys.exit(1)
    
    logger.info("Server will run on default port (FastMCP handles this automatically)")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Run the HTTP server
        mcp.run(transport='streamable-http')
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
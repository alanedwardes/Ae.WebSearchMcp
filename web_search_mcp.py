#!/usr/bin/env python3
"""
Web Search MCP HTTP Server

An HTTP-based Model Context Protocol (MCP) server that provides web search functionality.
This server can be used with OpenWebUI or other MCP-compatible clients.

Usage:
    python google_search_mcp.py

Environment Variables:
    GOOGLE_API_KEY: Your Google Custom Search API key
    GOOGLE_SEARCH_ENGINE_ID: Your Google Custom Search Engine ID
    OLLAMA_API_KEY: Your Ollama API key (optional, for hosted Ollama service)
    SEARCH_PROVIDER: Search provider to use ("google" or "ollama", defaults to "google")
"""

import asyncio
import json
import logging
import os
import signal
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

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


# Global search provider instance
_search_provider: Optional[SearchEngineProvider] = None


def get_search_provider() -> SearchEngineProvider:
    """Get the configured search provider."""
    global _search_provider
    if _search_provider is None:
        # Get the preferred search provider
        provider_type = os.getenv("SEARCH_PROVIDER", "google").lower()
        
        if provider_type == "ollama":
            # Use Ollama search provider
            ollama_api_key = os.getenv("OLLAMA_API_KEY")
            _search_provider = OllamaSearchProvider(ollama_api_key)
        else:
            # Default to Google search provider
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not api_key or not search_engine_id:
                raise Exception("Google API credentials not configured. Set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables.")
            
            _search_provider = GoogleSearchProvider(api_key, search_engine_id)
    
    return _search_provider


@mcp.tool()
async def web_search(
    query: str,
    count: int = 10
) -> str:
    """
    Search the web using the configured search engine.
    
    Args:
        query: The search query to execute
        count: Number of results to return (default: 10, max: 10)
        
    Returns:
        Formatted search results as text
    """
    try:
        logger.info(f"Searching web for: {query}")
        
        # Get the search provider
        provider = get_search_provider()
        
        # Perform the search
        results = await provider.search(query, count)
        
        if not results:
            return f"No results found for query: {query}"
        
        # Format results as text
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(f"{i}. **{result.title}**\n   {result.snippet}\n   {result.link}\n")
        
        response_text = f"Web Search Results for '{query}':\n\n" + "\n".join(formatted_results)
        return response_text
        
    except Exception as e:
        logger.error(f"Error in web_search tool: {e}")
        return f"Error: {str(e)}"


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal, exiting...")
    sys.exit(0)


def main():
    """Main entry point for the MCP HTTP server."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get the preferred search provider
    provider_type = os.getenv("SEARCH_PROVIDER", "google").lower()
    
    logger.info("Starting Web Search MCP HTTP Server...")
    
    if provider_type == "ollama":
        # Check Ollama configuration
        ollama_api_key = os.getenv("OLLAMA_API_KEY")
        logger.info(f"Search Provider: Ollama")
        if ollama_api_key:
            logger.info(f"Ollama API Key: {'*' * 8}{ollama_api_key[-4:]}")
        else:
            logger.info("Ollama API Key: Not set (using local Ollama instance)")
    else:
        # Check Google configuration
        google_api_key = os.getenv("GOOGLE_API_KEY")
        google_search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not google_api_key or not google_search_engine_id:
            logger.error("Please set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables")
            logger.error("Or set SEARCH_PROVIDER=ollama to use Ollama search")
            sys.exit(1)
        
        logger.info(f"Search Provider: Google Custom Search")
        logger.info(f"Google API Key: {'*' * 8}{google_api_key[-4:] if google_api_key else 'Not set'}")
        logger.info(f"Search Engine ID: {google_search_engine_id[:8]}...{google_search_engine_id[-4:] if google_search_engine_id else 'Not set'}")
    
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
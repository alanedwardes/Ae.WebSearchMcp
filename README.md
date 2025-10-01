# Web Search MCP Server

A Model Context Protocol (MCP) HTTP server that provides web search functionality using either Google Custom Search API or Ollama's web search API. This server can be integrated with OpenWebUI or other MCP-compatible clients to enable web search capabilities.

## Features

- **Multiple Search Providers**: Support for both Google Custom Search API and Ollama web search
- **Web Search Tool**: Search the web using your preferred search provider
- **MCP Protocol**: Compatible with Model Context Protocol for AI assistant integration
- **HTTP Server**: Runs as an HTTP server using FastMCP
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Configurable Results**: Adjustable number of search results (up to 10 per query)

## Prerequisites

- Python 3.13+ (or Docker)
- **For Google Search**: Google Custom Search API key and Search Engine ID
- **For Ollama Search**: Ollama API key (optional, for hosted service) or local Ollama instance

## Setup

### 1. Choose Your Search Provider

You can use either Google Custom Search API or Ollama's web search API. Set the `SEARCH_PROVIDER` environment variable to choose:

- `SEARCH_PROVIDER=google` (default) - Uses Google Custom Search API
- `SEARCH_PROVIDER=ollama` - Uses Ollama's web search API

### 2. Get Google API Credentials (if using Google provider)

#### Step 1: Create a Google Programmable Search Engine

1. Go to the [Google Programmable Search Engine Control Panel](https://programmablesearchengine.google.com/controlpanel/all)
2. Sign in with your Google account
3. Click "Add" to create a new search engine
4. In the "Sites to search" field, specify the websites you want to include:
   - For general web search: enter `*` (searches the entire web)
   - For specific sites: enter the domain(s) you want to search
5. Provide a name for your search engine
6. Click "Create" to finalize the setup
7. After creation, go to the "Setup" section and note down the "Search engine ID" (also called "cx" parameter)

#### Step 2: Enable the Custom Search JSON API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Library"
4. Search for "Custom Search API" and click on it
5. Click "Enable" to activate the API for your project

#### Step 3: Create API Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "API Key"
3. Copy the generated API key for use in your application
4. (Recommended) Restrict the API key to the Custom Search API for security:
   - Click on the API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Choose "Custom Search API" from the list

### 3. Get Ollama API Key (if using Ollama provider)

1. Sign up for an Ollama account at [ollama.com](https://ollama.com)
2. Go to your account settings and generate an API key
3. Alternatively, you can use a local Ollama instance without an API key

### 4. Environment Variables

Set the following environment variables based on your chosen provider:

**For Google Search (Windows PowerShell):**
```powershell
$env:SEARCH_PROVIDER="google"
$env:GOOGLE_API_KEY="your_google_api_key_here"
$env:GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

**For Google Search (Linux/macOS):**
```bash
export SEARCH_PROVIDER="google"
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

**For Ollama Search (Windows PowerShell):**
```powershell
$env:SEARCH_PROVIDER="ollama"
$env:OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
```

**For Ollama Search (Linux/macOS):**
```bash
export SEARCH_PROVIDER="ollama"
export OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
```

## Installation

### Option 1: Local Python Installation

1. Clone the repository:
```bash
git clone https://github.com/alanedwardes/Ae.WebSearchMcp.git
cd Ae.WebSearchMcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (see above section)

4. Run the server:
```bash
python web_search_mcp.py
```

### Option 2: Docker Deployment

1. Clone the repository:
```bash
git clone https://github.com/alanedwardes/Ae.WebSearchMcp.git
cd Ae.WebSearchMcp
```

2. Create a `.env` file in the project root with your credentials:

**For Google Search:**
```bash
# .env file
SEARCH_PROVIDER=google
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**For Ollama Search:**
```bash
# .env file
SEARCH_PROVIDER=ollama
OLLAMA_API_KEY=your_ollama_api_key_here  # Optional for hosted service
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

The server will be available at `http://localhost:8085`

## Usage

### MCP Tool: web_search

The server provides a single MCP tool called `web_search` with the following parameters:

- **query** (string, required): The search query to execute
- **count** (integer, optional): Number of results to return (default: 10, max: 10)

### Example Usage

When integrated with an MCP client, you can use the web search functionality like this:

```
Search for "Python web scraping tutorials"
```

The tool will return formatted search results including:
- Title
- Snippet/description
- URL

## API Response Format

The `web_search` tool returns formatted text with search results:

```
Web Search Results for 'your query':

1. **Result Title**
   Result snippet/description
   https://example.com/result-url

2. **Another Result Title**
   Another result snippet
   https://example.com/another-url
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SEARCH_PROVIDER` | Search provider to use ("google" or "ollama") | No | "google" |
| `GOOGLE_API_KEY` | Your Google Custom Search API key | Yes (if using Google) | - |
| `GOOGLE_SEARCH_ENGINE_ID` | Your Google Custom Search Engine ID | Yes (if using Google) | - |
| `OLLAMA_API_KEY` | Your Ollama API key (for hosted service) | No (if using Ollama) | - |

### Docker Configuration

The Docker setup includes:
- **Port**: 8085 (mapped to container port 8000)
- **Restart Policy**: unless-stopped
- **Security**: Runs as non-root user

## Development

### Project Structure

```
Ae.WebSearchMcp/
├── web_search_mcp.py    # Main MCP server implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker container configuration
├── compose.yaml        # Docker Compose configuration
└── README.md          # This file
```

### Key Components

- **SearchEngineProvider**: Abstract base class for search providers
- **GoogleSearchProvider**: Google Custom Search API implementation
- **OllamaSearchProvider**: Ollama web search API implementation
- **SearchResult**: Data class for search results
- **FastMCP Server**: HTTP server using the FastMCP framework

## Troubleshooting

### Common Issues

1. **API Key Not Set**: 
   - For Google: Ensure `GOOGLE_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID` environment variables are set
   - For Ollama: `OLLAMA_API_KEY` is optional for hosted service
2. **Search Provider Not Configured**: Verify `SEARCH_PROVIDER` is set to "google" or "ollama"
3. **API Quota Exceeded**: Check your API quota limits (Google or Ollama)
4. **Network Issues**: Ensure the server can reach the API endpoints
5. **Ollama Connection Issues**: If using local Ollama, ensure the service is running

### Logs

The server logs important information including:
- Startup confirmation
- Search queries being executed
- API errors and exceptions

# Web Search MCP Server

A Model Context Protocol (MCP) HTTP server that provides web search functionality using multiple search engines. The server automatically detects all configured search engines and randomly selects one for each search request, with fallback support - if the selected engine fails or returns no results, another engine will be automatically tried. This server can be integrated with OpenWebUI or other MCP-compatible clients to enable web search capabilities.

## Features

- **Multiple Search Providers**: Support for various search engines including Google Custom Search API and Ollama web search
- **Automatic Engine Detection**: Automatically detects all configured search engines at startup
- **Random Load Balancing**: Randomly selects from available engines for each search request
- **Fallback Support**: If the selected engine fails or returns no results, another engine will be automatically tried
- **Web Search Tool**: Search the web using any of the configured search providers
- **MCP Protocol**: Compatible with Model Context Protocol for AI assistant integration
- **HTTP Server**: Runs as an HTTP server using FastMCP
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Configurable Results**: Adjustable number of search results (up to 10 per query)

## Prerequisites

- Python 3.13+ (or Docker)
- **For Google Search**: Google Custom Search API key and Search Engine ID
- **For Ollama Search**: Ollama API key (optional, for hosted service) or local Ollama instance
- **For other search engines**: See their respective documentation for required credentials

## Setup

### 1. Configure Search Engines

The server automatically detects all configured search engines and randomly selects one for each search request. Currently supported engines include:

- **Google Custom Search API**: Requires `GOOGLE_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`
- **Ollama Web Search API**: Requires `OLLAMA_API_KEY` (optional for local instances)

**Note**: At least one search engine must be configured. If multiple engines are configured, the server will randomly select one for each search request, providing load balancing and redundancy. If the selected engine fails or returns no results, another engine will be tried automatically. Additional search engines may be added in future releases.

### 2. Get Google API Credentials (if using Google search)

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

### 3. Get Ollama API Key (if using Ollama search)

1. Sign up for an Ollama account at [ollama.com](https://ollama.com)
2. Go to your account settings and generate an API key
3. Alternatively, you can use a local Ollama instance without an API key

### 4. Environment Variables

Set the environment variables for the search engines you want to use. The server will automatically detect all configured engines and randomly select one for each search request with fallback support. Each search engine has its own specific environment variables.

**For Google Search (Windows PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_google_api_key_here"
$env:GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

**For Google Search (Linux/macOS):**
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

**For Ollama Search (Windows PowerShell):**
```powershell
$env:OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
```

**For Ollama Search (Linux/macOS):**
```bash
export OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
```

**For Multiple Search Engines (Windows PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_google_api_key_here"
$env:GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
$env:OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
# Add other search engine environment variables as needed
```

**For Multiple Search Engines (Linux/macOS):**
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
export OLLAMA_API_KEY="your_ollama_api_key_here"  # Optional for hosted service
# Add other search engine environment variables as needed
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
PORT=8000  # Optional: custom host port (default: 8000)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**For Ollama Search:**
```bash
# .env file
PORT=8000  # Optional: custom host port (default: 8000)
OLLAMA_API_KEY=your_ollama_api_key_here  # Optional for hosted service
```

**For Multiple Search Engines:**
```bash
# .env file
PORT=8000  # Optional: custom host port (default: 8000)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
OLLAMA_API_KEY=your_ollama_api_key_here  # Optional for hosted service
# Add other search engine environment variables as needed
```

3. Run with Docker Compose:
```bash
docker-compose up -d
```

The server will be available at `http://localhost:8000`

## Usage

### MCP Tool: web_search

The server provides a single MCP tool called `web_search` with the following parameters:

- **query** (string, required): The search query to execute
- **count** (integer, optional): Number of results to return (default: 10, max: 10)

The server will automatically randomly select a search engine for each request, with fallback support if the selected engine fails or returns no results.

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
| `GOOGLE_API_KEY` | Your Google Custom Search API key | Yes (if using Google) | - |
| `GOOGLE_SEARCH_ENGINE_ID` | Your Google Custom Search Engine ID | Yes (if using Google) | - |
| `OLLAMA_API_KEY` | Your Ollama API key (for hosted service) | No (if using Ollama) | - |
| `PORT` | Host port for Docker container mapping | No | 8000 |

**Note**: At least one search engine must be configured. The server automatically detects all configured engines and randomly selects one for each search request, providing load balancing and redundancy. If the selected engine fails or returns no results, another engine will be tried automatically. Additional search engines may be added in future releases with their own environment variables.

### Docker Configuration

The Docker setup includes:
- **Port**: Configurable via `PORT` environment variable (default: 8000, mapped to container port 8000)
- **Restart Policy**: unless-stopped
- **Security**: Runs as non-root user

#### Configurable Port

You can customize the host port mapping using the `PORT` environment variable:

**Default behavior** (no environment variable set):
- Host port: 8000
- Container port: 8000

**Custom host port**:
```bash
# Set custom host port
export PORT=9090
docker-compose up -d
```
This maps host port 9090 to container port 8000.

**Using .env file**:
```bash
# .env file
PORT=9090
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

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

The modular design allows for easy addition of new search engine providers by implementing the `SearchEngineProvider` interface.

## Troubleshooting

### Common Issues

1. **No Search Engines Configured**: 
   - Ensure at least one search engine is configured with the required environment variables
   - For Google: Set `GOOGLE_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID`
   - For Ollama: `OLLAMA_API_KEY` is optional for hosted service
   - For other engines: Check their specific documentation for required environment variables
2. **API Quota Exceeded**: Check your API quota limits (Google or Ollama)
3. **Network Issues**: Ensure the server can reach the API endpoints
4. **Ollama Connection Issues**: If using local Ollama, ensure the service is running

### Logs

The server logs important information including:
- Startup confirmation and detected search engines
- Random engine selection for each search request
- Fallback attempts when engines fail or return no results
- Search queries being executed
- API errors and exceptions
- Success/failure status for each engine attempt

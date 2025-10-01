# Web Search MCP Server

A Model Context Protocol (MCP) HTTP server that provides web search functionality using Google Custom Search API. This server can be integrated with OpenWebUI or other MCP-compatible clients to enable web search capabilities.

## Features

- **Web Search Tool**: Search the web using Google Custom Search API
- **MCP Protocol**: Compatible with Model Context Protocol for AI assistant integration
- **HTTP Server**: Runs as an HTTP server using FastMCP
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Configurable Results**: Adjustable number of search results (up to 10 per query)

## Prerequisites

- Python 3.13+ (or Docker)
- Google Custom Search API key
- Google Custom Search Engine ID

## Setup

### 1. Get Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Custom Search API
4. Create credentials (API Key)
5. Create a Custom Search Engine at [Google Custom Search](https://cse.google.com/)
6. Note down your API key and Search Engine ID

### 2. Environment Variables

Set the following environment variables:

```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id_here"
```

## Installation

### Option 1: Local Python Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Ae.WebSearchMcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables (see above)

4. Run the server:
```bash
python web_search_mcp.py
```

### Option 2: Docker Deployment

1. Clone the repository:
```bash
git clone <repository-url>
cd Ae.WebSearchMcp
```

2. Create a `.env` file with your credentials:
```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
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

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Your Google Custom Search API key | Yes |
| `GOOGLE_SEARCH_ENGINE_ID` | Your Google Custom Search Engine ID | Yes |

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
- **SearchResult**: Data class for search results
- **FastMCP Server**: HTTP server using the FastMCP framework

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `GOOGLE_API_KEY` environment variable is set
2. **Search Engine ID Missing**: Verify `GOOGLE_SEARCH_ENGINE_ID` is configured
3. **API Quota Exceeded**: Check your Google API quota limits
4. **Network Issues**: Ensure the server can reach Google's API endpoints

### Logs

The server logs important information including:
- Startup confirmation
- Search queries being executed
- API errors and exceptions

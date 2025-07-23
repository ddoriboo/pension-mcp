# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that integrates with Korea's Financial Supervisory Service (FSS) pension portal APIs. It provides access to 12 different pension-related APIs for collecting and analyzing Korean pension data, including pension savings, retirement pensions, and pension statistics.

## Core Commands

### Running the Server
```bash
python fss_pension_mcp_server/fss_pension_server.py
```

### Installing Dependencies
```bash
pip install -r fss_pension_mcp_server/requirements.txt
```

### Testing the Server
```bash
python fss_pension_mcp_server/test_server.py
```

### Demo Client
```bash
python fss_pension_mcp_server/demo_client.py
```

## Architecture

### Main Components

1. **FSSPensionServer Class** (`fss_pension_server.py:40-231`)
   - Core server class that handles all FSS API interactions
   - Manages async HTTP client for API calls
   - Handles XML/JSON response parsing with xmltodict

2. **MCP Server Integration** (`fss_pension_server.py:230-580`)
   - Uses `mcp.server` framework for protocol compliance
   - Implements 14 tools (12 basic APIs + 2 advanced analysis functions)
   - Handles tool registration and execution

3. **API Endpoints**
   - 12 FSS OpenAPI endpoints for different pension data types
   - Base URL: `https://apis.data.go.kr/1160100/service`
   - Requires service key from Korean government data portal

4. **Advanced Analysis Functions**
   - `analyze_pension_performance()`: Multi-API data analysis
   - `generate_pension_recommendation()`: Personalized pension advice

### Key Dependencies

- `mcp==1.0.0` - Model Context Protocol framework
- `httpx==0.27.0` - Async HTTP client for API calls
- `xmltodict>=0.13.0` - XML to dict conversion for API responses
- `pandas>=2.1.4` - Data manipulation for analysis functions

## API Configuration

### Service Key Setup
The server requires a valid service key from Korea's public data portal (data.go.kr):

```python
# In fss_pension_server.py:38
DEFAULT_SERVICE_KEY = "YOUR_SERVICE_KEY_HERE"
```

### API Categories
1. **Pension Savings APIs** (3 tools)
2. **Retirement Pension APIs** (4 tools) 
3. **Principal Guaranteed Product APIs** (2 tools)
4. **Pension Statistics APIs** (4 tools)
5. **Advanced Analysis Tools** (2 tools)

## Testing and Development

The project includes:
- `test_server.py`: Basic server functionality tests
- `demo_client.py`: Example usage demonstrations

All API calls are asynchronous and include proper error handling with logging to the console.

## Important Notes

- This is a defensive security tool for analyzing public pension data
- All APIs require valid Korean government service keys
- Server handles both XML and JSON responses automatically
- Uses Korean language for tool descriptions and error messages (as shown in the README)
- No package.json present - this is a pure Python project
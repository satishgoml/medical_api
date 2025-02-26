# Medical Workflow API

An AI-powered medical workflow API that processes medical queries and generates diagnoses using LLM agents.

## Overview

This FastAPI application implements a medical workflow system that can:
- Process natural language medical queries
- Analyze medical records (PDF format)
- Generate diagnostic reports
- Stream responses in real-time using Server-Sent Events (SSE)

The system uses LangGraph to orchestrate agent workflows and LangChain with OpenAI models for language processing.

## Prerequisites

- Python 3.12+
- OpenAI API key

## Installation

1. Clone the repository
   ```bash
   git clone [repository-url]
   cd medical_api
   ```

2. Install dependencies
   ```bash
   pip install -e .
   ```
   
3. Set up environment variables
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` file to add your OpenAI API key.

## Usage

### Starting the API server

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

- `POST /medical/diagnose` - Start a medical diagnosis workflow (POST method)
- `GET /medical/diagnose?input=your-query` - Start a diagnosis (GET method)
- `GET /files/list` - List all files in the data directory
- `GET /files/{filename}` - Download a specific file
- `POST /files/upload` - Upload a file to the data directory
- `GET /health` - Health check endpoint

## Project Structure

```
├── main.py               # FastAPI application entry point
├── pyproject.toml        # Project configuration
├── data/                 # Data storage (PDFs, etc.)
├── src/
│   ├── graph.py          # LangGraph workflow definitions
│   ├── schema.py         # Data models
│   ├── settings.py       # Project settings
│   ├── agents/           # Agent implementations
│   │   ├── config.py
│   │   ├── executor.py
│   │   ├── planner.py
│   │   ├── replanner.py
│   │   └── report_generator.py
│   └── tools/            # Agent tools
│       └── retriever.py  # Document retrieval tools
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OPENAI_API_KEY | Your OpenAI API key | - |
| DEFAULT_MODEL | Default OpenAI model to use | gpt-4o-mini |

## License

[License information]
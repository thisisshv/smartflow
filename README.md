# Smartflow

A natural-language-driven dynamic workflow engine using LangChain-style architecture, Mistral-7B, and FastAPI.

## Running Locally

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

```

## LLM Integration (Cohere)

This project uses [Cohere](https://cohere.com/) for natural language command processing. You must set your Cohere API key as an environment variable:

```
export CO_API_KEY=your_cohere_api_key_here
```

Or on Windows (PowerShell):
```
$env:CO_API_KEY="your_cohere_api_key_here"
```

The backend will use this key to access Cohere's free tier for LLM-powered features.

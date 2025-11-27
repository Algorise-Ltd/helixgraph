# Gemini API Setup Guide for HelixGraph

## Overview
This document provides a comprehensive guide to setting up and configuring the Google Gemini API for use with the HelixGraph RAG system. It covers obtaining an API key, configuring your environment, testing the connection, understanding usage limits, and troubleshooting common issues.

## Prerequisites
- A Google account.
- Access to Google AI Studio (https://aistudio.google.com/).
- Python 3.9+ installed.
- `uv` package manager installed

## Step 1: Get API Key

### Navigate to Google AI Studio
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.

### Create API Key
1. In the Google AI Studio interface, navigate to "Get API key" or "API access".
2. Create a new API key.

### Important Security Notes
- **NEVER** commit your API key directly to version control (e.g., Git).
- **NEVER** share your API key publicly.
- Treat your API key like a password.

## Step 2: Configure Environment

### Create .env File
Create a file named `.env` in the root directory of your `helixgraph` project (the same directory as `requirements.txt`). Add your Gemini API key to this file:

```
# Google Gemini API
GEMINI_API_KEY=your_actual_key_here

# Neo4j Connection (example, adjust as needed)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j
NEO4J_DATABASE=neo4j

# RAG Settings (optional - have defaults)
RAG_TEMPERATURE=0.3
RAG_MAX_TOKENS=2048
```
**Note:** The `.env.example` can be used as but file name must be changed.

### Install Dependencies
Ensure all required Python packages are installed. From your project root, run:
```bash
uv pip install -r requirements.txt
```
This will install `google-genai`, `jinja2`, `python-dotenv`, `neo4j`, and `pandas` (or their specified versions).

## Step 3: Test Connection

### Run Test Script
Execute the `rag/test_connections.py` script to verify connectivity to both Gemini and Neo4j.
```bash
python rag/test_connections.py
```

### Expected Output
A successful run should indicate that both Gemini and Neo4j connections are established, and the configuration is loaded correctly. For Gemini, you should see a response from the model.

## Free Tier Limits
Google Gemini API offers a free tier with certain usage limits.

### What This Means for HelixGraph
- For development and testing, `gemini-1.5-flash` is generally sufficient due to its higher rate limit.
- For production or high-volume scenarios, consider upgrading to a paid plan or optimizing API calls.
- Be mindful of your usage to avoid hitting rate limits, especially during intensive RAG operations.

## Configuration Options
The `rag/config.py` file centralizes various configuration parameters for the RAG system.

### Temperature
- **`temperature`**: Controls the randomness of the LLM's output (0.0 to 1.0).
    - `0.0`: More deterministic, factual, and consistent responses (ideal for RAG).
    - `1.0`: More creative, varied, and less predictable responses.
    - Default in HelixGraph is `0.3` for a balance of creativity and factual accuracy.

## Troubleshooting

### Error: "API key not valid"
- Double-check your `GEMINI_API_KEY` in the `.env` file for typos or extra spaces.
- Ensure your API key is active in Google AI Studio.

### Error: "Resource exhausted" or "429"
- You've likely hit a rate limit. Wait for some time before retrying.
- Consider optimizing your RAG queries or upgrading your API plan for higher limits.

### Error: "Model not found"
- Verify the `GEMINI_MODEL` specified in `rag/config.py` is correct and available.
- Ensure you have access to the specified model.

### Slow Responses
- This could be due to network latency or complex RAG queries.
- Optimize your Neo4j queries in `context_retriever.py` to fetch context more efficiently.
- Consider using a faster Gemini model if available and within your rate limits.

## Best Practices

### API Key Security
- Always use environment variables (via `.env` and `python-dotenv`) for API keys.
- Never hardcode API keys in your codebase.
- Regularly rotate your API keys.

### Rate Limiting
- Implement retry mechanisms with exponential backoff for API calls to handle rate limits gracefully.
- Monitor your API usage to stay within free tier limits or manage costs effectively.

### Cost Optimization
- Use the most cost-effective Gemini model suitable for your needs.
- Optimize context retrieval to send only necessary information to the LLM, reducing token usage.

## Usage Example
(This section will be populated with examples once the RAG system is built.)

## Resources
- Official Docs: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api
- Pricing: https://ai.google.dev/pricing
- Rate Limits: https://ai.google.dev/gemini-api/docs/models/generative-models#model-parameters

## Support
- Google AI Forum: https://discuss.ai.google.dev/
- Stack Overflow: Tag `google-gemini`
- HelixGraph Team: Ask in project Slack

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based LLM inference testing tool specifically designed for prompt injection (PI) attack simulation. The tool allows security researchers to test HTTP-based inference endpoints for prompt injection vulnerabilities using a comprehensive taxonomy of attack techniques.

**Key Purpose**: Authorized security testing of LLM applications for prompt injection vulnerabilities.

## Architecture

### Core Components

- **`llmtest/main.py`**: CLI application built with Typer that provides three main commands: `load`, `run`, and `export`
- **`llmtest/taxonomy.py`**: Loads attack taxonomy from markdown files organized in three categories (intents, techniques, evasions)
- **`llmtest/payloads.py`**: Generates attack payloads by combining taxonomy elements with LLM assistance (sequential)
- **`llmtest/async_payloads.py`**: **NEW** - Async/parallel payload generation with 10x performance improvement
- **`llmtest/execution.py`**: Executes HTTP requests with injected payloads
- **`llmtest/evaluation.py`**: Uses LLM to evaluate attack success/failure (sequential)
- **`llmtest/async_evaluation.py`**: **NEW** - Async/parallel response evaluation with batch processing
- **`llmtest/llm_client.py`**: Synchronous LLM API client
- **`llmtest/async_llm_client.py`**: **NEW** - Async LLM client with connection pooling and HTTP/2 support
- **`llmtest/model.py`**: Pydantic models defining data structures

### Performance Optimization (Async/Parallel Execution)

**Major Performance Improvement**: The tool now supports async/parallel execution for LLM API calls, providing approximately **10x faster** test runs compared to sequential execution.

#### Key Features:
- **Parallel Payload Generation**: All payloads are generated concurrently instead of sequentially
- **Batch Response Evaluation**: All responses are evaluated in parallel
- **Connection Pooling**: Reuses HTTP connections with HTTP/2 support for better performance
- **Rate Limiting**: Configurable concurrency control to respect API rate limits (default: 10 concurrent)
- **Backward Compatible**: Original sequential mode still available via `--sequential` flag

#### Performance Comparison:
```
Sequential Mode (original):
- 10 payloads × 60s timeout = ~600s generation
- 10 evaluations × 60s timeout = ~600s evaluation
- Total: ~20 minutes

Parallel Mode (new, default):
- 10 payloads in parallel = ~60s generation
- 10 evaluations in parallel = ~60s evaluation
- Total: ~2-3 minutes (10x faster!)
```

#### Usage:
```bash
# Default: Parallel async execution (10x faster)
poetry run llmtest run --intent "jailbreak" --goal "Bypass safety guardrails"

# Control concurrency (useful for API rate limits)
poetry run llmtest run --intent "jailbreak" --goal "Test" --max-concurrent 5

# Use sequential execution (original behavior)
poetry run llmtest run --intent "jailbreak" --goal "Test" --sequential
```

### Taxonomy Structure

The repository contains a comprehensive prompt injection taxonomy organized in three directories:

1. **`attack_intents/`**: What the attacker wants to achieve (e.g., jailbreak, data_exfiltration, system_prompt_leak)
2. **`attack_techniques/`**: How the attack is structured (e.g., role_playing, narrative_smuggling, meta_prompting)
3. **`attack_evasions/`**: How to bypass filters (e.g., base64, emoji, reverse, cipher)

Each category contains markdown files with attack descriptions and examples that are dynamically loaded by the tool.

### Data Flow

1. **Load**: Parse HTTP request template and specify injection point
2. **Generate**: Create payloads by combining taxonomy elements
3. **Execute**: Send requests with injected payloads
4. **Evaluate**: Use LLM to determine attack success
5. **Export**: Output results in table or JSON format

### State Management

- Uses local JSON file (`llmtest_db.json`) to persist request templates and test results
- No external database dependencies

## Development Commands

### Setup and Installation
```bash
# Install dependencies
poetry install

# Install development dependencies
poetry install --with dev

# Activate virtual environment
poetry shell
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_model.py

# Run with verbose output
poetry run pytest -v

# Run with debug output
poetry run pytest -s
```

### CLI Usage

#### Modern FUZZ-based Workflow (Recommended)
```bash
# Copy curl command from browser DevTools and add FUZZ where you want injection
poetry run llmtest load --from-curl 'curl -X POST https://api.openai.com/v1/chat/completions -H "Authorization: Bearer FUZZ" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"'

# Run attacks
poetry run llmtest run --intent "jailbreak" --goal "Bypass safety guardrails"
poetry run llmtest export --format table

# Multiple FUZZ locations supported
poetry run llmtest load --from-curl 'curl -X POST https://api.example.com/search -H "X-API-Key: FUZZ" -d "query=FUZZ&limit=10"'

# Works with any API format
poetry run llmtest load --from-curl 'curl -X POST https://graphql.example.com -H "Authorization: Bearer FUZZ" -d "{\"query\":\"{ user { name } }\"}"'
```

#### Legacy Manual Workflow (Backward Compatible)
```bash
# Manual injection point specification
poetry run llmtest load --url "https://api.example.com/chat" --data '{"messages":[{"role":"user","content":"test"}]}' --inject "body.messages[0].content"
poetry run llmtest run --intent "jailbreak" --goal "Bypass safety guardrails"
poetry run llmtest export --format table
```

#### Debug Mode
```bash
# See FUZZ detection and payload generation details
poetry run llmtest --debug load --from-curl 'curl -X POST https://api.com/chat -d "{\"message\":\"FUZZ\"}"'
poetry run llmtest --debug run --intent "system_prompt_leak" --goal "Extract system instructions"
```

### Development Server (for testing)
```bash
# Start test chatbot server
poetry run python -m uvicorn tests.test_chatbot_server:app --reload --port 8000
```

## Environment Requirements

- **Python**: ^3.9
- **Required Environment Variable**: `OPENROUTER_API_KEY` for LLM API access
- **Dependencies**: Uses Poetry for dependency management

## Key Implementation Details

### FUZZ-based Injection System (New)
- **FUZZ Keyword Detection**: Automatically detects `FUZZ` placeholders in curl commands
- **Universal API Support**: Works with any HTTP API (REST, GraphQL, SOAP, custom endpoints)
- **Multiple Injection Points**: Supports FUZZ in headers, URL parameters, JSON body, form data
- **Browser Integration**: Direct import from browser "Copy as cURL" commands
- **Flexible Placement**: FUZZ can be placed anywhere: `"Authorization: Bearer FUZZ"`, `"message": "FUZZ"`, `?q=FUZZ`

### Request Template System (Legacy + Enhanced)
- **Dual Mode Support**: Both FUZZ-based and traditional dot notation injection
- **Complex injection points**: Traditional dot notation (e.g., `body.messages[0].content`)
- **Enhanced parsing**: Robust curl parsing with `uncurl` library
- **Preserves structure**: Maintains original request format while enabling injection

### Payload Generation
- Dynamically combines taxonomy elements to create diverse attack vectors
- Uses LLM to generate contextual attack content
- Supports configurable payload limits per test run

### Evaluation System
- Uses external LLM to judge attack success with confidence scores
- Returns structured verdicts: SUCCESS, PARTIAL, or FAIL
- Provides response excerpts for manual verification

### Error Handling
- Graceful handling of malformed requests, API failures, and invalid taxonomy references
- Debug mode provides detailed logging and payload inspection
- Continues execution if individual tests fail

## Security Considerations

This tool is designed for **authorized security testing only**. It should be used for:
- Penetration testing with proper authorization
- Security research in controlled environments
- CTF competitions and educational contexts
- Defensive security assessments

The taxonomy contains real attack techniques that could be misused. Ensure proper authorization and ethical use.

## Testing the Codebase

### Unit Tests
- **`tests/test_model.py`**: Tests Pydantic model validation and serialization
- **`tests/test_parsing.py`**: Tests request parsing and injection point resolution
- **`tests/test_chatbot_server.py`**: Integration tests with mock API server

### Integration Testing
Use the included test server to verify end-to-end functionality:
```bash
# Terminal 1: Start test server
poetry run python -m uvicorn tests.test_chatbot_server:app --port 8000

# Terminal 2: Run integration test
poetry run llmtest load --url "http://localhost:8000/chat" --data '{"message":"test"}' --inject "body.message"
poetry run llmtest run --intent "jailbreak" --goal "Test attack"
```

## FUZZ Workflow Guide

### Basic FUZZ Usage
1. **Copy curl from browser**: Right-click in DevTools Network tab → "Copy as cURL"
2. **Add FUZZ markers**: Replace values you want to test with `FUZZ`
3. **Import and test**: Use `--from-curl` to load the modified command

### FUZZ Placement Examples

#### API Authentication Testing
```bash
# Test API key injection
llmtest load --from-curl 'curl -H "Authorization: Bearer FUZZ" https://api.example.com/data'

# Test multiple auth methods
llmtest load --from-curl 'curl -H "X-API-Key: FUZZ" -H "Authorization: Basic FUZZ" https://api.com'
```

#### JSON Body Injection
```bash
# OpenAI-style chat API
llmtest load --from-curl 'curl -X POST https://api.openai.com/v1/chat/completions -H "Authorization: Bearer sk-1234" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"FUZZ\"}]}"'

# Complex nested JSON
llmtest load --from-curl 'curl -X POST https://api.example.com -d "{\"data\":{\"query\":\"FUZZ\",\"filters\":{\"type\":\"admin\"}}}"'
```

#### URL Parameter Testing
```bash
# Search endpoint testing
llmtest load --from-curl 'curl "https://api.example.com/search?q=FUZZ&limit=10"'

# Multiple parameters
llmtest load --from-curl 'curl "https://api.example.com/users?id=FUZZ&role=FUZZ"'
```

#### Form Data Injection
```bash
# Login form testing
llmtest load --from-curl 'curl -X POST https://app.example.com/login -d "username=admin&password=FUZZ"'
```

#### GraphQL Testing
```bash
# GraphQL endpoint with auth
llmtest load --from-curl 'curl -X POST https://api.github.com/graphql -H "Authorization: token FUZZ" -d "{\"query\":\"{ viewer { login } }\"}"'
```

### Advanced FUZZ Features
- **Multiple FUZZ locations**: Place FUZZ in multiple places for comprehensive testing
- **Automatic detection**: Tool validates FUZZ presence and shows detected locations
- **Debug mode**: Use `--debug` to see exactly where FUZZ was detected
- **Universal compatibility**: Works with any HTTP-based API regardless of format

## File Organization Notes

- **Taxonomy files**: All `.md` files in `attack_*` directories are automatically loaded
- **Source code**: All application code is in `src/llmtest/`
- **Tests**: Integration and unit tests in `tests/`
- **Enhanced curl parsing**: `src/llmtest/curl_parser.py` handles FUZZ-based injection
- **Ecosystem documentation**: `ecosystem/README.MD` contains security assessment information for LLM DevOps tools
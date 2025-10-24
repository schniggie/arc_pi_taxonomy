# Slim LLM Inference Testing Tool

A lightweight LLM inference testing tool focused on prompt injection (PI) attack simulation with **universal API support**.

## Overview

This tool allows you to test **any HTTP-based API endpoint** for prompt injection vulnerabilities using a simple **FUZZ-based workflow**.

- **Universal Input**: Copy curl commands directly from browser DevTools, mark injection points with `FUZZ`
- **Any API Support**: Works with OpenAI, Anthropic, custom APIs, GraphQL, REST, and more
- **Smart Payload Generation**: Automatically generates attack payloads based on the [arc_pi_taxonomy](https://github.com/Arcanum-Sec/arc_pi_taxonomy)
- **AI Evaluation**: Uses state-of-the-art LLMs to judge attack success with confidence scores
- **Flexible Output**: Results in JSON and human-readable table formats

## Quick Start

### 1. Install and Setup
```bash
# Install dependencies
poetry install

# Set your OpenRouter API key for LLM evaluation
export OPENROUTER_API_KEY="your-api-key-here"
```

### 2. Modern FUZZ Workflow (Recommended)
```bash
# Step 1: Copy curl command from browser DevTools and add FUZZ where you want injection
llmtest load --from-curl 'curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer FUZZ" \
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"'

# Step 2: Run attack simulation
llmtest run --intent "jailbreak" --goal "Bypass safety guardrails"

# Step 3: View results
llmtest export --format table
```

## FUZZ Placement Examples

### API Authentication Testing
```bash
# Test API key in headers
llmtest load --from-curl 'curl -H "Authorization: Bearer FUZZ" https://api.example.com'

# Test API key in URL parameters
llmtest load --from-curl 'curl "https://api.example.com?api_key=FUZZ"'
```

### Message/Content Injection
```bash
# Chat API (OpenAI/Anthropic style)
llmtest load --from-curl 'curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"FUZZ\"}]}"'

# Custom chat endpoint
llmtest load --from-curl 'curl -X POST https://app.example.com/chat \
  -d "{\"message\":\"FUZZ\",\"user_id\":\"123\"}"'
```

### GraphQL Testing
```bash
# GitHub GraphQL API
llmtest load --from-curl 'curl -X POST https://api.github.com/graphql \
  -H "Authorization: token FUZZ" \
  -d "{\"query\":\"{ viewer { login } }\"}"'
```

### Form Data Testing
```bash
# Login forms
llmtest load --from-curl 'curl -X POST https://app.example.com/login \
  -d "username=admin&password=FUZZ"'
```

## Legacy Manual Workflow (Backward Compatible)
```bash
# Manual injection point specification
llmtest load --url "https://api.example.com/chat" \
  --data '{"messages":[{"role":"user","content":"test"}]}' \
  --inject "body.messages[0].content"

llmtest run --intent "jailbreak" --goal "Bypass safety guardrails"
llmtest export --format table
```

## Available Attack Intents

The tool includes a comprehensive taxonomy of prompt injection techniques:

- `jailbreak` - Bypass model safety measures
- `system_prompt_leak` - Extract system instructions
- `data_exfiltration` - Extract training data or sensitive info
- `denial_of_service` - Cause model failures or resource exhaustion
- `business_integrity` - Manipulate business logic (discounts, access, etc.)
- And many more in the `attack_intents/` directory

## Command Reference

### Load Commands
```bash
# FUZZ-based loading (modern)
llmtest load --from-curl 'curl_command_with_FUZZ_markers'

# Manual loading (legacy)
llmtest load --url URL --inject INJECTION_POINT [--data DATA] [--header HEADER]...

# Debug loading to see FUZZ detection
llmtest --debug load --from-curl 'curl_command'
```

### Run Commands
```bash
# Basic attack simulation
llmtest run --intent INTENT --goal "DESCRIPTION"

# Customize payload count and model
llmtest run --intent INTENT --goal "DESCRIPTION" --max-payloads 5 --model "gpt-4"

# Debug mode for detailed execution info
llmtest --debug run --intent INTENT --goal "DESCRIPTION"
```

### Export Commands
```bash
# Table format (human-readable)
llmtest export --format table

# JSON format for automation
llmtest export --format json --output results.json
```

## Architecture

- **Universal Curl Parser**: Robust parsing of real-world browser-exported curl commands
- **FUZZ Detection**: Automatically finds and validates `FUZZ` injection points in any part of HTTP requests
- **Smart Injection**: Supports headers, URL parameters, JSON bodies, form data, and raw text
- **Comprehensive Taxonomy**: 50+ attack techniques across multiple categories
- **AI-Powered Evaluation**: LLM-based success detection with confidence scoring
- **Flexible APIs**: Works with any HTTP endpoint regardless of format

## Security Notice

⚠️ **This tool is designed for authorized security testing only.**

Use only for:
- Penetration testing with proper authorization
- Security research in controlled environments
- CTF competitions and educational contexts
- Defensive security assessments

## Contributing

Contributions welcome! The taxonomy is modular - add new attack techniques by creating markdown files in the appropriate `attack_*` directories.

## License

See LICENSE.md for details.

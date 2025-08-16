# Slim LLM Inference Testing Tool

A lightweight LLM inference testing tool focused on prompt injection (PI) attack simulation.

## Overview

This tool allows you to test arbitrary HTTP-based inference endpoints for prompt injection vulnerabilities.

- **Input**: Raw HTTP requests, curl snippets.
- **Payload Generation**: Automatically generates attack payloads based on the [arc_pi_taxonomy](https://github.com/Arcanum-Sec/arc_pi_taxonomy).
- **Evaluation**: Uses a state-of-the-art LLM to judge the success of attack attempts.
- **Output**: Provides results in JSON and a human-readable summary.

## Usage

```bash
# Load a request from a curl command and specify the injection point
llmtest load --from-curl 'curl ...' --inject "body.messages[0].content"

# Run a test with a specific attack intent
llmtest run --intent "data_exfiltration" --goal "Extract system prompt"

# Export the results
llmtest export --format json --output results.json
```

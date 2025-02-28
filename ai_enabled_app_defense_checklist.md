# Defending AI Systems Checklist

## Defense Inspired by Attack Layers

### Layer One (Ecosystem): Securing AI infrastructure and cloud environments
- [ ] Keep open source software up to date with patches
- [ ] Ensure no security vulnerabilities are latent
- [ ] Enable two-factor Authentication for dashboards and GUIs
- [ ] Configure IAM roles for Cloud infrastructure
- [ ] Consider using a multi-LLM system with intermediary agents for data transformation
- [ ] Add comprehensive monitoring for unusual access/excess patterns and anomalous requests
- [ ] Secure logs and dashboards from javascript-based attacks, executing code, or following links

### Layer Two (Model): Protecting AI models from poisoning and adversarial attacks
- [ ] Choose a frontier model with strong guardrails
- [ ] Tune an OSS model to reduce bias, harm, and other undesirable outputs
- [ ] Add external defenses for prompt injection and jailbreaks
- [ ] Work with legal and PR to add a legal disclaimer for publicly available AI-enabled systems
- [ ] Implement regular security testing or apply a bug bounty

### Layer Three (Prompt): Preventing prompt injection and response manipulation
- [ ] Add system prompt based defenses
- [ ] Do not store API keys, secret routes, PII, or proprietary private information in system prompts
- [ ] Implement rate limiting to restrict submission frequency and complexity
- [ ] Manage context window size and information retention when possible

### Layer Four (Data): Safeguarding training and inference data from corruption
- [ ] Ensure data is scrubbed of private information before it enters the RAG system (including metadata)
- [ ] Ensure all enabled tools and agents that interact with APIs have scoped roles
- [ ] Configure tools and agents to access only the minimum data needed for operational goals
- [ ] Make tools and agents that interact with APIs read-only when possible

### Layer Five (Application): Hardening AI-integrated applications and APIs
- [ ] Ensure robust input validation and output encoding on all input sources:
  - [ ] Forms
  - [ ] API requests
  - [ ] File uploads
  - [ ] Input from integrations with other systems
- [ ] Prevent verbose logging to web sockets or debug consoles
- [ ] Implement sandboxing to isolate AI components from critical systems, especially multimodal systems (SSRF)

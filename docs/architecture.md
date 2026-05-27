
# Architecture Documentation

## System Overview

The AI Server Health Agent is a three-tier system designed for intelligent server fleet management:

1. **AI Layer** — Ollama running llama3 model locally on EC2
2. **Agent Layer** — LangChain ReAct agent orchestrating tools via Python
3. **Execution Layer** — Ansible managing remote servers over SSH

## Component Details

### Ollama (Local LLM)

- Runs on the agent EC2 instance as a systemd service
- Serves the llama3 model via REST API on port 11434
- Handles natural language understanding and intent classification
- No data leaves the EC2 instance — fully private and air-gapped capable

### LangChain ReAct Agent

- Uses the ReAct (Reasoning + Acting) pattern for decision making
- Classifies user intent into one of 6 available actions
- Selects and invokes the appropriate tool with correct parameters
- Provides natural language summaries of results

### Ansible Execution Engine

- Manages SSH connections to all target servers
- Executes playbooks for remediation, patching, and package installation
- Maintains server inventory in YAML format
- Supports ad-hoc commands across the entire fleet



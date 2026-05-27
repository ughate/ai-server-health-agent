
# 🤖 AI Server Health Agent

> An intelligent server health monitoring and management system powered by **LangChain**, **Ollama (Local LLM)**, **Python**, and **Ansible** — running entirely on AWS EC2.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-orange.svg)
![Ansible](https://img.shields.io/badge/Ansible-Automation-red.svg)
![AWS](https://img.shields.io/badge/AWS-EC2-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Infrastructure Setup](#-infrastructure-setup)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Available Tools](#-available-tools)
- [Security](#-security)
- [Chaos Testing](#-chaos-testing)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [License](#-license)

---

## 🎯 Overview

This project implements an **AI-powered server health monitoring agent** that:

- Accepts **natural language commands** (e.g., *"check server health"*, *"install nginx on all servers"*)
- Uses a **local LLM (Ollama with Llama3)** to understand user intent and decide actions
- Executes actions on remote servers via **Ansible** over SSH
- Requires **human approval** before any destructive action (human-in-the-loop)
- Runs entirely on **AWS EC2** with zero external API dependencies — fully private

---

## 🏗️ Architecture


┌─────────────────────────────────────────────────────────────────┐
│                      AGENT EC2 INSTANCE                         │
│                                                                 │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐   │
│  │    User      │──▶│   LangChain    │──▶│  Ollama (LLM)    │   │
│  │  (Terminal)  │  │  ReAct Agent   │  │  Model: llama3   │   │
│  └──────────────┘  └───────┬────────┘  └──────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│                   ┌──────────────────┐                          │
│                   │  Human Approval  │                          │
│                   │      Gate        │                          │
│                   └────────┬─────────┘                          │
│                            │                                    │
│                            ▼                                    │
│                   ┌──────────────────┐                          │
│                   │  Ansible Engine  │                          │
│                   └────────┬─────────┘                          │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             │ SSH (Port 22)
                ┌────────────┼────────────┐
                ▼                          ▼
┌────────────────────┐      ┌────────────────────┐
│  Target Server 1   │      │  Target Server 2   │
│  (EC2 Instance)    │      │  (EC2 Instance)    │
│  Amazon Linux 2023 │      │  Amazon Linux 2023 │
└────────────────────┘      └────────────────────┘



## ✨ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Interface** | Talk to the agent in plain English — no menus or commands to memorize |
| 🧠 **Local LLM (Ollama)** | No external API calls — your data never leaves your infrastructure |
| 🔍 **Health Monitoring** | Check uptime, memory usage, disk space, and service status |
| 📦 **Package Management** | Install any package across all servers with one sentence |
| 🔄 **Auto-Remediation** | Restart failed services automatically across the fleet |
| 🛡️ **Security Patching** | Apply security patches to all servers simultaneously |
| 🖥️ **Custom Commands** | Run any shell command across the entire server fleet |
| ✅ **Human-in-the-Loop** | Every destructive action requires explicit user confirmation |
| 🔗 **LangChain ReAct Agent** | Intelligent multi-step reasoning and tool selection |
| 📋 **Inventory Management** | View and manage all servers in your fleet |

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Ollama (llama3) | Natural language understanding & reasoning |
| **Agent Framework** | LangChain (ReAct Pattern) | Tool orchestration & decision making |
| **Automation** | Ansible | Remote server management via SSH |
| **Cloud** | AWS EC2 | Infrastructure hosting |
| **Language** | Python 3.9+ | Agent application logic |
| **OS** | Amazon Linux 2023 | Server operating system |

---

## 🏗️ Infrastructure Setup

### EC2 Instances Required

| Instance | Role | Type | RAM | Purpose |
|----------|------|------|-----|---------|
| Agent Server | Control Node | t3.medium | 8 GB | Runs Ollama + Python Agent + Ansible |
| Target Server 1 | Managed Node | t2.micro | 1 GB | Server being monitored and managed |
| Target Server 2 | Managed Node | t2.micro | 1 GB | Server being monitored and managed |

### Security Group Configuration

**Agent Server Security Group:**

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Your IP | SSH access to agent |
|[IP_ADDRESS]TCP | localhost | Ollama API (internal only) |

**Target Servers Security Group:**

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | Agent Server SG | SSH from agent for Ansible |

### IAM Role (Optional - for AWS API integration)

- `AmazonEC2ReadOnlyAccess`
- `ElasticLoadBalancingReadOnly`

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ughate/ai-server-health-agent.git
cd ai-server-health-agent
Step 2: Setup Ollama on Agent EC2
bash

chmod +x scripts/setup_ollama.sh
./scripts/setup_ollama.sh

Or manually:

bash

curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
ollama pull llama3

Verify installation:

bash

ollama list
curl http://localhost:11434/api/tags

Step 3: Install Python Dependencies
bash

pip install -r requirements.txt

Step 4: Setup SSH Keys for Ansible
bash

# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/agent_key -N ""

# Copy public key to each target server
ssh-copy-id -i ~/.ssh/agent_key.pub ec2-user@<TARGET_SERVER_1_PRIVATE_IP>
ssh-copy-id -i ~/.ssh/agent_key.pub ec2-user@<TARGET_SERVER_2_PRIVATE_IP>

Step 5: Configure Ansible Inventory
Edit ansible/inventory.yml with your target server private IPs:

yaml

all:
  children:
    webfarm:
      hosts:
        server1:
        [IP_ADDRESS]host: 172.31.X.X    # Replace with actual IP
        [IP_ADDRESS]user: ec2-user
        [IP_ADDRESS]ssh_private_key_file: ~/.ssh/agent_key
        server2:
        [IP_ADDRESS]host: 172.31.X.X    # Replace with actual IP
        [IP_ADDRESS]user: ec2-user
        [IP_ADDRESS]ssh_private_key_file: ~/.ssh/agent_key

Step 6: Test Ansible Connectivity
bash

ansible all -i ansible/inventory.yml -m ping

Expected output:

server1 | SUCCESS => { "ping": "pong" }
server2 | SUCCESS => { "ping": "pong" }
Step 7: Run the Agent
bash

python3 health_agent.py

💬 Usage
Starting the Agent
bash

$ python3 health_agent.py

============================================================
🤖 AI Server Health Agent (LangChain + Ollama)
============================================================
Talk to me in natural language! I can:
  • Check server health and status
  • Install packages on all servers
  • Patch/update all servers
  • Restart services and remediate issues
  • Run custom commands on servers
  • List managed servers

Type 'exit' or 'quit' to stop.
============================================================

Example Conversations
Checking Server Health:

🧑 You: check the health of my servers

⏳ Processing your request...

> Thought: User wants to check server health status
> Action: check_server_health
> Observation: Server Health Report...

🤖 Agent: Here's the health status of your servers:
   - Server1: Uptime 5 days, Memory 1.2GB free, Disk 45% used, nginx active
   - Server2: Uptime 3 days, Memory 0.8GB free, Disk 92% used (⚠️ HIGH), nginx inactive (⚠️ DOWN)
   Recommendation: Server2 needs attention - high disk usage and nginx is down.
Installing a Package:

🧑 You: install docker on all servers

⏳ Processing your request...

> Thought: User wants to install docker package
> Action: install_package
> Action Input: docker

⚠️  About to install 'docker' on ALL servers.
   Approve installation of 'docker'? (yes/no): yes

🤖 Agent: ✅ docker has been successfully installed on all servers.
Running Custom Commands:

🧑 You: run df -h on all servers

⏳ Processing your request...

⚠️  About to run command on ALL servers: df -h
   Approve execution? (yes/no): yes

🤖 Agent: ✅ Disk usage across all servers:
   server1: /dev/xvda1  100G   45G   55G  45%  /
   server2: /dev/xvda1  100G   92G    8G  92%  /
Patching Servers:

🧑 You: apply security patches to all servers

⏳ Processing your request...

⚠️  About to apply security patches to ALL servers.
   Approve patching? (yes/no): yes

🤖 Agent: ✅ Security patches applied successfully to all servers.
Restarting Services:

🧑 You: restart nginx on all servers

⏳ Processing your request...

⚠️  About to restart services on ALL servers.
   Target service: nginx
   Approve remediation? (yes/no): yes

🤖 Agent: ✅ nginx has been restarted successfully on all servers.
📁 Project Structure
ai-server-health-agent/
│
├── health_agent.py              # 🤖 Main AI agent (LangChain + Ollama)
│
├── ansible/
│   ├── inventory.yml            # 📋 Target server inventory
│   └── remediation.yml          # 🔧 Ansible remediation playbook
│
├── scripts/
│   ├── setup_ollama.sh          # ⚙️ Ollama installation script
│   ├── setup_agent.sh           # ⚙️ Full agent environment setup
│   └── chaos.sh                 # 💥 Chaos testing script
│
├── docs/
│   └── architecture.md          # 📖 Detailed architecture documentation
│
├── requirements.txt             # 📦 Python dependencies
├── .gitignore                   # 🚫 Git ignore rules
├── LICENSE                      # 📄 MIT License
└── README.md                    # 📖 This file
⚙️ How It Works
LangChain ReAct Agent Pattern
The agent uses the ReAct (Reasoning + Acting) pattern:

1. QUESTION  → User types natural language request
2. THOUGHT   → LLM reasons about what action to take
3. ACTION    → LLM selects the appropriate tool
4. INPUT     → LLM provides the correct input for the tool
5. APPROVAL  → Human confirms destructive actions
6. EXECUTION → Ansible runs the action on target servers
7. OBSERVE   → Agent receives results
8. ANSWER    → LLM summarizes results for the user
Example ReAct Trace
Question: "install nginx on all servers"
Thought: The user wants to install a software package called nginx on all servers.
         I should use the install_package tool.
Action: install_package
Action Input: nginx
[Human Approval: yes]
Observation: ✅ Package 'nginx' installation result: SUCCESS on server1, server2
Thought: I now know the final answer. The package was installed successfully.
Final Answer: ✅ nginx has been successfully installed on all managed servers
              (server1 and server2).
🔧 Available Tools
Table
#
Tool
Description
...
1
check_server_health
Checks uptime, memory, disk, services on all servers
...
2
install_package
Installs a software package on all servers
...
3
patch_servers
Applies security patches/updates to all servers
...
4
restart_services
Restarts a specific service or all critical services
...
5
run_command
Executes any shell command on all servers
...
6
list_servers
Lists all servers in the Ansible inventory
...

Natural Language Triggers
Table
Intent
Example Phrases
Health Check
"check health", "server status", "how are my servers", "monitor servers"
Install Package
"install nginx", "add docker", "setup git", "I need htop installed"
Patch Servers
"patch servers", "apply updates", "upgrade all", "security patches"
Restart Services
"restart nginx", "fix services", "remediate issues", "services are down"
Run Command
"run df -h", "execute uptime", "show me disk usage", "check logs"
List Servers
"list servers", "show inventory", "what servers do you manage"

🔒 Security
Security Measures Implemented
Table
Layer
Measure
Details
Access Control
Human-in-the-Loop
All write operations require explicit user approval
Authentication
SSH Key-Based
No password authentication — RSA 4096-bit keys only
Authorization
Least Privilege
Ansible uses minimal required sudo permissions
Data Privacy
Local LLM
Zero data sent to external APIs — fully air-gapped capable
Network
Localhost Binding
Ollama API accessib[IP_ADDRESS]0.0.1:11434
Secrets
External Config
No hardcoded credentials — keys stored in ~/.ssh/
Audit
Verbose Logging
All agent reasoning and actions logged to terminal

What the Agent CANNOT Do Without Approval
❌ Install any software
❌ Restart any service
❌ Apply patches or updates
❌ Run shell commands
❌ Modify any server configuration
What the Agent CAN Do Without Approval
✅ Check server health (read-only)
✅ List managed servers (read-only)
🧪 Chaos Testing
Test the agent's detection capabilities by simulating real server failures.

Run Chaos on Target Servers
bash

# SSH into a target server
ssh -i ~/.ssh/agent_key ec2-user@<TARGET_SERVER_IP>

# Run the chaos script
chmod +x scripts/chaos.sh
./scripts/chaos.sh

What Chaos Creates
Table
Failure
Simulation
Detection
Service Down
Stops nginx
Agent detects "inactive" status
Disk Full
Creates 85GB file at /root/
Agent detects 90%+ disk usage
Memory Pressure
Runs stress tool (256MB)
Agent detects low free memory

Test the Agent
After running chaos, go to your agent and ask:

🧑 You: check the health of my servers
The agent will detect:

⚠️ nginx service is DOWN
⚠️ Disk usage is critically HIGH (~90%)
⚠️ Memory usage is elevated
Then ask:

🧑 You: fix the issues on my servers
Undo Chaos
bash

sudo rm /root/disk_filler.img
killall stress
sudo systemctl start nginx

🚀 Future Enhancements
 AWS ELB Integration — Monitor load balancer health via Boto3
 Slack/Teams Alerts — Send notifications for critical issues
 Web Dashboard — Flask/FastAPI UI for monitoring
 Scheduled Checks — Cron-based automated health monitoring
 Multi-Cloud — Extend to Azure and GCP instances
 RBAC — Role-based access control for team environments
 Docker — Containerize the agent for easy deployment
 Prometheus/Grafana — Export metrics for visualization
 Auto-Scaling — Trigger scaling based on health metrics
 Email Reports — Daily/weekly health summary reports
🤝 Contributing
Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request
👤 Author
Umesh Ghate

GitHub: @ughate
Project: ai-server-health-agent
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

⭐ Show Your Support
If you found this project helpful or interesting, please give it a ⭐ on GitHub!

Built with ❤️ using LangChain, Ollama, Ansible, and AWS EC2



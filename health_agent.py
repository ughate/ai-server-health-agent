import subprocess
import json
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate

# ============================================================
# CONFIGURATION
# ============================================================
ANSIBLE_PLAYBOOK_PATH = "./ansible/remediation.yml"
INVENTORY_PATH = "./ansible/inventory.yml"
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL = "qwen2.5:3b"

# ============================================================
# INITIALIZE OLLAMA VIA LANGCHAIN
# ============================================================
llm = Ollama(
    model=MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
    timeout=120
)

# ============================================================
# CORE FUNCTIONS (Ansible & Server Operations)
# ============================================================

def run_ansible_playbook(extra_vars=None):
    """Execute Ansible playbook with optional variables"""
    cmd = ["ansible-playbook", ANSIBLE_PLAYBOOK_PATH, "-i", INVENTORY_PATH]
    if extra_vars:
        cmd.extend(["-e", json.dumps(extra_vars)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout + result.stderr
    except Exception as e:
        return f"Execution failed: {e}"


def check_server_health_fn(query: str = "") -> str:
    """Check health of all servers using Ansible setup module"""
    cmd = [
        "ansible", "all", "-i", INVENTORY_PATH,
        "-m", "shell", "-a",
        "uptime && free -m && df -h / && systemctl is-active nginx httpd docker 2>/dev/null || true",
        "-b"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        if output.strip():
            return f"Server Health Report:\n{output}"
        else:
            return "No response from servers. Check connectivity."
    except Exception as e:
        return f"Health check failed: {e}"


def install_package_fn(package_name: str) -> str:
    """Install a package on all servers"""
    # Handle key=value input format and sanitize
    if "=" in package_name:
        _, package_name = package_name.split("=", 1)
    package_name = package_name.strip().strip('"').strip("'").strip()
    
    if not package_name:
        return "Error: No package name provided. Please specify a package name."

    print(f"\n⚠️  About to install '{package_name}' on ALL servers.")
    approval = input(f"   Approve installation of '{package_name}'? (yes/no): ").strip().lower()

    if approval in ['yes', 'y']:
        output = run_ansible_playbook({"action": "install", "package": package_name})
        return f"✅ Package '{package_name}' installation result:\n{output}"
    else:
        return f"❌ Installation of '{package_name}' was cancelled by user."


def patch_servers_fn(query: str = "") -> str:
    """Apply security patches to all servers"""
    print("\n⚠️  About to apply security patches to ALL servers.")
    approval = input("   Approve patching? (yes/no): ").strip().lower()

    if approval in ['yes', 'y']:
        output = run_ansible_playbook({"action": "patch"})
        return f"✅ Patching result:\n{output}"
    else:
        return "❌ Patching was cancelled by user."


def restart_services_fn(service_name: str = "") -> str:
    """Restart services on all servers for remediation"""
    # Handle key=value input format (e.g., service_name=nginx)
    if "=" in service_name:
        _, service_name = service_name.split("=", 1)
    
    # Sanitize service name
    service_name = service_name.strip().strip('"').strip("'").strip()
    
    print(f"\n⚠️  About to restart services on ALL servers.")
    if service_name:
        print(f"   Target service: {service_name}")
    
    approval = input("   Approve remediation? (yes/no): ").strip().lower()

    if approval not in ['yes', 'y']:
        return "❌ Remediation was cancelled by user."

    if service_name:
        # Build Ansible command with proper quoting for systemd module
        cmd = [
            "ansible", "all", "-i", INVENTORY_PATH,
            "-m", "systemd",
            "-a", f"name={service_name} state=restarted",  # No extra quotes - systemd uses space-separated args
            "-b"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            output = result.stdout + result.stderr
            return f"✅ Service '{service_name}' restart result:\n{output}"
        except Exception as e:
            return f"Restart failed: {e}"
    else:
        output = run_ansible_playbook({"action": "remediate"})
        return f"✅ Remediation result:\n{output}"


def run_command_fn(command: str) -> str:
    """Run a custom shell command on all servers"""
    # Handle key=value input format and sanitize
    if "=" in command:
        _, command = command.split("=", 1)
    command = command.strip().strip('"').strip("'").strip()
    
    if not command:
        return "Error: No command provided."

    print(f"\n⚠️  About to run command on ALL servers: {command}")
    approval = input("   Approve execution? (yes/no): ").strip().lower()

    if approval in ['yes', 'y']:
        cmd = ["ansible", "all", "-i", INVENTORY_PATH, "-m", "shell", "-a", command, "-b"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return f"✅ Command output:\n{result.stdout + result.stderr}"
        except Exception as e:
            return f"Command execution failed: {e}"
    else:
        return "❌ Command execution was cancelled by user."


def list_inventory_fn(query: str = "") -> str:
    """List all servers in the Ansible inventory"""
    cmd = ["ansible-inventory", "-i", INVENTORY_PATH, "--list"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return f"Server Inventory:\n{result.stdout}"
    except Exception as e:
        return f"Failed to list inventory: {e}"

# ============================================================
# LANGCHAIN TOOLS DEFINITION
# ============================================================

tools = [
    Tool(
        name="check_server_health",
        func=check_server_health_fn,
        description="""Use this tool to check the health status of all servers.
        This checks uptime, memory usage, disk space, and service status.
        Input: any string (not used, can be empty)"""
    ),
    Tool(
        name="install_package",
        func=install_package_fn,
        description="""Use this tool to install a software package on all servers.
        Input: the exact package name to install (e.g., 'nginx', 'docker', 'git', 'htop').
        You can also use format: package_name=nginx"""
    ),
    Tool(
        name="patch_servers",
        func=patch_servers_fn,
        description="""Use this tool to apply security patches and updates to all servers.
        Use when user asks to patch, update, or upgrade servers.
        Input: any string (not used, can be empty)"""
    ),
    Tool(
        name="restart_services",
        func=restart_services_fn,
        description="""Use this tool to restart services on servers for remediation.
        Use when user asks to fix issues, restart services, or remediate problems.
        Input: service name to restart (e.g., 'nginx', 'docker') 
        OR use format: service_name=nginx"""
    ),
    Tool(
        name="run_command",
        func=run_command_fn,
        description="""Use this tool to run a custom shell command on all servers.
        Use when user asks to execute a specific command.
        Input: the shell command to execute (e.g., 'df -h', 'free -m', 'systemctl status nginx')
        OR use format: command=df -h"""
    ),
    Tool(
        name="list_servers",
        func=list_inventory_fn,
        description="""Use this tool to list all managed servers in the inventory.
        Use when user asks what servers are managed or wants to see the server list.
        Input: any string (not used, can be empty)"""
    ),
]

# ============================================================
# LANGCHAIN REACT AGENT PROMPT
# ============================================================

AGENT_PROMPT = PromptTemplate.from_template("""You are an AI Server Health Management Agent. You help manage and monitor servers using Ansible.

You have access to the following tools:

{tools}

Tool Names: {tool_names}

IMPORTANT RULES:
1. When the user asks to check health/status → use check_server_health
2. When the user asks to install something → use install_package with the package name
3. When the user asks to patch/update servers → use patch_servers
4. When the user asks to restart/fix/remediate → use restart_services
5. When the user asks to run a command → use run_command with the exact command
6. When the user asks about managed servers → use list_servers
7. Always provide a helpful summary after getting tool results
8. If the user's request is unclear, ask for clarification
9. **Input Format Support**: Tools accept both direct input (e.g., `nginx`) OR key=value format (e.g., `service_name=nginx`)

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

# ============================================================
# CREATE THE AGENT
# ============================================================

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=AGENT_PROMPT
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,          # Set to False to hide reasoning steps
    handle_parsing_errors=True,
    max_iterations=5,
    return_intermediate_steps=True
)

# ============================================================
# MAIN INTERACTIVE LOOP
# ============================================================

def main():
    print("=" * 60)
    print("🤖 AI Server Health Agent (LangChain + Ollama)")
    print("=" * 60)
    print("Talk to me in natural language! I can:")
    print("  • Check server health and status")
    print("  • Install packages on all servers")
    print("  • Patch/update all servers")
    print("  • Restart services and remediate issues")
    print("  • Run custom commands on servers")
    print("  • List managed servers")
    print("")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n🧑 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                print("\n👋 Goodbye, UMESH! Agent shutting down.")
                break

            print("\n⏳ Processing your request...\n")

            # Run the LangChain agent
            response = agent_executor.invoke({"input": user_input})

            # Print the final answer
            print(f"\n🤖 Agent: {response['output']}")

        except KeyboardInterrupt:
            print("\n\n👋 Agent interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try rephrasing your request.")


if __name__ == "__main__":
    main()
